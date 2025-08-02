"""
Compat. layer between `pytest_autoprofile._doctest` and `xdoctest`.
"""
import doctest
import functools
import inspect
import re
import types
from os import PathLike
from pathlib import Path

import pytest
from line_profiler.autoprofile.util_static import modpath_to_modname

from . import _doctest
from ._typing import (
    TYPE_CHECKING,
    Dict, Set, Tuple, Generator,
    Callable, ParamSpec,
    Any, Annotated, Type, TypeVar, Union,
    overload,
    ChainedIdentifier, ImportPath,
)
from .importers import AutoProfStash

try:
    import xdoctest  # noqa: F401
except ImportError:
    HAS_XDOCTEST = False
else:
    HAS_XDOCTEST = True

if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811

if TYPE_CHECKING or HAS_XDOCTEST:
    from xdoctest.doctest_example import DocTest
else:
    DocTest = object


__all__ = ('get_doctest_class',)

Exc = TypeVar('Exc', bound=BaseException)
PS = ParamSpec('PS')

THIS_PACKAGE = (lambda: None).__module__.rpartition('.')[0]


def wrap_example_generator_func(
    func: Callable[PS, Generator[DocTest, None, None]],
) -> Callable[PS, Generator[DocTest, None, None]]:
    """
    Create a wrapper around a function used in `xdoctest` to yield
    `xdoctest.doctest_example.DocTest` instances, e.g.
    `xdoctest.core.parse_docstr_examples()`, which attaches extra
    information required for resolving docstring locations.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Generator[DocTest, None, None]:
        ba = sig.bind(*args, **kwargs)
        ba.apply_defaults()
        lineno = ba.arguments['lineno']
        if TYPE_CHECKING:
            assert isinstance(lineno, int)
        for example in func(*args, **kwargs):
            if TYPE_CHECKING:
                assert isinstance(example, _DocTestMixin)
            example._extra_offset = example.lineno - lineno
            yield example

    sig = inspect.signature(func)
    if 'lineno' not in sig.parameters:
        return func
    return wrapper


def wrap_xdoctest_core(
    core: types.ModuleType, mp: pytest.MonkeyPatch,
) -> types.ModuleType:
    """
    Create a wrapper around `xdoctest.core` so that its
    `parse_*_examples()` functions attaches additional information to
    the created `DocTest` objects.

    Return
    ------
    `core`

    Side effects
    ------------
    The `parse_*_examples()` generator functions in its namespace are
    wrapped by `wrap_example_generator_func()`.
    """
    set_attr = functools.partial(mp.setattr, core)
    for name, value in inspect.getmembers(core):
        if not (name.startswith('parse_') and name.endswith('_examples')):
            continue
        if not inspect.isgeneratorfunction(value):
            continue
        set_attr(name, wrap_example_generator_func(value))
    return core


class _DocTestMixin(_doctest._RunnerMixin):
    """
    Mixin class to work with `xdoctest.doctest_example.DocTest` which
    handles doctest profiling.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._last_compiled = None
        self._extra_offset = 0

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        # Note: it would've been cleaner to just modify the traceback
        # and reraise the exception with it in e.g.
        # `.exec_doctest_example()`;
        # but since we can't instantiate frame objects in Python, we
        # have to resort to mocking `sys.exc_info()`

        # Retrieve the basic wrapper around
        # `xdoctest.doctest_example.DocTest.run()`, which handles the
        # compilation/execution of code with instrumentation
        base_run = type(self)._base_run  # type: ignore[attr-defined]

        # Create a copy of the `sys` imported by
        # `xdoctest.doctest_example`...
        xdoctest_module = ImportPath(base_run.__module__).import_target()
        sys_ = self._clone_module(xdoctest_module.sys)
        # ... and override its `exc_info()`
        sys_.exc_info = functools.partial(  # type: ignore[attr-defined]
            self._get_exc_info, sys_.exc_info,
        )

        # Now we run the wrapper;
        # and if there's any exception, the cleanup code will see the
        # repaired traceback
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(xdoctest_module, 'sys', sys_, raising=False)
            return base_run(self, *args, **kwargs)

    @functools.wraps(_doctest._RunnerMixin.compile_doctest_example)
    def compile_doctest_example(self, *args, **kwargs):
        """
        Notes
        -----
        `xdoctest` operates on code objects in the traceback to
        streamline it;
        so keep a reference of how the code object is supposed to look
        and restore it in tracebacks when necessary.
        """
        code = super().compile_doctest_example(*args, **kwargs)
        self._last_compiled = compile(*args, **kwargs), code
        return code

    def _reconstruct_mock_traceback(
        self,
        tb: types.TracebackType,
        drop_package_frames: bool = True,
    ) -> types.SimpleNamespace:
        """
        When code execution fails, repair the traceback and its frames
        in a way that `xdoctest` understands.

        Notes
        -----
        Since traceback and frame objects are highly rigid, and it is
        not allowed to either (1) create frame objects in Python code or
        (2) create traceback objects with a non-frame object in the
        `.tb_frame` slot:
        - The returned object is a daisy chain of namespace objects
          which mocks the traceback APIs.
        - The frames in the repaired object can be namespaces which
          mocks the frame APIs.
        """
        def copy_frame(frame: types.FrameType) -> types.SimpleNamespace:
            attrs = {
                name: value for name, value in inspect.getmembers(frame)
                if name.startswith('f_')
            }
            attrs['clear'] = frame.clear
            del frame  # Help the GC out
            return types.SimpleNamespace(**attrs)

        def replace_tb(
            tb: types.TracebackType, /, **tb_attrs,
        ) -> types.SimpleNamespace:
            return types.SimpleNamespace(**{
                attr: tb_attrs.get(attr, getattr(tb, attr))
                for attr in ['tb_frame', 'tb_lineno', 'tb_lasti', 'tb_next']
            })

        @overload
        def repair_tb(tb: types.TracebackType) -> types.SimpleNamespace:
            ...

        @overload
        def repair_tb(tb: None) -> None:
            ...

        def repair_tb(
            tb: Union[types.TracebackType, None],
        ) -> Union[types.SimpleNamespace, None]:
            if tb is None:
                return None
            result = replace_tb(tb)
            fname = tb.tb_frame.f_code.co_filename
            if fname == code_after.co_filename:
                frame = copy_frame(tb.tb_frame)
                frame.f_code = code_before
                frame.f_lineno += lineno_offset
                result.tb_frame = frame
                result.tb_lineno += lineno_offset
            elif fname in drop_filenames:
                # Skip the stack frame
                return repair_tb(tb.tb_next)
            result.tb_next = repair_tb(tb.tb_next)
            return result

        assert self._last_compiled
        code_before, code_after = self._last_compiled
        if drop_package_frames:
            drop_filenames: Set[str] = {__file__, _doctest.__file__}
        else:
            drop_filenames = set()
        lineno_offset = code_before.co_firstlineno - code_after.co_firstlineno
        return repair_tb(tb)

    def _get_exc_info(
        self,
        impl: Callable[
            [],
            Union[
                Tuple[None, None, None],
                Tuple[Type[Exc], Exc, types.TracebackType],
            ]
        ],
    ) -> Union[
        Tuple[None, None, None], Tuple[Type[Exc], Exc, types.SimpleNamespace],
    ]:
        """
        Mock for `sys.exc_info()` which repairs the traceback object.
        """
        Exc, xc, tb = impl()
        if tb:
            mock_tb = self._reconstruct_mock_traceback(tb)
        else:
            mock_tb = None
        return Exc, xc, mock_tb  # type: ignore[return-value]

    @classmethod
    def install(cls) -> None:
        """
        Beside installing the `xdoctest.doctest_example.DocTest`
        subclass itself, also monkey-patch the `xdoctest.core` generator
        functions to attach extra info to the yielded instances.
        """
        super().install()
        xdoctest_core = ImportPath('xdoctest.core').import_target()
        wrap_xdoctest_core(xdoctest_core, cls._installer)

    @functools.cached_property
    def test(self) -> doctest.DocTest:
        # `doctest.DocTest.lineno` is zero-based;
        # also compensate for how `.lineno` is that of the snippet, not
        # of the docstring itself
        lineno = self.lineno - self._extra_offset - 1
        # `.modpath` can be `None` or an `os.PathLike`
        if self.modpath is None:
            filename = None
        else:
            try:
                file_path = Path(self.modpath)
                if not file_path.is_file():
                    raise FileNotFoundError
                filename = str(file_path)
            except Exception:
                filename = None
        if filename is None:
            module_name = None
        else:
            module_name = modpath_to_modname(filename, hide_init=True)
        if module_name is None:
            name = '???.{self.callname}'
        elif self.callname == '__doc__':  # Module docstring
            name = module_name
        else:
            name = f'{module_name}.{self.callname or "???"}'
        # Create a mock `doctest.DocTest` object
        return doctest.DocTest(
            # These we don't care about...
            examples=[], globs={}, docstring='',
            # ... while these are actually used in the code
            lineno=lineno, filename=filename, name=name,
        )

    @property
    def _current_example(self) -> doctest.Example:
        module = self.ExpectedBaseClass.__module__
        current_part = self._seek_module_frame(module).f_locals['part']
        lineno: int = current_part.line_offset + self._extra_offset
        # Note: we basically just need the line number
        return doctest.Example(source='pass', want='', lineno=lineno)

    # Class attributes

    ExpectedBaseClass = DocTest
    filename_pattern = re.compile(r'^<doctest:.*:[0-9]+(?::[a-z_]+)?>$')

    # These attributes are to be inherited from
    # `xdoctest.doctest_example.DocTest`

    lineno: int
    modpath: Union[str, PathLike]
    callname: Annotated[str, ChainedIdentifier]

    # These attributes are added to help with locating the docstring
    # and formatting tracebacks
    _last_compiled: Union[Tuple[types.CodeType, types.CodeType], None]
    _extra_offset: int


def get_doctest_class(
    config: pytest.Config, stash: AutoProfStash,
) -> Type[_doctest.DoctestHandler]:
    """
    Factory function for building the appropriate
    `xdoctest.doctest_example.DocTest` subclass.
    """
    dest: Annotated[str, ChainedIdentifier] = (
        '{0.__module__}.{0.__qualname__}'.format(DocTest)
    )
    base_run = DocTest.run  # type: ignore[attr-defined]
    namespace = {
        # Since `DocTest` already has a `.config`, just directly
        # override `.pytest_config`
        'pytest_config': config,
        'stash': stash,
        '_base_run': _doctest.get_run_wrapper(base_run),
        '_installer': pytest.MonkeyPatch(),
        'installation_destinations': dest,
    }
    name = 'Profiling' + DocTest.__name__
    return type(name, (_DocTestMixin, DocTest), namespace)
