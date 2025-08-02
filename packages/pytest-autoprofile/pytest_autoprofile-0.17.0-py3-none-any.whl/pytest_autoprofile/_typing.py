import argparse
import dataclasses
import functools
import inspect
import keyword
import importlib
import math
import operator
import pathlib
import shlex
import types
try:
    import typing_extensions as typing
except ImportError:
    import typing  # type: ignore[no-redef]
from typing import TYPE_CHECKING

from line_profiler.toml_config import ConfigSource
from line_profiler.cli_utils import add_argument, get_cli_config


if TYPE_CHECKING:
    # `mypy` is a bit rough around the edge so import the `typing` names
    # explicitly to help it out
    from typing import (  # noqa: F401
        Dict, FrozenSet, List, Set, Tuple,
        Collection, ContextManager, Generator, Iterable, Iterator, Mapping,
        MutableSequence, Sequence,
        BinaryIO, TextIO,
        Callable, ParamSpec, Concatenate,
        DefaultDict, NamedTuple, TypedDict,
        Type, TypeAlias, TypeVar, ClassVar, Generic, Protocol,
        Annotated, Any, Self,
        Literal, Union, Optional,
        cast, get_args, overload,
    )

if hasattr(typing, '__all__'):
    __all__ = tuple(typing.__all__)
else:
    __all__ = tuple(name for name in vars(typing) if name.isidentifier())


__all__ += (
    'ChainedIdentifier',
    'Identifier',
    'ImportPath',
    'LineProfilerViewOptions',
    'Parser',
    'Parsable',
    'is_identifier',
    'is_chained_identifier',
    '__getattr__',
    '__dir__',
)


T = typing.TypeVar('T')
T_co = typing.TypeVar('T_co', covariant=True)

ChainedIdentifier = typing.NewType('ChainedIdentifier', str)
Identifier = typing.NewType('Identifier', str)


class Parsable(str, typing.Generic[T]):
    """
    Metadata-only type for use with `typing.Annotated`, indicating that
    the string should be parsable to an object of type `T` by some
    parser.
    """
    pass


class Parser(typing.Protocol, typing.Generic[T_co]):
    """
    Protocol for a callable which takes an appropriate string and parses
    it into an object of type `T`.
    """
    def __call__(
        self, string: typing.Annotated[str, Parsable[T_co]],
    ) -> T_co:
        ...


class ImportPath(typing.NamedTuple):
    """
    Specification for a path along which an item should be imported.

    Examples
    --------
    >>> ipath = ImportPath.parse('foo.bar::baz')
    >>> assert ipath.module == 'foo.bar'
    >>> assert ipath.object == 'baz'
    >>> assert str(ipath) == 'foo.bar::baz'

    >>> assert ImportPath.parse_multiple('') == []
    >>> assert ImportPath.parse_multiple('foo::bar.baz,spam') == [
    ...     ImportPath('foo', 'bar.baz'), ImportPath('spam'),
    ... ]

    >>> import importlib.abc
    >>>
    >>>
    >>> ipath = ImportPath.parse(
    ...     'importlib.abc::MetaPathFinder.invalidate_caches'
    ... )
    >>> assert ipath.import_target() is (
    ...     importlib.abc.MetaPathFinder.invalidate_caches
    ... )
    """
    module: typing.Annotated[str, ChainedIdentifier]
    object: typing.Optional[typing.Annotated[str, ChainedIdentifier]] = None

    def __str__(self) -> typing.Annotated[str, Parsable[typing.Self]]:
        return ('{0[0]}::{0[1]}' if self.object else '{0[0]}').format(self)

    def import_target(self) -> typing.Any:
        module = importlib.import_module(self.module)
        if not self.object:
            return module
        return operator.attrgetter(self.object)(module)

    @classmethod
    def parse(
        cls, string: typing.Annotated[str, Parsable[typing.Self]],
    ) -> typing.Self:
        obj: typing.Union[str, None]
        module, _, obj = string.partition('::')
        if not is_chained_identifier(module):
            raise ValueError(
                'expected the format '
                "'MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH]', "
                f'got {string!r}'
            )
        if not obj:
            obj = None
        elif not is_chained_identifier(obj):
            raise ValueError(
                'expected the format '
                "'MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH]', "
                f'got {string!r}'
            )
        return cls(module, obj)

    @classmethod
    def parse_multiple(
        cls,
        string: typing.Annotated[str, Parsable[typing.List[typing.Self]]],
        sep: str = ',',
    ) -> typing.List[typing.Self]:
        if not string:
            return []
        return [cls.parse(substring) for substring in string.split(sep)]


