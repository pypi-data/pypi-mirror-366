"""
Define a patched `line_profiler.LineProfiler`.
"""
import abc
import functools
import inspect
import pathlib
import pickle
import types
try:
    from builtins import ExceptionGroup
except ImportError:  # Python < 3.11
    from exceptiongroup import ExceptionGroup  # type: ignore[no-redef]

import pytest
from line_profiler import line_profiler, profiler_mixin
from line_profiler._line_profiler import LineStats
from line_profiler.explicit_profiler import GlobalProfiler
from line_profiler.scoping_policy import ScopingPolicy

from . import _warnings as warnings
from ._typing import (
    TYPE_CHECKING,
    DefaultDict, Dict, FrozenSet, List, Set, Tuple,
    Mapping, Sequence,
    Callable, ParamSpec,
    BinaryIO,
    Type, TypeVar, ClassVar, TypeIs, Protocol,
    Annotated, Any, Self,
    Literal, Union, Optional,
    overload,
    Parsable, ChainedIdentifier, Identifier, ImportPath,
)
from .option_hooks import resolve_hooked_option
from .utils import get_config, LazyImporter


if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811
    from .importers import AutoProfStash


__all__ = ('LineProfiler',)

# These are types returned as-is from `.wrap_callable()` and
# `.__call__()`, and cannot be parametrized
UnparametrizedFunctionLike = TypeVar(
    'UnparametrizedFunctionLike', types.FunctionType, types.MethodType,
)
# These are C-level callables that the base class just spits out
# unmodified
CLevelCallable = TypeVar(
    'CLevelCallable',
    types.BuiltinFunctionType, types.BuiltinMethodType,
    types.ClassMethodDescriptorType, types.MethodDescriptorType,
    types.MethodWrapperType, types.WrapperDescriptorType,
)
# Objects of corresponding types are returned from these callable-like
# objects
FunctionLike = TypeVar(
    'FunctionLike',
    bound=Union[
        functools.partial, functools.partialmethod,
        classmethod, staticmethod,
        type,
        # From `UnparametrizedFunctionLike`
        types.FunctionType, types.MethodType,
        # From `CLevelCallable`
        types.BuiltinFunctionType, types.BuiltinMethodType,
        types.ClassMethodDescriptorType, types.MethodDescriptorType,
        types.MethodWrapperType, types.WrapperDescriptorType,
    ],
)
ExtendedPropertyLike = TypeVar(
    'ExtendedPropertyLike',
    bound=Union['PropertyLike', functools.cached_property],
)

CallableLike = Union[FunctionLike, ExtendedPropertyLike, Callable]
OutputCallableLike = Union[
    FunctionLike, ExtendedPropertyLike, types.FunctionType,
]

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
K = TypeVar('K')
P = TypeVar('P', bound='PropertyLike')
PS = ParamSpec('PS')

TimingKey = Tuple[str, int, str]
TimingEntries = Sequence[Tuple[int, int, int]]
MutableTimingEntries = List[Tuple[int, int, int]]
Timings = Mapping[TimingKey, TimingEntries]
TimingsDict = Dict[TimingKey, MutableTimingEntries]
StatsLike = Union[
    LineStats, '_FrozenLineStats', '_LineStatsCollator', str, pathlib.PurePath,
]
DoctestRegistry = DefaultDict[
    Union[str, None],  # Test filename
    Set[Annotated[str, ChainedIdentifier]]  # Test name
]

DERIVED_FUNCTION_LIKES = (
    types.MethodType, functools.partial, functools.partialmethod,
)

THIS_PACKAGE = (lambda: None).__module__.rpartition('.')[0]

# We have a forward reference to `~.importers.AutoProfStash`;
# lazy-import it

__dir__, __getattr__ = LazyImporter.install(
    globals(), AutoProfStash='importers::AutoProfStash',
)


