"""
Set up hooks for the additional options.
"""
import functools
import inspect
import pathlib
import sys
import textwrap
import types

import pytest

from ._typing import (
    TYPE_CHECKING,
    Dict, List, Set, Tuple,
    Mapping, Sequence,
    Callable, ParamSpec,
    Type, TypeVar, ClassVar, Generic, Protocol,
    Annotated, Any, Self,
    Literal, Union, Optional,
    overload,
    Parser, Parsable,
    Identifier, LineProfilerViewOptions, ImportPath,
)
from ._warnings import OptionParsingWarning

if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811


__all__ = (
    'Hook',
    'OptionParsingWarning',
    'resolve_hooked_option',
    'pytest_always_autoprof_default',
    'pytest_recursive_autoprof_default',
    'pytest_postimport_autoprof_default',
    'pytest_autoprof_mod_default',
    'pytest_autoprof_imports_default',
    'pytest_autoprof_tests_default',
    'pytest_autoprof_doctests_default',
    'pytest_autoprof_rewrite_doctests_default',
    'pytest_autoprof_subprocs_default',
    'pytest_autoprof_outfile_default',
    'pytest_autoprof_view_default',
    'pytest_autoprof_global_profiler_default',
)

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
Object = TypeVar('Object')
PS = ParamSpec('PS')

_ABSENT = type('_Absent', (), {'__repr__': lambda _: '<ABSENT>'})()


class CanAddOptions(Protocol, Generic[T_co]):
    def addoption(self, *args: str, **kwargs) -> T_co: ...


