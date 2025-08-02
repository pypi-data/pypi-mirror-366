"""
Generate the `.pth` hook which provides the same profiling facilities
to spawned `python` interpreters as on the main `pytest` process.

Notes
-----
- To reduce overhead, imports in this file are deferred to being as late
  as possible, and some type annotations are omitted.
- Inspired by `coverage` (see: `igor.py::run_tests_with_coverage()`,
  `coverage/control.py::process_startup()`, and
  `tests/conftest.py`).
"""
__all__ = ('write_pth_hook', 'load_pth_hook')

_PID_ENV_VAR_NAME = 'PYTEST_AUTOPROFILE_TEST_PID'
_DEBUG = False


def write_pth_hook(
    stash,
    *,
    serialized_stash=None,
    update_env: bool = True,
    wrap_fork: bool = True,
):
    """
    Parameters
    ----------
    stash
        `~.importers.AutoProfStash` object
    serialized_stash
        Optional path to the serialization of `stash`;
        if not provided, it is created here
    update_env
        Whether to also update the environment by injecting the
        `${PYTEST_AUTOPROFILE_TEST_PID}` variable, which subprocesses
        will inherit
    wrap_fork
        Whether to also wrap `os.fork()` so that forked processes are
        properly profiled (and instruct subprocesses to do the same)

    Return
    ------
    `pathlib.Path` to the written `.pth` file

    Side effects
    ------------
    - `stash` serialized to a tempoarary file
    - Temporary `.pth` file written
    - If `update_env` is true, `os.environ` updated
    - If `wrap_fork` is true, `os.fork()` wrapped
    - Callbacks for undoing the above added via `stash.add_cleanup()`
    """
    import os
    from operator import setitem
    from pathlib import Path
    from sysconfig import get_path
    from tempfile import mkstemp

    # Write the `.pth` file
    if serialized_stash is None:
        serialized_stash = stash._dump()
    handle, pth_fname = mkstemp(
        prefix='_pytest_autoprofile_', suffix='.pth', dir=get_path('purelib'),
    )
    try:
        pth = Path(pth_fname)
        pth.write_text('import {0}; {0}.{1}({2}, {3!r}, wrap_fork={4})'.format(
            (lambda: None).__module__,
            'load_pth_hook',
            stash.process_id,
            str(serialized_stash),
            bool(wrap_fork),
        ))
        stash.add_cleanup(pth.unlink, missing_ok=True)
    except Exception:
        os.remove(pth_fname)
        raise
    finally:
        os.close(handle)

    # Update the environment
    if update_env:
        try:
            value = os.environ[_PID_ENV_VAR_NAME]
        except KeyError:
            stash.add_cleanup(os.environ.pop, _PID_ENV_VAR_NAME, None)
        else:
            stash.add_cleanup(setitem, os.environ, _PID_ENV_VAR_NAME, value)
        os.environ[_PID_ENV_VAR_NAME] = str(stash.process_id)

    # Wrap `os.fork()`
    if wrap_fork:
        _make_fork_wrapper(stash)

    return pth


def load_pth_hook(
    ppid: int, serialized_stash: str,
    *,
    suppress_errors: bool = not _DEBUG,
    wrap_fork: bool = True,
) -> None:
    """
    Set up profiling in the current subprocess where appropriate.

    Parameters
    ----------
    ppid
        Process ID of the parent test process;
        for the side effects below to happen, both
        `${PYTEST_AUTOPROFILE_TEST_PID}` and the `.process_id` of the
        deserialized stash must line up with it
    serialized_stash
        Path to the serialized `AutoProfStash` object
    suppress_errors
        Whether to suppress the errors occurring in the inner function
    wrap_fork
        Whether to also wrap `os.fork()` so that forked processes are
        properly profiled

    Side effects
    ------------
    - Profiler and importer(s) installed
    - Preexisting import targets of the importer(s) purged from
      `sys.modules` (to be later re-imported with instrumentation)
    - Post-import profiling executed (where appropriate)
    - Callback to call `LineProfiler.dump_stats()` registered with
      `.add_cleanup()` at the deserialized stash
    - `.cleanup()` of said stash registered with `atexit.register()`

    Notes
    -----
    Each Python interpretor only calls the inner function once.
    """
    from os import environ

    try:
        env_ppid = int(environ[_PID_ENV_VAR_NAME])
    except (KeyError, ValueError):
        return
    if env_ppid != ppid:
        return
    accepted_errors = (Exception,) if suppress_errors else ()
    # Note: `.pth` files may be double-loaded in a virtual environment
    # (see https://stackoverflow.com/questions/58807569), so work around
    # that;
    # also see similar check in `coverage/control.py::process_startup()`
    if getattr(_inner_hook, 'called', False):
        return
    try:
        _inner_hook(ppid, serialized_stash, wrap_fork)
    except accepted_errors:
        pass
    finally:
        _inner_hook.called = True  # type: ignore[attr-defined]


def _inner_hook(test_pid: int, serialized_stash: str, wrap_fork: bool) -> None:
    from .importers import AutoProfStash

    try:
        stash = AutoProfStash._load_in_subproc(serialized_stash)
    except FileNotFoundError:
        return
    if test_pid == stash.process_id:
        _setup_in_subprocess(stash, exit_hook=True, wrap_fork=wrap_fork)


def _setup_in_subprocess(
    stash, *, exit_hook: bool = False, wrap_fork: bool = False,
) -> None:
    from sys import modules

    from . import setup

    if not setup._should_profile_subprocs(stash):
        raise AssertionError

    # Set up the importers
    if stash.importers:
        if len(stash.importers) > 2:
            raise AssertionError
        modules_importer = next(
            (im for im in stash.importers if im.importer_class == 'modules'),
            None,
        )
        tests_importer = next(
            (im for im in stash.importers if im.importer_class == 'tests'),
            None,
        )
        if modules_importer is tests_importer is None:
            raise AssertionError
        # Install importers
        setup._scrub_imported_modules(
            modules, modules_importer, tests_importer,
        )
        # Handle post-import profiling
        if modules_importer and modules_importer.postimport_autoprof:
            modules_importer.add_targets_explicitly()

    # Set up the profiler and the hooks for its data to be dumped on
    # exit
    stash.profiler.install()
    # Don't delete the dumped stats on exit, the parent process will
    # take care of that
    outfile = stash.generate_new_tempfile(cleanup_priority=None)
    stash.add_cleanup(stash.profiler.dump_stats, str(outfile))

    if exit_hook:
        from atexit import register

        register(stash.cleanup)

    if wrap_fork:
        _make_fork_wrapper(stash)


def _make_fork_wrapper(stash) -> None:
    """
    Create a wrapper around `os.fork()` which handles profiling.

    Parameters
    ----------
    stash
        `~.importers.AutoProfStash` object

    Side effects
    ------------
    If `wrap` is true, replace `os.fork()` (if available) with the
    wrapper and register a cleanup callback at `stash` undoing that
    """
    import os
    from functools import wraps

    try:
        fork = os.fork
    except AttributeError:  # Can't fork on this platform
        return

    @wraps(fork)
    def wrapper():
        result = fork()
        if not result:  # In the fork
            _setup_in_subprocess(stash._get_forked_stash())
        return result

    os.fork = wrapper
    stash.add_cleanup(setattr, os, fork)
