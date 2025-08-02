import functools
import multiprocessing
import os
import platform
import pathlib
import shlex
import sysconfig

import pytest

from pytest_autoprofile import _test_utils as utils
from pytest_autoprofile._typing import (
    Dict, Callable,
    Annotated, Any, TypeAlias, Literal,
    Identifier,
)


Checker: TypeAlias = Callable[..., utils.CheckPytestResult]
N = 32


@utils.environment_fixture
def environment():
    """
    Test fixture.

    Modules
    -------
    <path_dir>/mymodule
        Module containing a simple function `func()`

    Tests
    -----
    Each of the (sub-)tests calls `func()` with a total of 32 hits on
    the line inside the main loop.

    <test_dir>/test_func.py::test_in_process
        Test running `mymodule.func()` in-process
    <test_dir>/test_func.py::test_subprocess_run
        Test running `mymodule.func()` in a subprocess spawned with
        `subprocess.run()`
    <test_dir>/test_func.py::test_nested_subprocess
        Test running `mymodule.func()` in a nested subprocess spawned
        with `subprocess.run()`
    <test_dir>/test_func.py::test_os_system
        Test running `mymodule.func()` in a subprocess spawned with
        `os.system()`
    <test_dir>/test_func.py::test_multiprocessing (2 subtests)
        Test running `mymodule.func()` in subprocesses spawned with
        `multiprocessing.Pool.map()`.
    """
    files = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_subprocess'
    )
    path_dir = files / 'packages'
    test_dir = files / 'tests'
    assert path_dir.is_dir()
    assert test_dir.is_dir()
    return path_dir, test_dir


@pytest.fixture
def check(
    pytester: pytest.Pytester, environment: utils.TestEnvironment,
) -> Checker:
    return functools.partial(utils.check_pytest, pytester, environment)


@pytest.mark.parametrize('fail', [True, False])
@pytest.mark.parametrize(
    'flags, tests, ntests_profiled',
    [
        ('', 8, 2),
        ('-k "not in_process"', 6, 0),
        ('--autoprof-subprocs -k "not multiproc"', 6, 6),
        ('--autoprof-subprocs -k "not in_process and not multiproc"', 4, 4),
    ],
)
def test_profiling_subprocesses(
    check: Checker, flags: str, fail: bool, tests: int, ntests_profiled: int,
) -> None:
    """
    Test that the profiling of subprocesses can be toggled, and works
    both for subprocesses which finish without errors and which errors
    out.
    """
    _test_inner(check, flags, fail, tests, ntests_profiled)


@pytest.mark.parametrize('fail', [True, False])
@pytest.mark.parametrize(
    'flags, start_method, tests, ntests_profiled',
    [('--autoprof-subprocs', None, 8, 8)] + [
        ('--autoprof-subprocs -k test_multiprocessing', method, 2, 2)
        for method in ['spawn', 'fork', 'forkserver']
    ],
)
def test_profiling_multiprocessing(
    check: Checker,
    flags: str,
    fail: bool,
    start_method: Literal['spawn', 'fork', 'forkserver', None],
    tests: int,
    ntests_profiled: int,
) -> None:
    """
    Ditto `test_profiling_subprocesses()`, but with a test which uses
    `multiprocessing.Pool`.
    """
    if start_method:
        add_flags = '-o multiproc_start_method=' + start_method
        flags = f'{flags} {add_flags}' if flags else add_flags
        try:
            multiprocessing.get_context(start_method)
        except ValueError:
            pytest.skip(
                '`multiprocessing` does not support start method '
                f'{start_method!r} on this platform ({platform.platform()})'
            )
    _test_inner(check, flags, fail, tests, ntests_profiled)


def _test_inner(
    check: Checker, flags: str, fail: bool, tests: int, ntests_profiled: int,
) -> None:
    path = pathlib.Path(sysconfig.get_path('purelib'))
    files_before = set(os.listdir(path))
    options = [
        '--always-autoprof=mymodule::func', '-s', '-v', *shlex.split(flags),
    ]
    if fail:
        options.extend(['-o', 'make_test_func_fail=True'])
        config: Dict[Annotated[str, Identifier], Any] = {
            'test_count': {'failed': tests},
            'check_pytest_return_code': None,
        }
    else:
        config = {'test_count': tests}
    try:
        result = check(
            utils.CheckPytestConfig(subprocess=True, **config), *options,
            func=True,
        )
    finally:
        # Check that we cleaned up after ourselves and wiped the `.pth`
        # file
        files_after = set(os.listdir(path))
        try:
            assert files_after == files_before
        finally:  # Clean up the `.pth` file(s) we wrote
            for extra_file in files_after - files_before:
                if (
                    extra_file.startswith('_pytest_autoprofile_') and
                    extra_file.endswith('.pth')
                ):
                    (path / extra_file).unlink()

    assert result.line_profiler is not None  # Help `mypy`
    line = next(
        line for line in str(result.line_profiler.stdout).splitlines()
        if line.endswith('x += n')
    )
    try:
        nhits = int(line.split()[1])
    except ValueError:
        nhits = 0
    assert nhits == ntests_profiled * N