class Hook(Generic[PS, T]):
    """
    Wrapper around `@pytest.hookspec` which also defines the parser
    option associated with it.

    Parameters
    ----------
    spec()
        Callable to be passed to `@pytest.hookspec`;
        if not supplied, the object can be used to decorate a spec
    parser_flags, parser_kwargs
        Optional positional and keyword arguments to be passed to
        `pytest.Parser.addoption()`
    use_spec_as_default
        Whether to take `spec()` as a default implementation in
        `.__call__()`

    Notes
    -----
    use_spec_as_default

    - Even when true, `.spec()` is not explicitly registered as an
      implementation to avoid clobbering others when
      `firstresult = True`.

    - Since callables decorated by `@pytest.hookspec` are treated are
      expected to have no body and are not used, its behavior can be
      recovered by explicitly setting `use_spec_as_default = False`.
    """
    def __init__(
        self,
        spec: Optional[
            Callable[PS, Union[T, Annotated[str, Parsable[T]]]]
        ] = None,
        /,
        *args,
        parser_flags: Optional[Union[str, Sequence[str]]] = None,
        parser_kwargs: Optional[
            Mapping[Annotated[str, Identifier], Any]
        ] = None,
        use_spec_as_default: bool = True,
        **kwargs
    ) -> None:
        if spec is None:
            self.spec = functools.partial(  # Turn into a decorator
                type(self),
                parser_flags=parser_flags,
                parser_kwargs=parser_kwargs,
                use_spec_as_default=use_spec_as_default,
                **kwargs,
            )
            self._sig = None
            return
        self.spec = pytest.hookspec(spec, *args, **kwargs)
        self._sig = inspect.signature(spec)
        if not all(
            param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
            for param in self._sig.parameters.values()
        ):
            raise ValueError(
                f'spec = {spec!r} -> signature {self._sig}: '
                'hook specs should only have named positional arguments'
            )
        for name in [
            '__name__',
            '__qualname__',
            '__module__',
            '__signature__',
            '__annotations__',
            '__doc__',
        ]:
            if hasattr(spec, name):
                self.__dict__[name] = getattr(spec, name)
        self.parser_flags = (
            (parser_flags,)
            if isinstance(parser_flags, str) else
            tuple(parser_flags)
            if parser_flags else
            ()
        )
        self.parser_kwargs = dict(parser_kwargs or {})
        self.use_spec_as_default = bool(use_spec_as_default)
        self.hooks[spec.__name__] = self

    def __repr__(self) -> str:
        try:
            name = repr(self.name)
        except AttributeError:  # To be used to decorate the spec
            name = 'constructor'
        return (
            '<{0.__module__}.{0.__qualname__} object {1} at {2:#x}>'
            .format(type(self), name, id(self))
        )

    def __getattr__(self, attr: Annotated[str, Identifier]) -> Any:
        return getattr(self.spec, attr)

    @overload
    def __call__(
        self,
        x: Union[pytest.Config, pytest.PytestPluginManager],
        *args: PS.args,
        **kwargs: PS.kwargs
    ) -> T:
        ...

    @overload
    def __call__(
        self,
        x: Callable[PS, Union[T, Annotated[str, Parsable[T]]]],
        *args,
        **kwargs,
    ) -> Self:
        ...

    def __call__(
        self,
        x: Union[
            pytest.Config, pytest.PytestPluginManager,
            Callable[PS, Union[T, Annotated[str, Parsable[T]]]],
        ],
        *args,
        **kwargs
    ) -> Union[Self, T]:
        """
        Parameters
        ----------
        For a non-fully-initialized instance:
            x
                The hookspec
            *args, **kwargs
                The remaining arguments
        Else:
            x
                A `pytest.Config` or `~.PytestPluginManager` otherwise
            *args, **kwargs
                Passed to the resolved hook

        Return
        ------
        If a non-fully-initialized instance:
            A fully-initialized instance
        Else:
            The result of calling the resolved hook with the arguments
        """
        # Construct an instance from the supplied callable
        if not self._has_spec:
            if TYPE_CHECKING:
                assert callable(x)
                assert isinstance(self.spec, functools.partial)
            return self.spec(x, *args, **kwargs)
        # Try to retrieve the appropriate default from hooks added later
        # than `pytest_addoption()`, e.g. `conftest.py` hooks
        if isinstance(x, pytest.Config):
            x = x.pluginmanager
        if TYPE_CHECKING:
            assert isinstance(x, pytest.PytestPluginManager)
        caller = getattr(x.hook, self.name)
        if self.use_spec_as_default and not caller.get_hookimpls():
            caller = self.spec
        # Note: `pluggy` hook implementations only take keyword args
        if args:
            kwargs = self.bind_arguments(*args, **kwargs)
        value = caller(**kwargs)
        # Coerce the value if necessary and possible
        convert = self.convert
        if convert is None or not isinstance(value, str):
            return value
        return convert(value)

    @overload
    def __get__(self, instance: None, owner: Type[Object]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: Object, owner: Optional[Type[Object]] = None,
    ) -> types.MethodType:
        ...

    def __get__(
        self,
        instance: Union[Object, None],
        owner: Optional[Type[Object]] = None,
    ) -> Union[types.MethodType, Self]:
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def __isabstractmethod__(self) -> bool:
        return getattr(self.spec, '__isabstractmethod__', False)

    def bind_arguments(
        self, *args, **kwargs
    ) -> Dict[Annotated[str, Identifier], Any]:
        """
        Return
        ------
        The passed arguments mapped to a keyword dictionary
        """
        assert self._sig
        return self._sig.bind(*args, **kwargs).arguments

    def add_option(self, parser_like: CanAddOptions) -> functools.partial:
        """
        Parameters
        ----------
        parser_like
            Object (e.g. `pytest.Parser` which has an `.addoption()`
            method)

        Return
        ------
        `functools.partial` object which is a caller for
        `parser_like.addoption()` with the `.parser_flags` supplied as
        leading positional arguments, and the `.parser_kwargs` supplied
        as keyword arguments
        """
        return functools.partial(
            parser_like.addoption, *self.parser_flags, **self.parser_kwargs,
        )

    @property
    def name(self) -> Annotated[str, Identifier]:
        if self._has_spec:
            return self.spec.__name__
        else:
            raise AttributeError(
                f'{type(self).__name__}.name: no `.spec` provided'
            )

    @property
    def convert(self) -> Union[Parser[T], None]:
        convert = self.parser_kwargs.get('type')
        return convert if callable(convert) else None

    @property
    def _has_spec(self) -> bool:
        if type(self.spec) is not functools.partial:
            return True
        if self.spec.func is not type(self):
            return True
        return False

    # Class attributes
    hooks: ClassVar[Dict[Annotated[str, Identifier], 'Hook']] = {}
    # Attributes
    _sig: Union[inspect.Signature, None]
    spec: Union[
        Callable[PS, Union[T, Annotated[str, Parsable[T]]]],
        Callable[
            [Callable[PS, Union[T, Annotated[str, Parsable[T]]]]],
            'Hook[PS, T]'
        ],
    ]
    parser_flags: Sequence[str]
    parser_kwargs: Dict[Annotated[str, Identifier], Any]
    use_spec_as_default: bool