@dataclasses.dataclass
class LineProfilerViewOptions:
    """
    Options for viewing the profiling results with
    `line_profiler.LineProfiler.print_stats()`.
    """
    config: typing.Optional[
        typing.Union[pathlib.PurePath, typing.Literal[False]]
    ] = None
    output_unit: typing.Optional[float] = None
    stripzeros: typing.Optional[bool] = None
    rich: typing.Optional[bool] = None
    sort: typing.Optional[bool] = None
    summarize: typing.Optional[bool] = None

    def __post_init__(self) -> None:
        # Consolidate the path to the config
        config: ConfigSource = get_cli_config('cli', self.config)
        # FIXME: see `line_profiler` PR #367
        self.config = config.path  # type: ignore[attr-defined]
        # Load values
        translations = {'output_unit': 'unit', 'stripzeros': 'skip_zero'}
        for attr, value in dataclasses.asdict(self).items():
            if value is None:
                key = translations.get(attr, attr)
                setattr(self, attr, config.conf_dict[key])
        # Check `.output_unit`
        unit = self.output_unit
        if unit is None:
            return
        if math.isfinite(unit) and unit > 0:
            return
        raise ValueError(
            f'.output_unit = {unit!r}: expected a finite real number',
        )

    @classmethod
    def parse(
        cls,
        args: typing.Union[
            typing.Annotated[str, Parsable[typing.Self]],
            typing.Sequence[typing.Annotated[str, Parsable[typing.Self]]],
        ],
    ) -> typing.Self:
        """
        Example
        -------
        Basic use:

        >>> Options = LineProfilerViewOptions
        >>> assert Options.parse('') == Options()
        >>> assert Options.parse('-r') == Options(rich=True)
        >>> assert Options.parse('-u.125 -mt') == Options(
        ...     output_unit=.125, summarize=True, sort=True,
        ... )
        >>> Options.parse('-r --foo')
        Traceback (most recent call last):
          ...
        ValueError: unrecognized arguments: --foo

        Extended booleans:

        >>> assert Options.parse('--rich=Y') == Options(rich=True)
        >>> assert Options.parse('--rich=no') == Options(rich=False)
        """
        def valid_config(filename: str) -> pathlib.Path:
            # FIXME: see `line_profiler` PR #367
            return (
                ConfigSource.from_config(filename)
                .path  # type: ignore[attr-defined]
            )

        parser = _ArgParser(add_help=False, exit_on_error=False)
        # FIXME: see `line_profiler` PR #367
        add = functools.partial(  # type: ignore[arg-type,type-var]
            add_argument, parser,
        )
        add('-c', '--config', type=valid_config)
        add('--no-config', action='store_const', const=False, dest='config')
        add('-u', '--unit', dest='output_unit', type=float)
        add('-z', '--skip-zero', action='store_true', dest='stripzeros')
        add('-r', '--rich', action='store_true')
        add('-t', '--sort', action='store_true')
        add('-m', '--summarize', action='store_true')
        if isinstance(args, str):
            args = shlex.split(args)
        if not isinstance(args, typing.Sequence):
            raise TypeError(f'args = {args!r}: expected a sequence of strings')
        try:
            # Note: raising instead of quitting in
            # `ArgumentParser.parse_args()` was only added in v3.13.0b3,
            # so use `.parse_known_args()` instead to be
            # backwards-compatible
            parsed, unparsed = parser.parse_known_args(args)
            if unparsed:
                raise ValueError(
                    'unrecognized arguments: ' + shlex.join(unparsed),
                )
            return cls(**vars(parsed))
        except argparse.ArgumentError as e:
            raise ValueError(e.message) from None