class PropertyLike(Protocol):
    fget: Union[Callable[[Any], Any], None]
    fset: Union[Callable[[Any, Any], None], None]
    fdel: Union[Callable[[Any], None], None]
    __isabstractmethod__: bool

    def __init__(
        self,
        fget: Optional[Callable[[Any], Any]] = None,
        fset: Optional[Callable[[Any, Any], None]] = None,
        fdel: Optional[Callable[[Any], None]] = None,
    ) -> None:
        ...

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> Self:
        ...

    @overload
    def __get__(self, instance: T, owner: Optional[Type[T]] = None) -> Any:
        ...

    def __get__(
        self, instance: Union[T, None], owner: Optional[Type[T]] = None,
    ) -> Union[Any, Self]:
        if instance is None:
            return self
        assert self.fget is not None
        return self.fget(instance)

    def __set__(self, instance: Any, value: Any) -> None:
        assert self.fset is not None
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        assert self.fdel is not None
        self.fdel(instance)


class _LineStatsBase(abc.ABC):
    def to_vanilla_line_stats(self) -> LineStats:
        result = LineStats(
            {key: list(entries) for key, entries in self.timings.items()},
            self.unit,
        )
        inst_vars = getattr(self, '__dict__', {})
        try:
            vars(result).update(inst_vars)
        except Exception:
            pass
        return result

    @property
    @abc.abstractmethod
    def timings(self) -> Timings:
        ...

    @property
    @abc.abstractmethod
    def unit(self) -> float:
        ...


class _FrozenLineStats(_LineStatsBase):
    __slots__ = ('_timings', '_unit')

    def __init__(self, timings: Timings, unit: float) -> None:
        self._timings = types.MappingProxyType({
            key: tuple(entries)
            for key, entries in timings.items()
        })
        self._unit = unit

    @classmethod
    def from_vanilla_line_stats(
        cls, stats: Union[LineStats, '_FrozenLineStats', '_LineStatsCollator'],
    ) -> Self:
        instance = cls(stats.timings, stats.unit)
        try:
            inst_vars = vars(stats)
        except Exception:
            inst_vars = {}
        if inst_vars:
            vars(instance).update(inst_vars)
        return instance

    @property
    def timings(self) -> Timings:
        return self._timings

    @property
    def unit(self) -> float:
        return self._unit