# Note: the Python 3.8 interpreter struggles with constructions like
# >>> @SomeGenericClass[SomeTypeVar](...)
# ... def some_func(...): ...
# so extract all the generic-type parametrization out here

if TYPE_CHECKING or sys.version_info[:2] >= (3, 10):
    _import_paths_hook = Hook[[], List[ImportPath]]
    _trues_or_import_paths_hook = Hook[
        [], Union[List[Literal[True]], List[ImportPath]]
    ]
    _outfile_hook = Hook[[pytest.Config], Union[pathlib.PurePath, str]]
    _view_options_hook = Hook[[], Union[LineProfilerViewOptions, bool]]
    _all_or_bool_book = Hook[[], Union[Literal['all'], bool]]
    _always_or_bool_book = Hook[[], Union[Literal['always'], bool]]
else:
    # Cannot create generic alias with arg-type lists in Python < 3.10,
    # so just give up on parametrizing them (doesn't matter at runtime)
    _import_paths_hook = Hook
    _trues_or_import_paths_hook = Hook
    _outfile_hook = Hook
    _view_options_hook = Hook
    _all_or_bool_book = Hook
    _always_or_bool_book = Hook


########################################################################
#                                Hooks                                 #
########################################################################


def _one_line(string: str) -> str:
    """
    Example
    -------
    >>> string = '''
    ...     Foo bar baz
    ...     spam ham
    ... '''
    >>> _one_line(string)
    'Foo bar baz spam ham'
    """
    return textwrap.fill(
        textwrap.dedent(string).strip('\n'),
        float('inf'),  # type: ignore[arg-type]
    )


@overload
def _boolean_hook(
    hookspec: Callable[PS, Union[bool, Annotated[str, Parsable[bool]]]],
    *,
    parser_flags: Optional[Union[str, Sequence[str]]] = None,
    **kwargs
) -> Hook[PS, bool]:
    ...


@overload
def _boolean_hook(
    hookspec: None = None,
    *,
    parser_flags: Optional[Union[str, Sequence[str]]] = None,
    **kwargs
) -> Callable[
    [Callable[PS, Union[bool, Annotated[str, Parsable[bool]]]]],
    Hook[PS, bool]
]:
    ...


