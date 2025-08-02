"""
Implement import-time AST rewrites like `pytest` does for assertions.
"""
import abc
import ast
import dataclasses
import doctest
import functools
import importlib.abc
import importlib.util
import inspect
import operator
import os
import pathlib
import pkgutil
import shutil
import sys
import tempfile
import textwrap
import types
try:
    import _pickle as pickle
except ImportError:
    import pickle  # type: ignore[no-redef] # noqa: F811
from pickle import HIGHEST_PROTOCOL  # Not available on `_pickle`

from _pytest.assertion import rewrite, DummyRewriteHook
from _pytest.pathlib import fnmatch_ex
from line_profiler.autoprofile.run_module import AstTreeModuleProfiler
import pytest

from ._json import JSONHelper
from ._typing import (
    TYPE_CHECKING,
    Dict, FrozenSet, List, Set, Tuple,
    Collection, Mapping, MutableSequence, Sequence,
    Callable, ParamSpec,
    Type, TypeVar, ClassVar, Generic,
    Annotated, Any, Self,
    Literal, Union, Optional,
    overload,
    ChainedIdentifier, Identifier, ImportPath,
    is_identifier,
)
from ._warnings import warn, OptionParsingWarning
from .option_hooks import _get_cache_dir, resolve_hooked_option
from .profiler import LineProfiler
from .rewriting import StrictModuleRewriter
from .utils import get_config, LazyImporter


if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811
    # `mypy` doesn't alias `importlib.abc.MetaPathFinder` to
    # `_typeshed.importlib.MetaPathFinderProtocol`;
    # do it manually here
    from _typeshed.importlib import MetaPathFinderProtocol as MetaPathFinder
    from ._doctest import DoctestHandler as _DoctestHandler
else:
    from importlib.abc import (  # type: ignore[no-redef] # noqa: F811
        MetaPathFinder,
    )


__all__ = (
    'rewrite_tests',
    'ProfileModulesImporter',
    'ProfileTestsImporter',
    'AutoProfStash',
    'AUTOPROF_STASH_KEY',
)

_DEFAULT_TEST_PATH_PATTERNS = 'test_*.py', '*_test.py'
_JSON_STASH = False

T = TypeVar('T')
PS = ParamSpec('PS')
_Importer = TypeVar('_Importer', 'AutoProfImporter', '_SubprocImporter')

# We have a forward reference to `~._doctest.DoctestHandler`;
# lazy-import it

__dir__, __getattr__ = LazyImporter.install(
    globals(), _DoctestHandler='_doctest::DoctestHandler',
)

# Note: `@profile` is slipped into the local namespace by
# `AutoProfImporter.exec_module()`, but that may not be enough for
# applications directly using the code objects (e.g. `runpy`). Hence,
# we provide an out by making the active profiler importable from the
# top level (see `~.profiler.LineProfiler.install()`)


@functools.lru_cache(maxsize=1)
def _get_conditional_import_node(
    source: ImportPath = ImportPath(
        (lambda: None).__module__.partition('.')[0], 'profile',
    ),
    dest: Annotated[str, Identifier] = 'profile',
) -> ast.If:
    assert source.object
    assert is_identifier(dest)
    dummy_name = '_dummy_module_' + dest
    code = f"""
    if {dest!r} not in globals():
        import {source.module} as {dummy_name}
        try:
            {dest} = {dummy_name}.{source.object}
        finally:
            del {dummy_name}
    """
    node, = ast.parse(textwrap.dedent(code).strip('\n')).body
    if TYPE_CHECKING:
        assert isinstance(node, ast.If)
    return node


# Note: since `_pytest.assertion` is used by `pytest.Config` very early
# at import time, by the time we get here the assertion-rewriting hooks
# will already have been run.
# So, while rewriting the modules we have to take care not to undo that


@overload
def rewrite_tests(
    spec: importlib.machinery.ModuleSpec,
    config: None = None,
    *,
    prof_targets: Collection[Union[ImportPath, str, pathlib.PurePath]],
    prof_imports: bool,
    rewrite_asserts: bool,
) -> types.CodeType:
    ...


@overload
def rewrite_tests(
    spec: importlib.machinery.ModuleSpec,
    config: pytest.Config,
    *,
    prof_targets: Optional[Collection[
        Union[ImportPath, str, pathlib.PurePath]
    ]] = None,
    prof_imports: Optional[bool] = None,
    rewrite_asserts: Optional[bool] = None,
) -> types.CodeType:
    ...


def rewrite_tests(
    spec: importlib.machinery.ModuleSpec,
    config: Optional[pytest.Config] = None,
    *,
    prof_targets: Optional[Collection[
        Union[ImportPath, str, pathlib.PurePath]
    ]] = None,
    prof_imports: Optional[bool] = None,
    rewrite_asserts: Optional[bool] = None,
) -> types.CodeType:
    """
    Rewrite the test module at `spec` and return the compiled code
    object.
    """
    if prof_targets is None:
        assert config is not None
        prof_targets = AutoProfImporter.get_autoprof_mod(config)
    if prof_imports is None:
        assert config is not None
        prof_imports = AutoProfImporter.get_autoprof_imports(config)
    if rewrite_asserts is None:
        assert config is not None
        rewrite_asserts = AutoProfImporter._get_rewrite_asserts(config)
    prof_mod: List[str] = [
        (
            str(ipath)
            if not isinstance(ipath, ImportPath) else
            '{0[0]}.{0[1]}'.format(ipath)
            if ipath.object else
            ipath.module
        )
        for ipath in prof_targets
    ]
    tree = AstTreeModuleProfiler(
        spec.origin, prof_mod, prof_imports,  # type: ignore[arg-type]
    ).profile()
    # Note: if we don't have a `config`, we don't know how to rewrite
    # assertions either
    if config is None:
        return _compile_module(tree, spec, None, rewrite_asserts=False)
    return _compile_module(tree, spec, config, rewrite_asserts=rewrite_asserts)


