"""
Patch `multiprocessing` so that profiling extends into processes it
creates.

Notes
-----
- Inspired by `coverage` (see: `coverage/multiproc.py`).
- Results may vary if the process pool is not properly `.close()`-d and
  `.join()`-ed (see similar caveat at https://coverage.readthedocs.io/\
en/latest/subprocess.html#using-multiprocessing)
"""
import functools
import multiprocessing.process

from ._typing import (
    Dict,
    Callable, ParamSpec, Concatenate,
    TypeVar,
    Annotated, Any, Union, Optional,
    Identifier,
)
from .importers import _SubprocImporter, AutoProfStash
from .startup_hook import _setup_in_subprocess


T = TypeVar('T')
PS = ParamSpec('PS')
_Stash = str
_HookState = Dict[Annotated[str, Identifier], _Stash]

_PATCHED_MARKER = '_pytest_autoprofile_patched_multiprocessing'


class PickleHook:
    """
    Object which, when unpickled, sets up profiling in the
    `multiprocessing`-created process. Inspired by
    `coverage.multiproc.Stowaway`.
    """
    def __init__(self, stash: _Stash) -> None:
        self.stash = stash

    def __getstate__(self) -> _HookState:
        return {'stash': self.stash}

    def __setstate__(_, state: _HookState) -> None:
        apply_monkey_patches(state['stash'])


def bootstrap(
    self: multiprocessing.process.BaseProcess,
    vanilla_impl: Callable[
        Concatenate[multiprocessing.process.BaseProcess, PS], T
    ],
    *args: PS.args,
    **kwargs: PS.kwargs
) -> T:
    """
    Wrap around `multiprocessing.process.BaseProcess._bootstrap()`,
    writing the profiling results after it is run.

    Parameters
    ----------
    self
        `BaseProcess`
    vanilla_impl()
        `BaseProcess._bootstrap()`
    *args, **kwargs
        Passed to `BaseProcess._bootstrap()`

    Return
    ------
    Return value of `BaseProcess._bootstrap()`
    """
    try:
        return vanilla_impl(self, *args, **kwargs)
    finally:  # Write profiling results
        _SubprocImporter.shared_stash.cleanup()


def get_preparation_data(
    vanilla_impl: Callable[PS, Dict[Annotated[str, Identifier], Any]],
    serialized_stash: _Stash,
    *args: PS.args, **kwargs: PS.kwargs
) -> Dict[Annotated[str, Identifier], Any]:
    """
    Wrap around `multiprocessing.spawn.get_preparation_data()`, slipping
    a `PickleHook` into the returned dictionary so that profiling is
    triggered upon unpickling.

    Parameters
    ----------
    vanilla_impl()
        `multiprocessing.spawn.get_preparation_data()`
    serialized_stash
        File from which the stash should be loaded
    *args, **kwargs
        Passed to `multiprocessing.spawn.get_preparation_data()`

    Return
    ------
    Dictionary returned by
    `multiprocessing.spawn.get_preparation_data()` with an extra key
    """
    key = 'pytest_autoprofile_pickle_hook'  # Doesn't matter
    data = vanilla_impl(*args, **kwargs)
    assert key not in data
    data[key] = PickleHook(serialized_stash)
    return data


def apply_monkey_patches(
    serialized_stash: _Stash, *, stash: Optional[AutoProfStash] = None,
) -> None:
    """
    Set up profiling in `multiprocessing` processes.

    Parameters
    ----------
    serialized_stash
        Path to the file whence a `AutoProfStash` object can be loaded
    stash
        Optional `AutoProfStash`;
        if not provided, it is loaded from `serialized_stash`, and
        profiling is set up therefrom in the (sub-)process

    Side effects
    ------------
    - `multiprocessing` marked as having been set up
    - `multiprocessing.process.BaseProcess._bootstrap()` patched
    - `multiprocessing.spawn.get_preparation_data()` patched
    - Cleanup callbacks registered via `stash.add_cleanup()`
    """
    if getattr(multiprocessing, _PATCHED_MARKER, False):
        return
    if stash is None:
        stash = AutoProfStash._load_in_subproc(serialized_stash)
        _setup_in_subprocess(stash)

    vanilla: Union[Callable, None]

    # Patch `multiprocessing.process.BaseProcess._bootstrap()`
    Proc = multiprocessing.process.BaseProcess
    vanilla = Proc._bootstrap  # type: ignore[attr-defined]
    Proc._bootstrap = (  # type: ignore[attr-defined]
        functools.partialmethod(bootstrap, vanilla)
    )
    stash.add_cleanup(setattr, Proc, '_bootstrap', vanilla)

    # Patch `multiprocessing.spawn.get_preparation_data()`
    try:
        from multiprocessing import spawn
    except ImportError:
        pass
    else:
        vanilla = getattr(spawn, 'get_preparation_data', None)
        if vanilla:
            spawn.get_preparation_data = functools.partial(
                get_preparation_data, vanilla, serialized_stash,
            )
            stash.add_cleanup(setattr, spawn, 'get_preparation_data', vanilla)

    # Mark `multiprocessing` as having been patched
    setattr(multiprocessing, _PATCHED_MARKER, True)
    stash.add_cleanup(vars(multiprocessing).pop, _PATCHED_MARKER, None)