def _boolean_hook(
    hookspec: Optional[
        Callable[PS, Union[bool, Annotated[str, Parsable[bool]]]]
    ] = None,
    *,
    parser_flags: Optional[Union[str, Sequence[str]]] = None,
    **kwargs
) -> Union[
    Hook[PS, bool],
    Callable[
        [Callable[PS, Union[bool, Annotated[str, Parsable[bool]]]]],
        Hook[PS, bool]
    ],
]:
    """
    Convenience decorator for setting up boolean flags. The docstring
    is turned into the help text of the option, and the name of the
    option is taken from the hook-spec name (assumed to be of the form
    'pytest_<name>_default').
    """
    if hookspec is None:
        return functools.partial(  # type: ignore[return-value]
            _boolean_hook, parser_flags=parser_flags, **kwargs
        )

    # Massage the parameters
    flag_name: Union[str, None]
    if isinstance(parser_flags, str):
        parser_flags = parser_flags,
    if parser_flags is None:
        assert hookspec.__name__.startswith('pytest_')
        assert hookspec.__name__.endswith('_default')
        name = hookspec.__name__[len('pytest_'):-len('_default')]
        parser_flags = flag_name = '--' + name.replace('_', '-')
    else:
        flag_name = next(
            (flag for flag in parser_flags if flag.startswith('--')),
            parser_flags[0],
        )
    parser_kwargs = dict(
        const=True,
        metavar='yes|no',
        nargs='?',
        type=parse_boolean,
    )
    hook_kwargs = dict(
        firstresult=True,
        parser_flags=parser_flags,
        parser_kwargs=parser_kwargs,
    )
    parser_kwargs.update(kwargs.pop('parser_kwargs', {}))
    hook_kwargs.update(**kwargs)

    # Set up the docstrings
    if hookspec.__doc__ and not hookspec.__doc__.isspace():
        parser_kwargs.setdefault(
            'help', _one_line(hookspec.__doc__),
        )
    hookspec.__doc__ = f"""
    Return
    ------
    Default value for the boolean flag `{flag_name}`, which is to
    be (a string parsable into) a boolean;
    parsing is case-insensitive, and the following are recognized:
    - Parsed into `True`:
      '1', 'T', 'True', 'Y', 'yes'
    - Parsed into `False`:
      '0', 'F', 'False', 'N', 'no'

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """

    # Supply default type annotations
    sig = inspect.signature(hookspec)
    if sig.return_annotation is sig.empty:
        BoolLike = Union[bool, Annotated[str, Parsable[bool]]]
        hookspec.__signature__ = (  # type: ignore[attr-defined]
            sig.replace(return_annotation=BoolLike)
        )

    return Hook[PS, bool](
        hookspec, **hook_kwargs,  # type: ignore[arg-type]
    )


def parse_boolean(s: Annotated[str, Parsable[bool]]) -> bool:
    """
    Example
    -------
    >>> for s in '1 2  t True YeS y'.split(): assert parse_boolean(s)
    >>> for s in '0  f faLse no N'.split(): assert not parse_boolean(s)
    >>> parse_boolean('what')  # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: expected any of
    ['y', 'yes', 't', 'true', 'n', 'no', 'f', 'false'],
    got 'what'
    """
    if s.isnumeric():
        return bool(int(s))
    table = {
        **dict.fromkeys(['y', 'yes', 't', 'true'], True),
        **dict.fromkeys(['n', 'no', 'f', 'false'], False),
    }
    s = s.lower()
    if s not in table:
        raise ValueError(f'expected any of {list(table)}, got {s!r}')
    return table[s]


def parse_view_options(
    x: Annotated[str, Parsable[bool], Parsable[LineProfilerViewOptions]],
) -> Union[bool, LineProfilerViewOptions]:
    try:
        return parse_boolean(x)
    except ValueError:
        return LineProfilerViewOptions.parse(x)


@_import_paths_hook(
    firstresult=True,
    parser_flags='--always-autoprof',
    parser_kwargs=dict(
        action='extend',
        metavar='MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]',
        type=ImportPath.parse_multiple,
        help=_one_line("""
    Comma separated list of entities which are to be auto-line-profiled
    ON IMPORT, no questions asked
    (equivalent to the `--line-profile` flag supplied by
    `pytest-line-profiler`;
    multiple copies of this flag can be passed and are concatenated;
    defaults can be supplied via the `pytest_always_autoprof_default()`
    hook)
        """),
    ),
)
def pytest_always_autoprof_default() -> Union[
    List[ImportPath], Annotated[str, Parsable[List[ImportPath]]],
]:
    """
    Return
    ------
    Default value for the flag `--always-autoprof`, which is to be a
    comma-separated list of paths for objects to be profiled:
    - Module/Package:
      'MODULE_OR_PACKAGE.DOTTED.PATH'
    - Other objects (e.g. methods):
      'MODULE_OR_PACKAGE.DOTTED.PATH::OBJECT.DOTTED.PATH'

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """
    return []