@overload
def _compile_module(
    module: ast.Module,
    spec: importlib.machinery.ModuleSpec,
    config: None = None,
    *,
    rewrite_asserts: Literal[False] = False,
    insert_conditional_import: bool = True,
) -> types.CodeType:
    ...


@overload
def _compile_module(
    module: ast.Module,
    spec: importlib.machinery.ModuleSpec,
    config: pytest.Config,
    *,
    rewrite_asserts: bool = False,
    insert_conditional_import: bool = True,
) -> types.CodeType:
    ...


def _compile_module(
    module: ast.Module,
    spec: importlib.machinery.ModuleSpec,
    config: Optional[pytest.Config] = None,
    *,
    rewrite_asserts: bool = False,
    insert_conditional_import: bool = True,
) -> types.CodeType:
    """
    Compile the `module`, optionally rewriting its assertions.

    Side effects
    ------------
    `module` may be altered.
    """
    fpath = pathlib.Path(spec.origin)  # type: ignore[arg-type]
    fname = str(fpath)
    # Re-apply the assertion rewrites where appropriate
    if rewrite_asserts:
        assert config is not None
        rewrite.rewrite_asserts(module, fpath.read_bytes(), fname, config)
    # Slip in a helper node so as to ensure the availability of
    # `@profile`
    if insert_conditional_import:
        module.body.insert(0, _get_conditional_import_node())
    return compile(module, fname, 'exec')