class _LineStatsCollator(_LineStatsBase):
    """
    Example
    -------
    >>> from line_profiler._line_profiler import LineStats
    >>>
    >>>
    >>> stats1 = LineStats(
    ...     {
    ...         ('spam', 1, 'foo'): [(2, 20, 500), (3, 500, 12500)],
    ...         ('eggs', 5, 'foobar'): [(10, 100, 4000)],
    ...     },
    ...     1 / 256,
    ... )
    >>> stats2 = LineStats(
    ...     {
    ...         ('spam', 1, 'foo'): [(2, 10, 100), (4, 400, 20000)],
    ...         ('spam', 30, 'bar'): [(32, 40, 3000)],
    ...     },
    ...     1 / 512,
    ... )
    >>> collator = _LineStatsCollator(stats1, stats2)
    >>> assert collator.unit == 1 / 256
    >>> assert collator.timings == {
    ...     ('spam', 1, 'foo'): [
    ...         (2, 30, 550), (3, 500, 12500), (4, 400, 10000),
    ...     ],
    ...     ('spam', 30, 'bar'): [(32, 40, 1500)],
    ...     ('eggs', 5, 'foobar'): [(10, 100, 4000)],
    ... }
    """
    all_stats: List[LineStats]

    def __init__(self, stats: StatsLike, *more_stats: StatsLike) -> None:
        self.all_stats = []
        add = self.all_stats.append
        for stats in [stats, *more_stats]:
            if isinstance(stats, LineStats):
                add(stats)
            elif callable(getattr(stats, 'to_vanilla_line_stats', None)):
                add(stats.to_vanilla_line_stats())  # type: ignore[union-attr]
            else:
                add(line_profiler.load_stats(stats))
        self.collate()

    def collate(self) -> None:
        all_stats = self.all_stats
        if len(all_stats) == 1:
            stats, = all_stats
            self._unit = stats.unit
            self._timings = {
                label: entries.copy()
                for label, entries in stats.timings.items()
            }
            return
        unit = max(stats.unit for stats in all_stats)
        timings: Dict[TimingKey, Dict[int, Tuple[int, int]]] = {}
        for stats in all_stats:
            factor = stats.unit / unit
            for label, entries in stats.timings.items():
                entries_dict = timings.setdefault(label, {})
                for lineno, nhits, time in entries:
                    old_nhits, old_time = entries_dict.get(lineno, (0, 0))
                    entries_dict[lineno] = (
                        old_nhits + nhits, old_time + int(factor * time),
                    )
        self._unit = unit
        self._timings = {
            label: [
                (lineno, nhits, time)
                for lineno, (nhits, time) in sorted(entries_dict.items())
            ]
            for label, entries_dict in timings.items()
        }

    def show(self, **kwargs) -> None:
        line_profiler.show_text(self.timings, self.unit, **kwargs)

    def dump(self, file: Union[BinaryIO, str, pathlib.PurePath]) -> None:
        if not callable(getattr(file, 'write', None)):
            if TYPE_CHECKING:
                assert isinstance(file, (str, pathlib.PurePath))
            with open(file, mode='wb') as fobj:
                return self.dump(fobj)
        if TYPE_CHECKING:
            assert isinstance(file, BinaryIO)
        pickle.dump(
            LineStats(self.timings, self.unit), file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    @property
    def timings(self) -> Timings:
        return self._timings

    @property
    def unit(self) -> float:
        return self._unit


def _is_property_like(obj: Any) -> TypeIs[PropertyLike]:
    if isinstance(obj, property):
        return True
    for attr in '__get__', '__set__', '__delete__':
        try:
            if not callable(getattr(type(obj), attr)):
                return False
        except AttributeError:
            return False
    for attr in 'fget', 'fset', 'fdel':
        try:
            value = getattr(obj, attr)
        except AttributeError:
            return False
        if value is None:
            continue
        if not callable(obj):
            return False
    return True


def _import(*args, **kwargs) -> Any:
    return ImportPath(*args, **kwargs).import_target()


class LineProfiler(line_profiler.LineProfiler):
    """
    `line_profiler.line_profiler.LineProfiler` subclass with patches
    like:
    - Fixed wrapping of class and static methods
    - Extra bookkeeping to prevent double-wrapping
    - Extra bookkeeping for profiling doctests
    """
    def __init__(
        self, *args,
        config: Optional[pytest.Config] = None,
        tee_global_prof: Optional[Union[bool, Literal['always']]] = None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.config = config
        self.tee_global_prof = tee_global_prof
        self.profiled_doctests = DefaultDict(set)
        self.non_profiled_doctests = DefaultDict(set)
        self.omitted_doctests = DefaultDict(set)
        self._patches = pytest.MonkeyPatch()
        self._cleanup_callbacks = []
        # Basic cleanup callbacks
        self._register_cleanup_callback(self.unadd_wrappers)
        self._register_cleanup_callback(self.purge_count)

    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        cached_property = functools.cached_property
        cls._cached_properties = frozenset(
            name for name, member in inspect.getmembers(cls)
            if isinstance(member, cached_property)
        )

    def __repr__(self) -> str:
        attrs = ', '.join(
            f'.{attr}={value!r}' for attr, value in [
                ('object_count', self.object_count),
                ('enable_count', self.enable_count),
                ('autoprof_doctests', self.autoprof_doctests),
            ]
            if value
        )
        return '<{} object{} at {:#x}>'.format(
            type(self).__qualname__, f' ({attrs})' if attrs else '', id(self),
        )

    # Add cleanup

    def __del__(self) -> None:
        try:
            super_impl = super().__del__
        except AttributeError:
            super_impl = None
        try:
            self.cleanup()
        finally:
            if super_impl is not None:
                super_impl()

    def cleanup(self) -> None:
        """
        Handle cleanup after using the profiler:
        - Purge all `.enable_count`;
        - Revert all wrappers installed by the `.add_class()`,
          `.add_module()`, and `.add_imported_function_or_module()`
          methods; and
        - If `.autoprof_doctests` is true, `.uninstall()` the
          appropriate handler to restore `_pytest.doctest.RUNNER_CLASS`
          (or the corresponding entity for other doctest backends).
        """
        xcs: List[Tuple[functools.partial, Exception]] = []
        callbacks = self._cleanup_callbacks
        while callbacks:
            callback = callbacks.pop()
            try:
                callback()
            except Exception as e:
                xcs.append((callback, e))
        if not xcs:
            return
        raise ExceptionGroup(
            f'{len(xcs)} cleanup callback(s) resulted in errors: {xcs!r}',
            [xc for _, xc in xcs],
        )

    # Patch callable wrapping

    # --------------- Start: overloads (`.__call__()`) --------------- #

    @overload  # type: ignore[override]
    def __call__(  # type: ignore[overload-overlap]
        self, func: CLevelCallable,
    ) -> CLevelCallable:
        ...

    @overload
    def __call__(self, func: P) -> P:
        ...

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, func: UnparametrizedFunctionLike,
    ) -> UnparametrizedFunctionLike:
        ...

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, func: Type[T],
    ) -> Type[T]:
        ...

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, func: 'functools.partial[T]',
    ) -> 'functools.partial[T]':
        ...

    @overload
    def __call__(
        self, func: 'functools.partialmethod[T]',
    ) -> 'functools.partialmethod[T]':
        ...

    @overload
    def __call__(
        self, func: 'functools.cached_property[T_co]',
    ) -> 'functools.cached_property[T_co]':
        ...

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, func: 'staticmethod[PS, T_co]',
    ) -> 'staticmethod[PS, T_co]':
        ...

    @overload
    def __call__(
        self, func: 'classmethod[type[T], PS, T_co]',
    ) -> 'classmethod[type[T], PS, T_co]':
        ...

    @overload
    def __call__(self, func: Callable) -> types.FunctionType:
        ...

    # ---------------- End: overloads (`.__call__()`) ---------------- #

    def __call__(self, func: CallableLike) -> OutputCallableLike:
        add_func = self.add_callable
        dispatch = self.wrap_callable
        warn = warnings.warn
        result: OutputCallableLike
        if isinstance(func, DERIVED_FUNCTION_LIKES):
            # If its a 'derived' function-like (e.g. bound method or
            # partial object), return a wrapper even if we're already
            # profiling the underlying object, so that different
            # wrappers can all contribute to the profiling data
            add_func(func)
            result = dispatch(func)
        elif add_func(func):
            result = dispatch(func)
        else:
            return func
        if type(result) is not type(func):
            msg = (
                'object {0!r} is profiled, '
                'but it is of type `{1.__module__}.{1.__qualname__}` and now '
                'replaced with a `{2.__module__}.{2.__qualname__}`, '
                'which may have unintended consequences'
            ).format(func, type(func), type(result))
            warn(msg, UserWarning, 2)
        return result

    # ------------ Start: overloads (`.wrap_callable()`) ------------- #

    @overload  # type: ignore[override]
    def wrap_callable(  # type: ignore[overload-overlap]
        self, func: CLevelCallable,
    ) -> CLevelCallable:
        ...

    @overload
    def wrap_callable(self, func: P) -> P:
        ...

    @overload
    def wrap_callable(  # type: ignore[overload-overlap]
        self, func: UnparametrizedFunctionLike,
    ) -> UnparametrizedFunctionLike:
        ...

    @overload
    def wrap_callable(  # type: ignore[overload-overlap]
        self, func: Type[T],
    ) -> Type[T]:
        ...

    @overload
    def wrap_callable(  # type: ignore[overload-overlap]
        self, func: 'functools.partial[T]',
    ) -> 'functools.partial[T]':
        ...

    @overload
    def wrap_callable(
        self, func: 'functools.partialmethod[T]',
    ) -> 'functools.partialmethod[T]':
        ...

    @overload
    def wrap_callable(
        self, func: 'functools.cached_property[T_co]',
    ) -> 'functools.cached_property[T_co]':
        ...

    @overload
    def wrap_callable(  # type: ignore[overload-overlap]
        self, func: 'staticmethod[PS, T_co]',
    ) -> 'staticmethod[PS, T_co]':
        ...

    @overload
    def wrap_callable(
        self, func: 'classmethod[type[T], PS, T_co]',
    ) -> 'classmethod[type[T], PS, T_co]':
        ...

    @overload
    def wrap_callable(self, func: Callable) -> types.FunctionType:
        ...

    # ------------- End: overloads (`.wrap_callable()`) -------------- #

    def wrap_callable(self, func: CallableLike) -> OutputCallableLike:
        return self._call_super_with_extended_prop_check(
            self, 'wrap_callable', func,
        )

    def wrap_property(self, func: P) -> P:
        if callable(getattr(func, 'replace', None)):
            dispatch = self.wrap_callable
            subfuncs: Dict[
                Annotated[str, Identifier], Union[Callable, None]
            ] = {
                name: None if subfunc is None else dispatch(subfunc)
                for name, subfunc in [
                    ('fget', func.fget),
                    ('fset', func.fset),
                    ('fdel', func.fdel),
                ]
            }
            return func.replace(**{  # type: ignore[attr-defined]
                name: subfunc for name, subfunc in subfuncs.items()
                if subfunc is not None
            })
        return super().wrap_property(  # type: ignore[return-value]
            func,  # type: ignore[arg-type]
        )

    # Patch the profiling of imports

    @overload
    def add_imported_function_or_module(
        self, item: Union[type, types.ModuleType, CallableLike], *,
        silent: Literal[True] = True, **kwargs
    ) -> None:
        ...

    @overload
    def add_imported_function_or_module(
        self, item: Union[type, types.ModuleType, CallableLike], *,
        silent: Literal[False], **kwargs
    ) -> int:
        ...

    def add_imported_function_or_module(
        self, item: Union[type, types.ModuleType, CallableLike], *,
        silent: bool = True, **kwargs
    ) -> Union[int, None]:
        """
        Patch for `line_profiler.autoprofile.line_profiler_utils
        .add_imported_function_or_module()`.

        Parameters
        ----------
        item
            Module, class, function, property, etc. to profile
        silent
            Whether to suppress the item count and return `None` instead
        **kwargs
            Passed to `.add_class()` and `.add_module()`

        Return
        ------
        silent = False
            Number of items added
        silent = True
            None

        Notes
        -----
        - Since this method may increment the `.enable_count` of the
          profiler object, one should take care to `.purge_count()`
          after the object's lifetime.
        - The previous parameters `descend` and `match_scope` are now
          deprecated;
          use `scoping_policy` (which is consistent with upstream
          (`line_profiler`)) instead.
        """
        kwargs = self._regularize_scoping_policy(**kwargs)
        if isinstance(item, type):
            result = self.add_class(item, **kwargs)
        elif isinstance(item, types.ModuleType):
            result = self.add_module(item, **kwargs)
        else:
            try:
                result = self.add_callable(item)
            except TypeError:
                result = 0
        if result:
            self.enable_by_count()
        return None if silent else result

    def add_function(self, func: types.FunctionType) -> int:
        if id(func) in self._function_ids:
            return 0
        with warnings.catch_warnings():
            msg = 'Could not extract a code object'
            warnings.filterwarnings('error', msg)
            try:
                super().add_function(func)
            except UserWarning as e:
                message = str(e.args[0])
                if msg in message:
                    warnings.filterwarnings('once', msg)
                    warnings.warn(message, UserWarning, 2)
                    return 0
                raise
        self._invalidate_caches()
        return 1

    def add_module(
        self, mod: types.ModuleType, *, wrap: bool = True, **kwargs
    ) -> int:
        kwargs = self._regularize_scoping_policy(wrap=wrap, **kwargs)
        return super().add_module(mod, **kwargs)

    def add_class(self, cls: type, *, wrap: bool = True, **kwargs) -> int:
        kwargs = self._regularize_scoping_policy(wrap=wrap, **kwargs)
        return super().add_class(cls, **kwargs)

    def unadd_wrappers(self) -> None:
        """
        Revert all the replacements of callable-likes in class and
        module namespaces made by the `.add_class()`, `.add_module()`,
        and `.add_imported_function_or_module()` methods.
        """
        self._patches.undo()

    @staticmethod
    def _regularize_scoping_policy(
        *,
        descend: Optional[bool] = None,
        match_scope: Optional[Annotated[str, Parsable[ScopingPolicy]]] = None,
        **kwargs
    ) -> Dict[Annotated[str, Identifier], Any]:
        """
        Backward-compatible preprocessing to convert the deprecated
        parameters `descend` and `match_scope` into `scoping_policy`.
        """
        if kwargs.get('scoping_policy') is None:
            scoping_policy = ScopingPolicy.to_policies(match_scope)
            if descend in (False,):
                # FIXME: see `line_profiler` PR #367
                scoping_policy['module'] = (
                    ScopingPolicy.EXACT  # type: ignore[attr-defined]
                )
            kwargs['scoping_policy'] = scoping_policy
        elif (match_scope is not None or descend):
            msg = (
                f'match_scope = {match_scope!r}, '
                f'scoping_policy = {kwargs["scoping_policy"]!r}: '
                '`match_scope` and `descend` are deprecated; '
                'use the `scoping_policy` parameter instead'
            )
            if descend:
                msg = f'descend = {descend!r}, {msg}'
            warnings.warn(msg, DeprecationWarning, 3)
        return kwargs

    @classmethod
    @functools.wraps(inspect.getattr_static(
        line_profiler.LineProfiler, '_get_underlying_functions',
    ))
    def _get_underlying_functions(cls, *args, **kwargs):
        """
        Patch `line_profiler._get_underlying_functions()` so that when
        it does a `line_profiler.profiler_mixin.is_property()` check it
        is replaced by `_is_property_like()`.
        """
        return cls._call_super_with_extended_prop_check(
            cls, '_get_underlying_functions', *args, **kwargs,
        )

    @functools.wraps(line_profiler.LineProfiler._wrap_namespace_members)
    def _wrap_namespace_members(self, *args, **kwargs):
        """
        Patch `line_profiler.LineProfiler._wrap_namespace_members()` so
        that when it `setattr()` in a namespace, those changes are done
        with `self._patches.setattr(raising=False)`, and can thus be
        rerolled by `self.unadd_wrappers()`.
        """
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                profiler_mixin,
                'setattr',
                functools.partial(self._patches.setattr, raising=False),
                raising=False,
            )
            return super()._wrap_namespace_members(*args, **kwargs)

    # Summary methods

    def get_stats(self, *, refresh_cache: bool = True) -> LineStats:
        """
        Massage timing info from doctests (if any) so that they are (as
        far as possible) merged with the regular timing info.
        The additional `refresh_cache` argument controls whether to use
        the cached value if available.
        """
        if refresh_cache:
            vars(self).pop(  # type: ignore[attr-defined]
                '_cached_stats', None,
            )
        return self._cached_stats.to_vanilla_line_stats()

    def dump_stats(
        self, filename: Union[str, pathlib.PurePath], *,
        refresh_cache: bool = True,
    ) -> None:
        """
        Dump the timing info into `filename`;
        the additional `refresh_cache` argument controls whether to use
        the cached value if available.
        """
        self._call_super_with_cached_stats(
            'dump_stats', refresh_cache, filename,
        )

    def print_stats(self, *args, refresh_cache: bool = True, **kwargs) -> None:
        self._call_super_with_cached_stats(
            'print_stats', refresh_cache, *args, **kwargs,
        )

    # Usage

    def install(self) -> None:
        """
        Side effects
        ------------
        - Instance installed to `@pytest_autoprofile.profile`
        - If `.tee_global_prof` is true (or 'always'), also overwrite
          `line_profiler.explicit_profiler.GlobalProfiler.__call__()`
          (the type of `@line_profiler.profile`) so that profiling data
          it receives is "teed" to this instance
        - If `.autoprof_doctests` is true, also `.install()` the
          appropriate handler, overriding `_pytest.doctest.RUNNER_CLASS`
          (or the corresponding entity for other doctest backends) with
          it
        """
        if self.tee_global_prof:
            self._setup_global_prof()
        self._patches.setattr(
            _import(THIS_PACKAGE), 'profile', self, raising=False,
        )
        if self.autoprof_doctests:
            handler_factory = _import(
                THIS_PACKAGE + '._doctest', 'get_doctest_handler_class',
            )
            DoctestHandler = handler_factory(self.config, self.stash)
            DoctestHandler.install()
            self._register_cleanup_callback(DoctestHandler.uninstall)

    uninstall = cleanup

    def purge_count(self) -> None:
        """
        Disable the profiler fully and purge all of `.enable_count`.

        Notes
        -----
        - Due to the `.enable_by_count()` in
          `.add_imported_function_or_module()`, we may have leftover
          enable counts by the time profiling is done, so we take care
          of that here.
        - If the object is replaced when it still has outstanding
          enable counts, it may cause problems for the replacement
          profilier due to how it hasn't vacated its reserved tool ID
          with `sys.monitoring`.
        """
        for _ in range(self.enable_count):
            self.disable_by_count()

    # Helper methods

    @classmethod
    def from_pytest_args(
        cls, pytest_args: Sequence[str] = (), /, *args, **kwargs
    ) -> Self:
        return cls(*args, config=get_config(pytest_args), **kwargs)

    def _setup_global_prof(self) -> None:
        vanilla_call = GlobalProfiler.__call__

        @functools.wraps(vanilla_call)
        def call(gp, *args, **kwargs):
            result = vanilla_call(gp, *args, **kwargs)
            if gp.enabled or self.tee_global_prof == 'always':
                return self(result)
            return result

        self._patches.setattr(GlobalProfiler, '__call__', call)

    def _register_cleanup_callback(
        self, func: Callable[PS, None], *args: PS.args, **kwargs: PS.kwargs
    ) -> None:
        if args or kwargs:
            callback = functools.partial(func, *args, **kwargs)
        else:
            callback = functools.partial(func)
        self._cleanup_callbacks.append(callback)

    def _split_doctest_timings(
        self, timings: Timings,
    ) -> Tuple[TimingsDict, TimingsDict]:
        regular: TimingsDict = {}
        doctests: TimingsDict = {}
        parse_name = (
            self.stash.DoctestHandler  # type: ignore[union-attr]
            .parse_code_object_name  # type: ignore[union-attr]
        )
        for (filename, lineno, func_name), entries in timings.items():
            try:
                fields = parse_name(func_name)
            except ValueError:
                regular[filename, lineno, func_name] = list(entries)
                continue
            doctests.setdefault(
                (fields.filename, fields.lineno, fields.test), [],
            ).extend(entries)
        for entries in doctests.values():
            entries.sort()
        return regular, doctests

    def _call_super_with_cached_stats(
        self, method: Annotated[str, Identifier], refresh_cache: bool, /,
        *args, **kwargs
    ) -> Any:
        """
        Call the `super()` implementation of `method` which uses
        `self.get_stats()`, monkey-patching it so that we can optionally
        preserve the cached value.
        """
        inst_dict = vars(self)
        caller = functools.partial(getattr(super(), method), *args, **kwargs)
        if refresh_cache:
            # No need for the override since it's the default anyway
            return caller()
        with pytest.MonkeyPatch.context() as mp:
            get_stats = functools.partial(
                types.MethodType(type(self).get_stats, self),
                refresh_cache=False,
            )
            mp.setitem(inst_dict, 'get_stats', get_stats)
            return caller()

    @staticmethod
    def _call_super_with_extended_prop_check(
        inst_or_class: Union['LineProfiler', Type['LineProfiler']],
        method: Annotated[str, Identifier], /,
        *args, **kwargs
    ) -> Any:
        """
        Call the `super()` implementation of `method`, monkey-patching
        `line_profiler.profiler_mixin.is_property()` with
        `_is_property_like()`.
        """
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(profiler_mixin, 'is_property', _is_property_like)
            impl = getattr(super(LineProfiler, inst_or_class), method)
            return impl(*args, **kwargs)

    def _invalidate_caches(self) -> None:
        remove_cache = self.__dict__.pop
        for name in self._cached_properties:
            remove_cache(name, None)

    # Various attributes and descriptors

    @functools.cached_property
    def _function_ids(self) -> FrozenSet[int]:
        return frozenset(id(f) for f in self.functions)

    @functools.cached_property
    def _cached_stats(self) -> _FrozenLineStats:
        stats = super().get_stats()
        if not self.autoprof_doctests:
            return _FrozenLineStats.from_vanilla_line_stats(stats)
        # Massage doctest timing data into the regular ones
        regular_timings, doctest_timings = (
            self._split_doctest_timings(stats.timings)
        )
        aggregated_timings: DefaultDict[
            TimingKey, MutableTimingEntries
        ] = DefaultDict(list, regular_timings)
        Locator = _import(THIS_PACKAGE + '._doctest', 'DocstringLocator')
        Locator.cache_clear()
        locate = functools.partial(
            Locator.locate_docstring, refresh_cache=False,
        )
        for filename, lineno, test_name in set(doctest_timings):
            try:
                loc = locate(filename, lineno=lineno, test_name=test_name)
            except Exception:
                self.omitted_doctests[filename].add(test_name)
                continue
            self.profiled_doctests[filename].add(test_name)
            regular_key = (
                filename, loc.host_lineno, test_name.rpartition('.')[-1]
            )
            # Merge the timing info
            existing = aggregated_timings[regular_key]
            entries = doctest_timings.pop((filename, lineno, test_name))
            if existing:
                existing.extend(entries)
                existing.sort()
            else:
                existing[:] = entries
        return _FrozenLineStats(aggregated_timings, stats.unit)

    @functools.cached_property
    def object_count(self) -> int:
        return len(self.functions)

    @functools.cached_property
    def autoprof_doctests(self) -> bool:
        config = self.config
        if config is None:
            return False
        return bool(resolve_hooked_option(config, 'autoprof_doctests'))

    @property
    def tee_global_prof(self) -> Union[bool, Literal['always']]:
        value: Union[
            bool, Literal['always'], None,
        ] = vars(self).get('tee_global_prof')
        if value is not None:
            return value
        config = self.config
        if config is None:
            value = False
        else:
            value = resolve_hooked_option(config, 'autoprof_global_profiler')
        self.tee_global_prof = value
        return value

    @tee_global_prof.setter
    def tee_global_prof(self, tee_global_prof: Union[bool, str, None]) -> None:
        if isinstance(tee_global_prof, str):
            tee_global_prof = tee_global_prof.lower()
        if tee_global_prof not in (None, 'always'):
            tee_global_prof = bool(tee_global_prof)
        vars(self)['tee_global_prof'] = (  # type: ignore[index]
            tee_global_prof
        )

    @functools.cached_property
    def stash(self) -> Union['AutoProfStash', None]:
        if self.config is None:
            return None
        key = _import(THIS_PACKAGE + '.importers', 'AUTOPROF_STASH_KEY')
        try:
            return self.config.stash[key]
        except KeyError:
            pass
        Stash = _import(THIS_PACKAGE + '.importers', 'AutoProfStash')
        stash = Stash.from_config(self.config, profiler=self)
        self.config.stash[key] = stash
        return stash

    _patches: pytest.MonkeyPatch
    _cleanup_callbacks: List[functools.partial]
    config: Union[pytest.Config, None]
    profiled_doctests: DoctestRegistry
    non_profiled_doctests: DoctestRegistry
    omitted_doctests: DoctestRegistry
    _cached_properties: ClassVar[FrozenSet[Annotated[str, Identifier]]]


LineProfiler.__init_subclass__()