@_trues_or_import_paths_hook(
    firstresult=True,
    parser_flags='--recursive-autoprof',
    parser_kwargs=dict(
        action='extend',
        const=(True,),
        metavar='MODULE.DOTTED.PATH[,...]',
        nargs='?',
        type=ImportPath.parse_multiple,
        help=_one_line("""
    Comma separated list of modules/packages, which (along with their
    submodules) are to be recursively auto-line-profiled ON IMPORT à la
    `--always-autoprof`
    (if supplied without an argument, all the
    packages to be fully profiled as specified by `--always-autoprof`
    will be descended into;
    multiple copies of this flag can be passed and are concatenated;
    defaults can be supplied via the
    `pytest_recursive_autoprof_default()` hook)
        """),
    ),
)
def pytest_recursive_autoprof_default() -> Union[
    List[Literal[True]],
    List[ImportPath],
    Annotated[str, Parsable[List[ImportPath]]],
]:
    """
    Return
    ------
    Default value for the flag `--recursive-autoprof`, which is to be a
    comma-separated list of paths for modules/objects to be profiled:
    - Module/Package:
      'MODULE_OR_PACKAGE.DOTTED.PATH'
    Alternatively, implementations can return a list containing a single
    `True`, to indicate that all packages specified in
    `--always-autoprof` are to be descended into and have their
    submodules profiled

    Notes
    -----
    - Default values can be supplied via `conftest.py` or other plugins
      with a synonymous callable of compatible signature.
    - If a spec contains a non-module part ('::<obj>'), a warning is
      issued, and the spec is instead handled by `--always-autoprof`.
    - The return value for indicating that all `--always-autoprof`
      targets are to be handled recursively has to be `[True]` instead
      of the more intuitive `True`, because the flag
      `--recursive-autoprof` is a list-extending flag, and expects a
      list as the default value.
    """
    return []


@_trues_or_import_paths_hook(
    firstresult=True,
    parser_flags='--postimport-autoprof',
    parser_kwargs=dict(
        action='extend',
        const=(True,),
        metavar='MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]',
        nargs='?',
        type=ImportPath.parse_multiple,
        help=_one_line("""
    Comma separated list of targets, which are to be auto-line-profiled
    à la `--always-autoprof`, but AFTER they or their modules have been
    imported
    (if supplied without an argument, all the targets
    specified by `--always-autoprof` and `--recursive-autoprof`
    will be profiled post-import;
    targets explicitly supplied here but not included by the other two
    flags will be recursed into if they are packages;
    multiple copies of this flag can be passed and are concatenated;
    defaults can be supplied via the
    `pytest_postimport_autoprof_default()` hook)
        """),
    ),
)
def pytest_postimport_autoprof_default() -> Union[
    List[Literal[True]],
    List[ImportPath],
    Annotated[str, Parsable[List[ImportPath]]],
]:
    """
    Return
    ------
    Default value for the flag `--postimport-autoprof`, which is to be a
    comma-separated list of paths for modules/objects to be profiled:
    - Module/Package:
      'MODULE_OR_PACKAGE.DOTTED.PATH'
    - Other objects (e.g. methods):
      'MODULE_OR_PACKAGE.DOTTED.PATH::OBJECT.DOTTED.PATH'
    Alternatively, implementations can return a list containing a single
    `True`, to indicate that all packages specified in
    `--always-autoprof` and `--recursive-autoprof` are to be profiled
    post-import instead of pre-import via module rewriting.

    Notes
    -----
    - Default values can be supplied via `conftest.py` or other plugins
      with a synonymous callable of compatible signature.
    - Specs are profiled with
      `ProfileModulesImporter.add_targets_explicitly()`;
      whether they are recursed/descended into depends on whether they
      are found among `--always-autoprof` and `--recursive-autoprof`.
      If neither, package specs are descended into, and other specs are
      not.
    - The return value for indicating that all `--always-autoprof`
      and `--recursive-autoprof` targets are to be profiled post-import
      has to be `[True]` instead of the more intuitive `True`, because
      the flag `--postimport-autoprof` is a list-extending flag, and
      expects a list as the default value.
    - This option is mostly useful for setting up profiling for direct
      dependencies of this plugin (e.g. components of `line_profiler`
      itself).
    """
    return []