class _FallThruProperty(property, Generic[T]):
    name: Union[Annotated[str, Identifier], None]

    def __init__(
        self,
        fget: Optional[Callable[[Any], T]] = None,
        fset: Optional[Callable[[Any, T], None]] = None,
        fdel: Optional[Callable[[Any], None]] = None,
        doc: Optional[str] = None,
    ) -> None:
        super().__init__(
            self.default_fget if fget is None else fget,
            self.default_fset if fset is None else fset,
            self.default_fdel if fdel is None else fdel,
            doc,
        )
        vars(self)['_init_args'] = {
            'fget': fget, 'fset': fset, 'fdel': fdel, 'doc': doc,
        }
        self.name = None

    def replace(self, **attrs) -> Self:
        args = vars(self)['_init_args'].copy()
        for key in args:
            if key in attrs:
                args[key] = attrs[key]
        new_instance = type(self)(**args)
        new_instance.name = attrs.get('name', self.name)
        return new_instance

    __replace__ = replace

    def __set_name__(
        self, owner: type, name: Annotated[str, Identifier],
    ) -> None:
        new_instance = type(self)(**vars(self)['_init_args'])
        new_instance.name = name
        setattr(owner, name, new_instance)
        try:
            # Note: `property` does have a `.__set_name__()`, but it
            # isn't in `typeshed`
            super_impl = (
                super(_FallThruProperty, new_instance)
                .__set_name__  # type: ignore[misc]
            )
        except AttributeError:
            pass
        else:
            super_impl(owner, name)

    def getter(self, fget: Optional[Callable[[Any], T]] = None) -> Self:
        return self.replace(fget=fget)

    def setter(self, fset: Optional[Callable[[Any, T], None]] = None) -> Self:
        return self.replace(fset=fset)

    def deleter(self, fdel: Optional[Callable[[Any], None]] = None) -> Self:
        return self.replace(fdel=fdel)

    def default_fget(self, instance):
        try:
            return vars(instance)[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def default_fset(self, instance, value):
        vars(instance)[self.name] = value

    def default_fdel(self, instance):
        try:
            del vars(instance)[self.name]
        except KeyError:
            raise AttributeError(self.name) from None


_issue_warning = functools.partial(
    warn,
    skip_modules=('functools', 'line_profiler', 'importlib', 'pluggy'),
    stacklevel=2,
)


class _AutoProfImporterBase(
    importlib.abc.MetaPathFinder, importlib.abc.SourceLoader,
):
    _profiled_code_objs: Dict[
        int, types.CodeType  # Inode -> code
    ]
    imported_names: Set[Annotated[str, ChainedIdentifier]]
    _cached_properties: ClassVar[FrozenSet[Annotated[str, Identifier]]]
    _serializable_attrs: ClassVar[FrozenSet[Annotated[str, Identifier]]] = (
        frozenset({
            'always_autoprof', 'recursive_autoprof', 'postimport_autoprof',
            'autoprof_mod', 'autoprof_imports', 'autoprof_tests',
        })
    )
    _issued_warnings: ClassVar[  # Config id, warning class & message
        Set[Tuple[int, Type[Warning], str]]
    ] = set()

    def __init__(self, *_, **__) -> None:
        self._profiled_code_objs = {}
        self.imported_names = set()
        super().__init__()

    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        cached_property = functools.cached_property
        cls._cached_properties = frozenset(
            name for name, member in inspect.getmembers(cls)
            if isinstance(member, cached_property)
        )
        serializable: FrozenSet[Annotated[str, Identifier]] = frozenset()
        cls._serializable_attrs = serializable.union(*(
            getattr(base, '_serializable_attrs', frozenset())
            for base in cls.mro()
        ))

    def __repr__(self) -> str:
        attrs = ', '.join(
            f'.{attr}={value!r}'
            for attr, value in sorted(self._get_serializable_attrs().items())
            if not attr.startswith('_') if value
        )
        return '<{} object{} at {:#x}>'.format(
            type(self).__qualname__, f' ({attrs})' if attrs else '', id(self),
        )

    # Finder/Loader methods

    def find_spec(
        self,
        name: Annotated[str, ChainedIdentifier],
        path: Optional[Sequence[Union[str, bytes]]] = None,
        *_,
        use_meta_path: bool = True,
        **__
    ) -> Union[importlib.machinery.ModuleSpec, None]:
        spec = self.find_spec_by_path(name, path, use_meta_path=use_meta_path)
        inode = self.module_spec_to_inode(spec)
        if inode is None:
            return None
        assert spec is not None
        if inode in self._profiled_code_objs or self.rewrite_needed(spec):
            spec.loader = self
            return spec
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        namespace = module.__dict__
        namespace['profile'] = profiler = self._profiler
        spec: Union[importlib.machinery.ModuleSpec, None] = module.__spec__
        if spec is None:
            raise RuntimeError(f'module = {module!r}: empty `.__spec__`')
        count = profiler.object_count
        exec(self.get_code(spec), namespace, namespace)
        profiled = profiler.object_count > count
        if profiled:
            self._register_usage(spec.name)

    def _register_usage(
        self, module: Annotated[str, ChainedIdentifier],
    ) -> None:
        if self not in self._importers:
            if TYPE_CHECKING:
                assert isinstance(self, (AutoProfImporter, _SubprocImporter))
            self._importers.append(self)
        self.imported_names.add(module)

    def invalidate_caches(self) -> None:
        self._profiled_code_objs.clear()
        for name in self.imported_names:
            sys.modules.pop(name, None)
        self.imported_names.clear()
        remove_cache = self.__dict__.pop
        for prop in self._cached_properties:
            remove_cache(prop, None)
        super().invalidate_caches()

    @staticmethod
    def get_data(path: Union[str, pathlib.PurePath]) -> bytes:
        return pathlib.Path(path).read_bytes()

    @classmethod
    def get_filename(
        cls, name: Annotated[str, ChainedIdentifier], *,
        use_meta_path: bool = True,
    ) -> str:
        spec = cls.find_spec_by_path(name, use_meta_path=use_meta_path)
        if spec is None:
            raise ImportError(name)
        origin = spec.origin
        if origin is None:
            raise ImportError(name)
        if origin == 'frozen' or not os.path.exists(origin):
            raise ImportError(name)
        return origin

    if TYPE_CHECKING:
        def source_to_code(  # type: ignore[override]
            self, *args, **kwargs
        ) -> types.CodeType:
            """
            Notes
            -----
            `mypy` reports that `SourceLoader.source_to_code()` (an
            instance method) clashes with
            `InspectLoader.source_to_code()` (a static method);
            since:
            - The method is functionally only used in the superclasses
              as an instance method, and
            - `InspectLoader` is merely included as a base class because
              `SourceLoader` inherits from it,
            just explicitly override the method here so that we can
            catch and suppress the `mypy` error.
            """
            return super().source_to_code(*args, **kwargs)

    def get_code(
        self,
        name_or_spec: Union[
            Annotated[str, ChainedIdentifier], importlib.machinery.ModuleSpec,
        ],
        *,
        use_meta_path: bool = True,
    ) -> types.CodeType:
        if isinstance(name_or_spec, str):
            spec = self.find_spec_by_path(
                name_or_spec, use_meta_path=use_meta_path,
            )
            if spec is None:
                raise ImportError(name_or_spec)
        else:
            spec = name_or_spec
        try:
            inode = self.module_spec_to_inode(spec)
            assert inode is not None
            try:
                return self._profiled_code_objs[inode]
            except KeyError:
                self._profiled_code_objs[inode] = code = self.write_code(spec)
                return code
        except Exception as e:
            raise ImportError(name_or_spec) from e

    def install(
        self,
        *,
        index: int = 0,
        path: Optional[MutableSequence[MetaPathFinder]] = None,
    ) -> None:
        """
        Install the importer into `path` (default: `sys.meta_path`) at
        the specified `index`;
        if it's already there, it's first removed and re-inserted at
        the requested position.
        """
        if path is None:
            path = sys.meta_path
        self.uninstall(path=path, invalidate_caches=False)
        path.insert(index, self)

    def uninstall(
        self,
        *,
        invalidate_caches: bool = True,
        path: Optional[MutableSequence[MetaPathFinder]] = None,
    ) -> None:
        """
        Uninstall the importer from `path` (default: `sys.meta_path`),
        and optionally also invalidate the caches.
        """
        if path is None:
            path = sys.meta_path
        try:
            path.remove(self)
        except ValueError:  # Not in list
            return
        if invalidate_caches:
            self.invalidate_caches()

    # Selection/Modification methods

    @abc.abstractmethod
    def rewrite_needed(self, spec: importlib.machinery.ModuleSpec) -> bool:
        ...

    @abc.abstractmethod
    def write_code(
        self, spec: importlib.machinery.ModuleSpec,
    ) -> types.CodeType:
        ...

    # Helper methods

    @classmethod
    def _warn_once(
        cls,
        config: Union[pytest.Config, None],
        warning: Warning,
        stacklevel: int = 2,
    ) -> None:
        """
        Helper function making sure that warnings that are meant to be
        issued once per test session are treated as such.
        """
        if config is None:
            return
        key = id(config), type(warning), str(warning)
        if key in cls._issued_warnings:
            return
        cls._issued_warnings.add(key)
        _issue_warning(warning, stacklevel=stacklevel + 1)

    @staticmethod
    def find_spec_by_path(
        *args, use_meta_path: bool = False, **kwargs
    ) -> Union[importlib.machinery.ModuleSpec, None]:
        """
        Implementation of
        `importlib.abc.MetaPathFinder.find_spec()` which looks for
        module specs with the other meta-path finders.

        Parameters
        ----------
        use_meta_path
            If true, try use entries in `sys.meta_path` which have
            nothing to do with this module to find the spec;
            else, just use `importlib.machinery.PathFinder`
        *args, **kwargs
            Passed to `.find_spec()` of the finders

        Return
        ------
        `importlib.machinery.ModuleSpec` if one is found, `None`
        otherwise
        """
        Implementation = Callable[
            ..., Union[importlib.machinery.ModuleSpec, None]
        ]
        impls: List[Implementation] = []
        base_impl: Implementation = importlib.machinery.PathFinder.find_spec
        if use_meta_path:
            impls.extend(
                finder.find_spec for finder in sys.meta_path
                if callable(getattr(finder, 'find_spec', None))
                if not isinstance(finder, _AutoProfImporterBase)
            )
        if base_impl not in impls:
            impls.append(base_impl)
        for impl in impls:
            try:
                spec = impl(*args, **kwargs)
            except Exception:
                continue
            if spec is not None:
                return spec
        return None

    @staticmethod
    def _get_rewrite_asserts(config: pytest.Config) -> bool:
        return not isinstance(
            config.pluginmanager.rewrite_hook, DummyRewriteHook,
        )

    @staticmethod
    def module_spec_to_inode(
        spec: Union[importlib.machinery.ModuleSpec, None],
    ) -> Union[int, None]:
        try:
            return os.stat(
                spec.origin,  # type: ignore[arg-type, union-attr]
            ).st_ino
        except (TypeError, AttributeError, OSError):
            return None

    @classmethod
    def _classify_recursive_autoprof(
        cls, config: pytest.Config, **kwargs
    ) -> Tuple[Union[Literal[True], List[ImportPath]], List[ImportPath]]:
        targets = resolve_hooked_option(config, 'recursive_autoprof', **kwargs)
        if targets and all(t in (True,) for t in targets):
            return True, []
        valid: List[ImportPath] = []
        invalid: List[ImportPath] = []
        for ipath in targets:
            if ipath in (True,):
                continue
            (invalid if ipath.object else valid).append(ipath)
        if invalid:
            w = OptionParsingWarning.get_warning('recursive_autoprof', invalid)
            cls._warn_once(config, w)
        return valid, invalid

    @classmethod
    def get_always_autoprof(
        cls, config: pytest.Config, **kwargs
    ) -> List[ImportPath]:
        targets = resolve_hooked_option(config, 'always_autoprof', **kwargs)
        _, from_recursive_autoprof = cls._classify_recursive_autoprof(
            config, **kwargs,
        )
        return targets + from_recursive_autoprof

    @classmethod
    def get_recursive_autoprof(
        cls, config: pytest.Config, **kwargs
    ) -> Union[Literal[True], List[ImportPath]]:
        targets, _ = cls._classify_recursive_autoprof(config, **kwargs)
        return targets

    @classmethod
    def get_postimport_autoprof(
        cls, config: pytest.Config, **kwargs
    ) -> Union[Literal[True], List[ImportPath]]:
        targets = resolve_hooked_option(
            config, 'postimport_autoprof', **kwargs,
        )
        if targets and all(t in (True,) for t in targets):
            return True
        return [target for target in targets if target not in (True,)]

    get_autoprof_mod = staticmethod(functools.partial(
        resolve_hooked_option, opt_or_dest='autoprof_mod',
    ))
    get_autoprof_imports = staticmethod(functools.partial(
        resolve_hooked_option, opt_or_dest='autoprof_imports',
    ))
    get_autoprof_tests = staticmethod(functools.partial(
        resolve_hooked_option, opt_or_dest='autoprof_tests',
    ))

    # Attributes

    @property
    @abc.abstractmethod
    def always_autoprof(self) -> FrozenSet[ImportPath]:
        ...

    @property
    @abc.abstractmethod
    def recursive_autoprof(self) -> FrozenSet[ImportPath]:
        ...

    @property
    @abc.abstractmethod
    def postimport_autoprof(self) -> FrozenSet[ImportPath]:
        ...

    @property
    @abc.abstractmethod
    def autoprof_mod(self) -> FrozenSet[ImportPath]:
        ...

    @property
    def autoprof_targets(self) -> FrozenSet[ImportPath]:
        return self.always_autoprof | self.recursive_autoprof

    @property
    @abc.abstractmethod
    def autoprof_imports(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def autoprof_tests(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def stash(self) -> 'AutoProfStash':
        ...

    @property
    def _importers(self) -> List[Union['AutoProfImporter', '_SubprocImporter']]:
        return self.stash.importers

    @property
    def _profiler(self) -> LineProfiler:
        return self.stash.profiler

    # (De-)Serialization

    @abc.abstractmethod
    def _get_subproc_importer(self) -> '_SubprocImporter':
        ...

    def _get_serializable_attrs(self) -> Dict[Annotated[str, Identifier], Any]:
        return {attr: getattr(self, attr) for attr in self._serializable_attrs}


class AutoProfImporter(_AutoProfImporterBase):
    """
    Finder-loader which rewrites modules at import-time with the
    machineries provided in `line_profiler.autoprofile`.
    """
    config: pytest.Config
    _SubprocImporter: ClassVar[Type['_SPI']]

    def __init__(self, config: pytest.Config, *args, **kwargs) -> None:
        self.config = config
        super().__init__(config, *args, **kwargs)

    def _get_subproc_importer(self) -> '_SPI':
        return self._SubprocImporter(**self._get_serializable_attrs())

    @classmethod
    def from_pytest_args(
        cls, pytest_args: Sequence[str] = (), /, *args, **kwargs
    ) -> Self:
        return cls(get_config(pytest_args), *args, **kwargs)

    @functools.cached_property
    def always_autoprof(self) -> FrozenSet[ImportPath]:
        return frozenset(self.get_always_autoprof(self.config))

    @functools.cached_property
    def recursive_autoprof(self) -> FrozenSet[ImportPath]:
        recursive_autoprof = self.get_recursive_autoprof(self.config)
        if recursive_autoprof in (True,):
            return frozenset(
                ipath for ipath in self.always_autoprof if not ipath.object
            )
        if TYPE_CHECKING:  # Help `mypy` out
            assert recursive_autoprof is not True
        return frozenset(recursive_autoprof)

    @functools.cached_property
    def postimport_autoprof(self) -> FrozenSet[ImportPath]:
        postimport_autoprof = self.get_postimport_autoprof(self.config)
        if postimport_autoprof in (True,):
            return self.always_autoprof | self.recursive_autoprof
        if TYPE_CHECKING:  # Help `mypy` out
            assert postimport_autoprof is not True
        return frozenset(postimport_autoprof)

    @functools.cached_property
    def autoprof_mod(self) -> FrozenSet[ImportPath]:
        return frozenset(self.get_autoprof_mod(self.config))

    @functools.cached_property
    def autoprof_imports(self) -> bool:
        return self.get_autoprof_imports(self.config)

    @functools.cached_property
    def autoprof_tests(self) -> bool:
        return self.get_autoprof_tests(self.config)

    @property
    def stash(self) -> 'AutoProfStash':
        config = self.config
        try:
            return config.stash[AUTOPROF_STASH_KEY]
        except KeyError:
            return AutoProfStash.from_config(config)


class _SubprocImporter(_AutoProfImporterBase):
    """
    Deputy finder-loader objects that handle auto-profiling in
    subprocesses.
    """
    config: ClassVar[None] = None
    shared_stash: ClassVar['AutoProfStash']

    def __init__(
        self,
        *args,
        always_autoprof: Collection[ImportPath] = (),
        recursive_autoprof: Collection[ImportPath] = (),
        postimport_autoprof: Collection[ImportPath] = (),
        autoprof_mod: Collection[ImportPath] = (),
        autoprof_imports: bool = False,
        autoprof_tests: bool = False,
        **kwargs
    ) -> None:
        super().__init__(
            *args,
            always_autoprof=always_autoprof,
            recursive_autoprof=recursive_autoprof,
            postimport_autoprof=postimport_autoprof,
            autoprof_mod=autoprof_mod,
            autoprof_imports=autoprof_imports,
            autoprof_tests=autoprof_tests,
            **kwargs,
        )
        self.always_autoprof = frozenset(always_autoprof)
        self.recursive_autoprof = frozenset(recursive_autoprof)
        self.postimport_autoprof = frozenset(postimport_autoprof)
        self.autoprof_mod = frozenset(autoprof_mod)
        self.autoprof_imports = bool(autoprof_imports)
        self.autoprof_tests = bool(autoprof_tests)

    def __getstate__(self) -> Dict[Annotated[str, Identifier], Any]:
        return self._get_serializable_attrs()

    def __setstate__(
        self, state: Dict[Annotated[str, Identifier], Any],
    ) -> None:
        type(self).__init__(self, **state)

    always_autoprof = _FallThruProperty[FrozenSet[ImportPath]]()
    recursive_autoprof = _FallThruProperty[FrozenSet[ImportPath]]()
    postimport_autoprof = _FallThruProperty[FrozenSet[ImportPath]]()
    autoprof_mod = _FallThruProperty[FrozenSet[ImportPath]]()
    autoprof_imports = _FallThruProperty[bool]()
    autoprof_tests = _FallThruProperty[bool]()

    def _get_subproc_importer(self) -> Self:
        return self

    @property
    def stash(self) -> 'AutoProfStash':
        return type(self).shared_stash


_SPI = _SubprocImporter


class _ProfileModulesMixin:
    importer_class: ClassVar[str] = 'modules'

    def rewrite_needed(self, spec: importlib.machinery.ModuleSpec) -> bool:
        """
        Rewrite modules whose names match `.autoprof_targets`, or are
        otherwise deemed a target (e.g. because they are submodules of
        one of the `.recursive_autoprof`s)
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        affected_modules: Set[Annotated[str, ChainedIdentifier]] = {
            module for module, _ in self.autoprof_targets
        }
        if spec.name in affected_modules:
            return True
        return self.should_profile_entire_module(spec.name)

    def write_code(
        self, spec: importlib.machinery.ModuleSpec,
    ) -> types.CodeType:
        """
        Profile the script to import via rewriting all the matching
        function/method definitions.
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        prof_targets = self.autoprof_targets
        if self.should_profile_entire_module(spec.name):
            prof_targets |= {ImportPath(spec.name)}
        module, _ = StrictModuleRewriter.transform_module(
            spec, prof_targets,
        )
        return _compile_module(module, spec, self.config)

    def exec_module(self, module: types.ModuleType) -> None:
        """
        Rewrite the module AST, execute it, and post-hoc register the
        specific profiling targets if necessary.
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        # Handle the basic rewrites and on-import profiling
        super().exec_module(module)  # type: ignore[misc]
        try:
            name = module.__spec__.name  # type: ignore[union-attr]
        except AttributeError:
            return
        if not isinstance(name, str):
            return
        # Handle by-name profiling for objects defined in the module
        _, non_recursive_targets = self._default_explicit_targets
        non_recursive_targets |= self.autoprof_targets
        targets: Set[Annotated[str, ChainedIdentifier]] = {
            object for package, object in non_recursive_targets
            if package == name and object
        }
        profile = vars(module).setdefault('profile', self._profiler)
        attrgetter = operator.attrgetter
        profiled_additional_targets = False
        for target in targets:
            try:
                obj = attrgetter(target)(module)
            except AttributeError:
                continue
            try:
                if profile.add_imported_function_or_module(obj, silent=False):
                    profiled_additional_targets = True
            except Exception:
                pass
        # If we profiled anything missed by `.write_code()`, register
        # the module as profiled
        if profiled_additional_targets:
            self._register_usage(name)

    def add_targets_explicitly(
        self,
        targets: Optional[Collection[ImportPath]] = None,
        *,
        recurse: Optional[bool] = None,
    ) -> int:
        """
        Instead of setting up profiling via rewriting modules, add
        targets to the profiler on a post-hoc basis.

        Parameters
        ----------
        targets
            Optional collection of `~._typing.ImportPath`s to profile;
            if not provided, use `.postimport_autoprof`
        recurse
            Optional boolean value for whether to recurse down profiling
            targets that are packages;
            default is to
            - NOT recurse if `targets` is supplied, otherwise
            - INFER whether to recurse into each of
              `.postimport_autoprof` as below:
              - If a target is in `.recursive_autoprof`, RECURSE into it
              - Else, if it is in `.always_autoprof`, DON'T recurse into
                it
              - Else, recurse into packages and not other targets

        Return
        ------
        Number of targets profiled

        See also
        --------
        `line_profiler.autoprofile.eager_preimports
        .resolve_profiling_targets()`
        """
        def target_key(target: ImportPath) -> Tuple[List[str], List[str]]:
            return target.module.split('.'), (target.object or '').split('.')

        def get_class_name(cls: type) -> Annotated[str, ChainedIdentifier]:
            if cls.__module__ == 'builtins':
                return cls.__name__
            return '{0.__module__}.{0.__qualname__}'.format(cls)

        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        recursive_targets: FrozenSet[ImportPath]
        non_recursive_targets: FrozenSet[ImportPath]
        if targets is None:
            warning_prefix = '--postimport-autoprof: '
            recursive_targets, non_recursive_targets = (
                self._default_explicit_targets
            )
            if recurse is not None:
                if recurse:
                    recursive_targets |= non_recursive_targets
                    non_recursive_targets = frozenset()
                else:
                    non_recursive_targets |= recursive_targets
                    recursive_targets = frozenset()
        else:
            warning_prefix = ''
            targets = frozenset(targets)
            if recurse:
                recursive_targets, non_recursive_targets = targets, frozenset()
            else:
                recursive_targets, non_recursive_targets = frozenset(), targets

        profile = functools.partial(
            self._profiler.add_imported_function_or_module, silent=False,
        )
        profiled_modules: Set[Annotated[str, ChainedIdentifier]] = set()
        direct_targets = recursive_targets | non_recursive_targets
        indirect_targets: Set[ImportPath] = set()
        failures: Dict[Type[Exception], Set[ImportPath]] = {}
        tally = 0
        # Recurse down module targets
        for target in recursive_targets:
            if target.object:
                continue
            try:
                module_obj = target.import_target()
            except ImportError as e:
                failures.setdefault(type(e), set()).add(target)
                continue
            if not getattr(module_obj, '__path__', []):
                continue
            for module_info in pkgutil.walk_packages(
                module_obj.__path__, prefix=target.module + '.',
            ):
                indirect_targets.add(ImportPath(module_info.name))
        indirect_targets -= direct_targets
        # Import and add to the profiler
        accepted_errors: Type[Exception]
        for targets, accepted_errors, add_to_tally in [
            (indirect_targets, Exception, 0),
            (direct_targets, ImportError, 1),
        ]:
            # Try profiling from bottom-up
            for target in sorted(targets, key=target_key, reverse=True):
                try:
                    obj = target.import_target()
                    if profile(obj):
                        profiled_modules.add(target.module)
                        tally += add_to_tally
                except accepted_errors as e:
                    failures.setdefault(type(e), set()).add(target)
        # Bookkeeping
        if failures:
            nfailures = sum(len(targets) for targets in failures.values())
            pl_target = 'target' if nfailures == 1 else 'targets'
            header = '{}{} {} cannot be profiled:'.format(
                warning_prefix, nfailures, pl_target,
            )
            warning_lines = [header]
            for exc_type, targets in sorted(
                (get_class_name(Xc), ts) for Xc, ts in failures.items()
            ):
                rep_targets = ', '.join(
                    str(target) for target in sorted(targets, key=target_key)
                )
                warning_lines.append(
                    '- {} ({}): {}'
                    .format(exc_type, len(targets), rep_targets),
                )
            self._warn_once(self.config, UserWarning('\n'.join(warning_lines)))
        for module in profiled_modules:
            self._register_usage(module)
        return tally

    def should_profile_entire_module(
        self, module: Annotated[str, ChainedIdentifier],
    ) -> bool:
        """
        Return
        ------
        Whether `module` is to be profiled by rewriting in its entirety
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        entirely_profiled_packages: Set[Annotated[str, ChainedIdentifier]] = {
            package for package, object in self.autoprof_targets
            if object is None
        }
        if module in entirely_profiled_packages:
            return True
        # If the whole namespace is to be recursively profiled, check
        # submodules
        return module.startswith(tuple(
            package + '.' for package, _ in self.recursive_autoprof
        ))

    @functools.cached_property
    def _default_explicit_targets(self) -> Tuple[
        FrozenSet[ImportPath], FrozenSet[ImportPath],
    ]:
        """
        Return
        ------
        In a 2-tuple:
        `tuple[frozenset[recur_ipath], frozenset[non_recur_ipath]]`
        Where `recur_ipath` and `non_recur_ipath` are resp.
        `~._typing.ImportPath` objects that should be recursed into and
        not

        Example
        -------
        >>> from typing import List, Tuple
        >>>
        >>>
        >>> def get_targets_from_pytest_args(
        ...     *args: str,
        ... ) -> Tuple[List[str], List[str]]:
        ...     return tuple(
        ...         sorted(str(path) for path in paths)
        ...         for paths
        ...         in get_importer(args)._default_explicit_targets
        ...     )
        ...
        >>>
        >>> get_importer = ProfileModulesImporter.from_pytest_args

        Modules/packages are recursed into by default:

        >>> get_targets_from_pytest_args(
        ...     '--postimport-autoprof=foo.bar,foo.baz::spam'
        ... )
        (['foo.bar'], ['foo.baz::spam'])

        If `--always-autoprof` and/or `--recursive-autoprof` are
        supplied, they are used in determining which targets to recurse
        into:

        >>> get_targets_from_pytest_args(
        ...     '--always-autoprof=foo.bar,foo.baz::spam',
        ...     '--recursive-autoprof=foo.foobar',
        ...     '--postimport-autoprof',
        ... )
        (['foo.foobar'], ['foo.bar', 'foo.baz::spam'])
        >>> get_targets_from_pytest_args(
        ...     '--always-autoprof=foo.bar,foo.baz::spam',
        ...     '--recursive-autoprof=foo.foobar',
        ...     # '--postimport-autoprof',  # No flag, no expl. prof.
        ... )
        ([], [])

        If `--always-autoprof` and/or `--recursive-autoprof` are
        mixed with `--postimport-autoprof`, whether elements in the
        latter are to be recursed into can be controlled by their
        presence in the former:

        >>> get_targets_from_pytest_args(
        ...     '--always-autoprof=foo.bar,foo.baz::spam',
        ...     '--recursive-autoprof=foo.foobar',
        ...     '--postimport-autoprof=foo.bar,foo.foobar',  # Inherited
        ...     '--postimport-autoprof=foo.baz,foo::Bar',  # Inferred
        ... )
        (['foo.baz', 'foo.foobar'], ['foo.bar', 'foo::Bar'])
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        recurse_these = self.recursive_autoprof
        dont_recurse_these = self.always_autoprof - self.recursive_autoprof
        recursive_targets: Set[ImportPath] = set()
        non_recursive_targets: Set[ImportPath] = set()
        for target in self.postimport_autoprof:
            if target in recurse_these:
                targets = recursive_targets
            elif target in dont_recurse_these:
                targets = non_recursive_targets
            elif target.object:
                targets = non_recursive_targets
            else:
                targets = recursive_targets
            targets.add(target)
        return frozenset(recursive_targets), frozenset(non_recursive_targets)


class ProfileModulesImporter(_ProfileModulesMixin, AutoProfImporter):
    """
    Class rewriting the global modules which are to be profiled, as
    specified by the `--always-autoprof` flag.

    Notes
    -----
    This is meant to be a singleton for the entire test session.
    """
    class _SubprocImporter(_ProfileModulesMixin, _SPI):
        pass


class _ProfileTestsMixin:
    _serializable_attrs: ClassVar[FrozenSet[Annotated[str, Identifier]]] = (
        frozenset({'_rewrite_asserts', '_test_patterns'})
    )
    importer_class: ClassVar[str] = 'tests'

    def rewrite_needed(self, spec: importlib.machinery.ModuleSpec) -> bool:
        """
        Rewrite test files whose names match
        `.config.getini('python_files')` if necessary.
        """
        try:
            fpath = pathlib.Path(spec.origin)  # type: ignore[arg-type]
        except Exception:
            return False
        if not self.matcher(fpath):
            return False
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        return bool(
            self.autoprof_targets or self.autoprof_mod or self.autoprof_tests
        )

    def write_code(
        self, spec: importlib.machinery.ModuleSpec,
    ) -> types.CodeType:
        """
        Auto-profile the test file by profiling its imports according to
        `.autoprof_mod` with `.autoprof_imports`;
        if `.autoprof_tests`, the entirety of test file itself is
        profiled.
        """
        if TYPE_CHECKING:
            assert isinstance(self, (AutoProfImporter, _SubprocImporter))
        prof_targets = self.autoprof_targets | self.autoprof_mod
        # Also profile the entirety of the test script in question if
        # asked to
        if self.autoprof_tests:
            prof_targets |= {spec.origin}
        return rewrite_tests(
            spec, self.config,
            prof_targets=prof_targets,
            prof_imports=self.autoprof_imports,
            rewrite_asserts=self._rewrite_asserts,
        )

    @staticmethod
    def _get_matcher(
        patterns: Collection[str],
    ) -> Callable[[Union[pathlib.PurePath, str]], bool]:
        def matcher(fname: Union[pathlib.PurePath, str]) -> bool:
            patterns = matcher.patterns  # type: ignore[attr-defined]
            return any(fnmatch_ex(pat, fname) for pat in patterns)

        matcher.patterns = (  # type: ignore[attr-defined]
            frozenset(patterns)
        )
        return matcher

    @functools.cached_property
    def matcher(self):
        return self._get_matcher(self._test_patterns)

    @property
    @abc.abstractmethod
    def _rewrite_asserts(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def _test_patterns(self) -> FrozenSet[str]:
        ...


class ProfileTestsImporter(_ProfileTestsMixin, AutoProfImporter):
    """
    Class rewriting the tests which are to be profiled, as
    specified by the `--autoprof-mod`, `--autoprof-imports`, and
    `--autoprof-tests` flags.

    Notes
    -----
    This is meant to be a singleton for the entire test session.
    """
    @staticmethod
    def _get_test_path_patterns(config: pytest.Config) -> Tuple[str, ...]:
        # Taken from `_pytest.assertion.rewrite.AssertionRewritingHook`
        try:
            return tuple(config.getini("python_files"))
        except ValueError:
            return _DEFAULT_TEST_PATH_PATTERNS

    @classmethod
    def get_path_matcher(
        cls, config: pytest.Config,
    ) -> Callable[[Union[pathlib.PurePath, str]], bool]:
        return cls._get_matcher(cls._get_test_path_patterns(config))

    @property
    def _rewrite_asserts(self) -> bool:
        return self._get_rewrite_asserts(self.config)

    @property
    def _test_patterns(self) -> FrozenSet[str]:
        return frozenset(self._get_test_path_patterns(self.config))

    class _SubprocImporter(_ProfileTestsMixin, _SPI):
        def __init__(
            self,
            *args,
            _test_patterns: Collection[str] = (
                _DEFAULT_TEST_PATH_PATTERNS
            ),
            **kwargs
        ) -> None:
            super().__init__(
                *args,
                _test_patterns=_test_patterns,
                **kwargs,
            )
            self._test_patterns = _test_patterns

        # In a subprocess we have no access to a `pytest.Config` object,
        # and as such don't know how to rewrite assertions;
        # so just give up

        @property
        def _rewrite_asserts(self) -> Literal[False]:
            return False

        _test_patterns = _FallThruProperty[FrozenSet[str]]()


@dataclasses.dataclass
class AutoProfStash:
    importers: List[
        Union[AutoProfImporter, _SubprocImporter]
    ] = dataclasses.field(default_factory=list)
    existing: Dict[Annotated[str, ChainedIdentifier], types.ModuleType] = (
        dataclasses.field(default_factory=dict)
    )
    profiler: LineProfiler = dataclasses.field(
        default_factory=LineProfiler,
    )
    log_messages: List[
        Tuple[str, int, Mapping[Annotated[str, Identifier], bool]]
    ] = dataclasses.field(default_factory=list)
    DoctestHandler: Optional[Type['_DoctestHandler']] = None
    process_id: int = os.getpid()
    cache_dir: pathlib.Path = (
        '.pytest_cache'  # type: ignore[assignment]
    )
    _cleanups: Dict[float, Set[Callable[[], Any]]] = dataclasses.field(
        default_factory=dict, init=False, repr=False,
    )

    def __post_init__(self) -> None:
        self.cache_dir = pathlib.Path(self.cache_dir).absolute()
        for callback in [
            self.importers.clear,
            self.existing.clear,
            self.profiler.uninstall,
            self.log_messages.clear,
        ]:
            self.add_cleanup(callback)

    def __del__(self):
        self.cleanup()

    def add_importer(self, importer: _Importer) -> _Importer:
        importer.install()
        self.importers.insert(0, importer)
        return importer

    def add_cleanup(
        self, cleanup: Callable[PS, Any], /,
        *args: PS.args, **kwargs: PS.kwargs
    ) -> None:
        self._add_cleanup(0, cleanup, *args, **kwargs)

    def _add_cleanup(
        self, priority: float, cleanup: Callable[PS, Any], /,
        *args: PS.args, **kwargs: PS.kwargs
    ) -> None:
        if args or kwargs:
            cleanup = functools.partial(cleanup, *args, **kwargs)
        self._cleanups.setdefault(priority, set()).add(cleanup)

    def log(self, msg: str, verbosity: int = 1, **markup: bool) -> str:
        self.log_messages.append((msg, verbosity, markup))
        return msg

    def cleanup(self):
        for priority in sorted(self._cleanups):
            callbacks = self._cleanups.pop(priority)
            while callbacks:
                cleanup = callbacks.pop()
                try:
                    cleanup()
                except Exception:
                    pass

    def _get_forked_stash(self) -> Self:
        """
        Notes
        -----
        Should only be invoked on forked subprocesses, preferrably
        directly after forking.
        """
        _SubprocImporter.shared_stash = forked = type(self)(
            importers=[im._get_subproc_importer() for im in self.importers],
            process_id=self.process_id,
            cache_dir=str(self.cache_dir),  # type: ignore[arg-type]
        )
        return forked

    def _dump(self, *, json: bool = _JSON_STASH) -> pathlib.Path:
        path = self.generate_new_tempfile(suffix='.stash')
        dumped = {
            'importers': [im._get_subproc_importer() for im in self.importers],
            'process_id': self.process_id,
            'tee_global_prof': self.profiler.tee_global_prof,
            'cache_dir': str(self.cache_dir),
        }
        if json:
            dump, mode = JSONHelper.dump, 'w'
        else:
            dump = functools.partial(pickle.dump, protocol=HIGHEST_PROTOCOL)
            mode = 'wb'
        with path.open(mode=mode) as fobj:
            dump(dumped, fobj)  # type: ignore[arg-type]
        return path

    @classmethod
    def _load_in_subproc(
        cls, file: Union[str, pathlib.PurePath], *, json: bool = _JSON_STASH,
    ) -> Self:
        """
        Notes
        -----
        Should only be invoked in subprocesses.
        """
        load, mode = (JSONHelper.load, 'r') if json else (pickle.load, 'rb')
        with open(file, mode=mode) as fobj:
            loaded = load(fobj)  # type: ignore[arg-type]
            tee_global_prof = loaded.pop('tee_global_prof')
            _SubprocImporter.shared_stash = stash = cls(**loaded)
            stash.profiler.tee_global_prof = tee_global_prof
        return stash

    def generate_new_tempfile(
        self, prefix: str = 'autoprof-', suffix: str = '.lprof', *,
        cleanup_priority: Union[float, None] = 0, isdir: bool = False,
    ) -> pathlib.Path:
        """
        Return
        ------
        `pathlib.Path` pointing to a new empty file/directory
        """
        cleanup: Union[Callable[[], Any], None] = None
        if isdir:
            fname = tempfile.mkdtemp(
                prefix=prefix, suffix=suffix, dir=self.scratch_dir,
            )
        else:
            handle, fname = tempfile.mkstemp(
                prefix=prefix, suffix=suffix, dir=self.scratch_dir,
            )
            # The low-level handle is nothing but trouble esp. on
            # Windows; close it preemptively and just use the path to
            # refer to the file
            cleanup = functools.partial(os.close, handle)
        try:
            path = pathlib.Path(fname)
            if cleanup_priority is None:  # No cleanup
                return path
            if isdir:
                self._add_cleanup(
                    cleanup_priority, shutil.rmtree, path, ignore_errors=True,
                )
            else:
                self._add_cleanup(
                    cleanup_priority, path.unlink, missing_ok=True,
                )
            return path
        finally:
            if cleanup:
                cleanup()

    @classmethod
    def from_config(
        cls, config: pytest.Config, *,
        add_to_config: Optional[bool] = None, **kwargs
    ) -> Self:
        if 'profiler' not in kwargs:
            kwargs['profiler'] = LineProfiler(config=config)
        if 'cache_dir' not in kwargs:
            kwargs['cache_dir'] = _get_cache_dir(config)
        stash = cls(**kwargs)
        stashes = config.stash
        if add_to_config is None and AUTOPROF_STASH_KEY not in stashes:
            add_to_config = True
        if add_to_config:
            stashes[AUTOPROF_STASH_KEY] = stash  # type: ignore[misc]
        return stash

    @classmethod
    def from_pytest_args(cls, args: Sequence[str] = (), /, **kwargs) -> Self:
        return cls.from_config(get_config(args), **kwargs)

    @property
    def profiler_used(self) -> bool:
        return bool(self.profiler.object_count)

    @property
    def scratch_dir(self) -> pathlib.Path:
        path = self.cache_dir / f'pytest-autoprofile-{self.process_id}'
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
            # Since tempfiles are written to `scratch_dir`, only delete
            # it after dealing with the other tempfiles
            self._add_cleanup(1023, shutil.rmtree, path, ignore_errors=True)
        return path

    @property
    def DoctestRunner(self) -> Union[Type[doctest.DocTestRunner], None]:
        # Note: for backward compatibility only
        Handler = self.DoctestHandler
        if Handler is None:
            return None
        if issubclass(Handler, doctest.DocTestRunner):
            return Handler
        return None


AUTOPROF_STASH_KEY = pytest.StashKey[AutoProfStash]()