class _DeferredAttributes:
    """
    Defer item access to another module.

    Notes
    -----
    For the sake of the static type checker, it is recommended that
    static imports for the used attributes be done when
    `typing.TYPE_CHECKING` is true.
    """
    modules: typing.List[types.ModuleType]
    namespace: typing.MutableMapping[
        typing.Annotated[str, Identifier], typing.Any
    ]

    def __init__(
        self, module: types.ModuleType, *modules: types.ModuleType,
        namespace: typing.Optional[
            typing.MutableMapping[
                typing.Annotated[str, Identifier], typing.Any
            ]
        ] = None,
    ) -> None:
        self.modules = [module, *modules]
        if namespace is None:
            namespace = {}
        self.namespace = namespace

    def dir(self) -> typing.List[typing.Annotated[str, Identifier]]:
        return list(set(self.namespace).union(*(dir(m) for m in self.modules)))

    def getattr(self, attr: typing.Annotated[str, Identifier]) -> typing.Any:
        xc: typing.Union[Exception, None] = None
        for module in self.modules:
            try:
                result = getattr(module, attr)
            except Exception as e:
                e.__cause__ = xc
                xc = e
            else:
                return self.namespace.setdefault(attr, result)
        if TYPE_CHECKING:
            assert xc is not None
        raise xc

    @classmethod
    def install(
        cls,
        namespace: typing.MutableMapping[
            typing.Annotated[str, Identifier], typing.Any
        ],
        module: types.ModuleType, *modules: types.ModuleType,
    ) -> typing.Tuple[
        typing.Callable[[], typing.List[typing.Annotated[str, Identifier]]],
        typing.Callable[[typing.Annotated[str, Identifier]], typing.Any],
    ]:
        """
        Create an instance and return its `.dir()` and `.getattr()`
        methods in a 2-tuple.

        Example
        -------
        >>> import types
        >>> import typing
        >>>
        >>>
        >>> install = _DeferredAttributes.install
        >>> my_module = types.ModuleType('my_module')
        >>> namespace = vars(my_module)
        >>> my_module.__dir__, my_module.__getattr__ = install(
        ...     namespace, types, typing,
        ... )
        >>> attrs = {'SimpleNamespace', 'get_type_hints'}
        >>> assert not attrs.intersection(namespace)
        >>> assert attrs < set(dir(my_module))
        >>> assert my_module.SimpleNamespace is types.SimpleNamespace
        >>> assert namespace['SimpleNamespace'] is types.SimpleNamespace
        >>> assert my_module.get_type_hints is typing.get_type_hints
        >>> assert namespace['get_type_hints'] is typing.get_type_hints
        """
        instance = cls(module, *modules, namespace=namespace)
        result = instance.dir, instance.getattr
        namespace['__dir__'], namespace['__getattr__'] = result
        return result


class _CatchExitArgParser(argparse.ArgumentParser):
    """
    Emulation of `ArgumentParser.exit_on_error` (Python 3.9+).
    """
    def __init__(self, *args, exit_on_error: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_on_error = exit_on_error

    def error(self, message: str) -> typing.NoReturn:
        if self.exit_on_error:
            super().error(message)
        raise argparse.ArgumentError(None, message)


_ArgParser: typing.Type[argparse.ArgumentParser]
if 'exit_on_error' in inspect.signature(argparse.ArgumentParser).parameters:
    _ArgParser = argparse.ArgumentParser
else:  # Python < 3.9
    _ArgParser = _CatchExitArgParser


def _is_identifier(s: str) -> bool:
    return s.isidentifier() and not keyword.iskeyword(s)


def is_chained_identifier(s: typing.Any) -> typing.TypeIs[ChainedIdentifier]:
    """
    Example
    -------
    >>> is_chained_identifier(object())
    False
    >>> is_chained_identifier(1)
    False
    >>> is_chained_identifier('')
    False
    >>> is_chained_identifier('a')
    True
    >>> is_chained_identifier('0a')
    False
    >>> is_chained_identifier('a.b')
    True
    """
    return (
        isinstance(s, str) and
        bool(s) and
        all(_is_identifier(substring) for substring in s.split('.'))
    )


def is_identifier(s: typing.Any) -> typing.TypeIs[Identifier]:
    """
    Example
    -------
    >>> is_identifier(object())
    False
    >>> is_identifier(1)
    False
    >>> is_identifier('')
    False
    >>> is_identifier('a')
    True
    >>> is_identifier('0a')
    False
    >>> is_identifier('a.b')
    False
    """
    return isinstance(s, str) and _is_identifier(s)


__dir__, __getattr__ = _DeferredAttributes.install(globals(), typing)