@_import_paths_hook(
    firstresult=True,
    parser_flags='--autoprof-mod',
    parser_kwargs=dict(
        action='extend',
        metavar='MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]',
        type=ImportPath.parse_multiple,
        help=_one_line("""
    Comma separated list of entities which are to be auto-profiled,
    if they are imported in any of the tests
    (equivalent to the `--prof-mod` flag of `kernprof`;
    multiple copies of this flag can be passed and are concatenated;
    defaults can be supplied via the `pytest_autoprof_mod_default()`
    hook)
        """),
    ),
)
def pytest_autoprof_mod_default() -> Union[
    List[ImportPath], Annotated[str, Parsable[List[ImportPath]]],
]:
    """
    Return
    ------
    Default value for the flag `--autoprof-mod`, which is to be a
    comma-separated list of paths for objects to be profiled:
    - Module/Package:
      'MODULE_OR_PACKAGE.DOTTED.PATH'
    - Other objects (e.g. methods):
      'MODULE_OR_PACKAGE.DOTTED.PATH::OBJECT.DOTTED.PATH'

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """
    return []


@_boolean_hook
def pytest_autoprof_imports_default():
    """
    Whether to also auto-profile all the imports of a test module, if
    the test module itself is auto-profiled
    (equivalent to the `--prof-imports` flag of `kernprof`;
    defaults can be supplied by the `pytest_autoprof_imports_default()`
    hook)
    """
    return False


@_boolean_hook
def pytest_autoprof_tests_default():
    """
    Whether to auto-profile the test files themselves
    (equivalent to adding the test file to the `--prof-mod` flag of
    `kernprof`;
    defaults can be supplied by the `pytest_autoprof_tests_default()`
    hook)
    """
    return False


@_all_or_bool_book(
    firstresult=True,
    parser_flags='--autoprof-doctests',
    parser_kwargs=dict(
        const='all',
        metavar='all|yes|no',
        nargs='?',
        type=(
            lambda ad:
            'all' if ad.lower() in ('all', 'a') else parse_boolean(ad)
        ),
        help=_one_line("""
    Whether to auto-profile the execution of collected doctests
    (the special value (default in the no-argument form) '[a]ll'
    indicates that all traceable doctests (parsed from
    statically-defined docstrings of modules, classes, functions,
    methods, etc.), should be profiled, equivalent to the doctest
    version of `--autoprof-tests`;
    [t]ruey values indicate to only profile doctests explicitly included
    by `--autoprof-mod`;
    [f]alsy values indicate not to profile doctests;
    defaults can be supplied by the
    `pytest_autoprof_doctests_default()` hook)
        """),
    ),
)
def pytest_autoprof_doctests_default() -> Union[
    Literal['all'],
    bool,
    Annotated[str, Parsable[Literal['all']], Parsable[bool]],
]:
    """
    Return
    ------
    Default value for the extended boolean flag `--autoprof-doctests`,
    which is to be (a string parsable into) a boolean or the special
    value `'all'`;
    parsing is case-insensitive, and the following are recognized:
    - Parsed into `'all'`:
      'A', 'all'
    - Parsed into `True`:
      '1', 'T', 'True', 'Y', 'yes'
    - Parsed into `False`:
      '0', 'F', 'False', 'N', 'no'

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """
    return False


@_boolean_hook
def pytest_autoprof_rewrite_doctests_default():
    """
    Whether to also auto-profile imports and function/method definitions
    in the profiled doctests (if any; matched via `--autoprof-mod`, or
    if `--autoprof-doctests=all`) via AST rewriting
    (like regular tests, the scope of rewriting is controlled by
    `--autoprof-mod` and `--autoprof-imports`;
    defaults can be supplied by the
    `pytest_autoprof_rewrite_doctests_default()` hook)
    """
    return False


@_boolean_hook
def pytest_autoprof_subprocs_default():
    """
    Whether to also auto-profile forked/spawned Python subprocesses
    (defaults can be supplied by the
    `pytest_autoprof_subprocs_default()` hook)
    """
    return False


@_outfile_hook(
    firstresult=True,
    parser_flags='--autoprof-outfile',
    parser_kwargs=dict(
        metavar='FILENAME',
        help=_one_line("""
    Location to write the `line_profiler` output to
    (equivalent to the `--outfile` flag of `kernprof`;
    defaults can be supplied by the `pytest_autoprof_outfile_default()`
    hook;
    if not specified, it is written to
    `<root_dir> / <cache_dir> / 'pytest_autoprof.lprof'`)
        """),
    ),
)
def pytest_autoprof_outfile_default(
    config: pytest.Config,
) -> Union[pathlib.PurePath, str]:
    """
    Parameters
    ----------
    config
        `pytest.Config`

    Return
    ------
    Default value for the file path flag `--autoprof-outfile`

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """
    return _get_cache_dir(config) / 'pytest_autoprofile.lprof'


@_view_options_hook(
    firstresult=True,
    parser_flags='--autoprof-view',
    parser_kwargs=dict(
        const=True,
        metavar='yes|no|FLAGS',
        nargs='?',
        type=parse_view_options,
        help=_one_line("""
    Whether to show the profiling results (if any) as with
    `kernprof -lv`
    (alternatively, a string which is parsed as the command-line options
    for `kernprof -lv` and `python -m line_profiler`, which then causes
    the profiling results to be formatted correspondingly;
    defaults can be supplied by the
    `pytest_autoprof_view_default()` hook)
        """),
    ),
)
def pytest_autoprof_view_default() -> Union[
    bool,
    LineProfilerViewOptions,
    Annotated[str, Parsable[bool], Parsable[LineProfilerViewOptions]],
]:
    """
    Return
    ------
    Default value for the boolean flag `--autoprof-view`,
    which is to be (a string parsable into) a boolean;
    parsing is case-insensitive, and the following are recognized:
    - Parsed into `True`:
      '1', 'T', 'True', 'Y', 'yes'
    - Parsed into `False`:
      '0', 'F', 'False', 'N', 'no'
    Alternatively, the string can be of the CLI options that `kernprof`
    and `python -m line_profiler` take:
    - `-c CONFIG`/`--config=CONFIG`, `--no-config`:
      Load configuration from the provided file (or the default config
      file that ships with `line_profiler` if `--no-config`):
      if any of the following flags/flag pairs is not passed, the value
      is resolved therefrom
    - `-u UNIT`/`--unit=UNIT`:
      Set the `output_unit` argument (positive finite real number) for
      the `LineProfiler.print_stats()` call
    - `-z`/`--skip-zero`, `--no-skip-zero`:
      Whether to set `stripzeros=True` for said call
    - `-r`/`--rich`, `--no-rich`; `-t`/`--sort`, `--no-sort`;
      `-m`/`--summarize`, `--no-summarize`:
      Whether to set the synonymous arguments to `True` for said call

    Notes
    -----
    - Default values can be supplied via `conftest.py` or other plugins
      with a synonymous callable of compatible signature.
    - If none of `-c`/`--config`/`--no-config` is specified, the
      configuration is loaded from the default resolved location (see
      `line_profiler.toml_config`).
    """
    return False


@_always_or_bool_book(
    firstresult=True,
    parser_flags='--autoprof-global-profiler',
    parser_kwargs=dict(
        const='always',
        metavar='always|yes|no',
        nargs='?',
        type=(
            lambda ad:
            'always' if ad.lower() in ('always', 'a') else parse_boolean(ad)
        ),
        help=_one_line("""
    Whether to auto-profile whatever is passed to the "global" profiler
    `@line_profiler.profile`
    (the special value (default in the no-argument form) '[a]lways'
    means to always do such auto-profiling;
    otherwise, [t]ruey values indicate to only do so when the "global"
    profiler is `.enabled`,
    and [f]alsy values, not to do so at all;
    defaults can be supplied by the
    `pytest_autoprof_global_profiler_default()` hook)
        """),
    ),
)
def pytest_autoprof_global_profiler_default() -> Union[
    Literal['always'],
    bool,
    Annotated[str, Parsable[Literal['always']], Parsable[bool]],
]:
    """
    Return
    ------
    Default value for the extended boolean flag
    `--autoprof-global-profiler`, which is to be (a string parsable
    into) a boolean or the special value `'always'`;
    parsing is case-insensitive, and the following are recognized:
    - Parsed into `'always'`:
      'A', 'always'
    - Parsed into `True`:
      '1', 'T', 'True', 'Y', 'yes'
    - Parsed into `False`:
      '0', 'F', 'False', 'N', 'no'

    Notes
    -----
    Default values can be supplied via `conftest.py` or other plugins
    with a synonymous callable of compatible signature.
    """
    return False


def resolve_hooked_option(
    config: pytest.Config,
    opt_or_dest: str,
    *,
    default: Any = _ABSENT,
    add_to_config: bool = True,
    args: Optional[Sequence] = None,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:
    """
    Parameters
    ----------
    config
        `pytest.Config`
    opt_or_dest
        Option flag or destination name
    default
        Optional default when the option isn't available
    add_to_config
        Whether to add the resolved default back to `config.option`, so
        that the it doesn't need to be re-resolved the next time
    args, kwargs
        Optional arguments to the passed to the hook implementation to
        get a default

    Return
    ------
    The resolved value of the option associated with a `~~.Hook`
    """
    def to_dest(opt_or_dest: str) -> str:
        return table.get(opt_or_dest, opt_or_dest)

    try:
        value = config.getoption(opt_or_dest)
    except ValueError:  # No such option
        if default is _ABSENT:
            raise
        return default
    if value is not None:
        return value
    # Get all the flags resolving to the same destination
    table = config._opt2dest
    dest = to_dest(opt_or_dest)
    valid_hook_names: Set[Annotated[str, Identifier]] = set()
    all_hooks = Hook.hooks
    for name, hook in all_hooks.items():
        opts_and_dests = set(hook.parser_flags)
        if hook.parser_kwargs.get('dest'):
            opts_and_dests.add(hook.parser_kwargs['dest'])
        if any(to_dest(string) == dest for string in opts_and_dests):
            valid_hook_names.add(name)
    matching_name, = valid_hook_names
    hook_obj = all_hooks[matching_name]
    # Store the resolved default where appropriate
    resolved_default = hook_obj(config, *(args or ()), **(kwargs or {}))
    if resolved_default is not None and add_to_config:
        setattr(config.option, dest, resolved_default)
    return resolved_default


def _get_cache_dir(config: pytest.Config) -> pathlib.Path:
    cache_dir: Union[pathlib.PurePath, str]
    try:
        cache_dir = pathlib.Path(config.getini('cache_dir'))
    except ValueError:
        cache_dir = '.pytest_cache'
    return config.rootpath / cache_dir


########################################################################
#                        Pre-formatted warnings                        #
########################################################################


def _get_recursive_autoprof_warning_args(
    targets: Sequence[ImportPath],
) -> Tuple[
    Annotated[str, Parsable[int]],
    Literal['target', 'targets'],
    Annotated[str, Parsable[List[ImportPath]]],
    Literal['it', 'them'],
]:
    num = len(targets)
    if num == 1:
        target: Literal['target', 'targets'] = 'target'
        pronoun: Literal['it', 'them'] = 'it'
    else:
        target = 'targets'
        pronoun = 'them'
    return (
        str(num), target, ','.join(str(target) for target in targets), pronoun,
    )


OptionParsingWarning.register(
    'recursive_autoprof',
    'found {} invalid (non-module) {} ({}), moving {} to `--always-autoprof`',
    _get_recursive_autoprof_warning_args,
    '[1-9][0-9]*',
    'targets?',
    r'\w+(\.\w+)*::\w+(\.\w+)*(,\w+(\.\w+)*::\w+(\.\w+)*)*',
    '(it|them)',
)
