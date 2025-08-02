"""
Tests to ensure that `@line_profiler.profile` functions independently of
our profiler, which is nonetheless able to attach thereto and get
profiling output therefrom.
"""
import functools
import pathlib

import pytest

from pytest_autoprofile import _test_utils as utils
from pytest_autoprofile._typing import (
    List,
    Callable, Collection, Generator,
    Annotated, TypeAlias, Union,
    Identifier,
)


Checker: TypeAlias = Callable[..., utils.CheckPytestResult]


@utils.environment_fixture
def simple_env():
    """
    Fixture for a test which uses a function explicitly decorated with
    `@line_profiler.profile`.

    Modules
    --------
    <path_dir>/mymod.py
        Defines the function `func()`.

    Tests
    -----
    <test_dir>/test_func.py::test_func
        Test using `mymod.func()`.
    """
    files = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_global_prof'
        / 'simple_env'
    )
    assert (files / 'modules' / 'mymod.py').exists()
    assert (files / 'tests' / 'test_func.py').exists()
    return files / 'modules', files / 'tests'


@utils.environment_fixture
def complex_env():
    """
    Fixture for a more complex test involving manually `.enable()`-ing
    and `.disable()`-ing `@line_profiler.profile`

    Modules
    -------
    <nil>

    Tests
    -----
    <test_dir>/test_toggling.py::test_toggling
        Test explicitly toggling the state of the global profiler.
    """
    files = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_global_prof'
        / 'complex_env'
    )
    assert (files / 'test_toggling.py').exists()
    assert (files / 'script.py').exists()
    return [], files


@pytest.fixture
def check_simple(
    pytester: pytest.Pytester, simple_env: utils.TestEnvironment,
) -> Checker:
    return functools.partial(utils.check_pytest, pytester, simple_env)


@pytest.fixture
def check_complex(
    pytester: pytest.Pytester, complex_env: utils.TestEnvironment,
) -> Checker:
    return functools.partial(utils.check_pytest, pytester, complex_env)


@pytest.fixture(autouse=True)
def clean_env(
    tmp_path_factory: pytest.TempPathFactory
) -> Generator[pathlib.Path, None, None]:
    """
    `chdir()` to a fresh directory and remove the existing
    `LINE_PROFILE` env var.
    """
    path = tmp_path_factory.mktemp('new_curdir')
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(path)
        mp.delenv('LINE_PROFILE', raising=False)
        yield path


@pytest.mark.parametrize(
    ('agp', 'autoprof', 'global_prof'),
    [
        # `False` -> no `--autoprof-global-profiler` flag == `False`
        (False, False, True),
        (False, False, False),
        # `True` -> `--autoprof-global-profiler` flag == `'always'`
        (True, True, True),
        (True, True, False),
        # `'yes'` == `True`
        ('yes', True, True),
        ('yes', False, False),
    ],
)
def test_autoprof_global_profiler_env_enabling(
    check_simple: Checker,
    agp: Union[bool, str],
    autoprof: bool,
    global_prof: bool,
) -> None:
    """
    Test enabling `@line_profiler.profile` across the board with the
    `${LINE_PROFILE}` environment variable.
    """
    args: List[str] = []
    if agp in (True, False):
        if agp:
            args.append('--autoprof-global-profiler')
    else:
        assert not isinstance(agp, bool)  # Help `mypy`
        args.append('--autoprof-global-profiler=' + agp)
    run_test = functools.partial(
        check_simple,
        utils.CheckPytestConfig(
            subprocess=True,
            test_count=1,  # type: ignore[arg-type]
            no_profiling=not autoprof,
        ),
        *args,
        func=autoprof,
    )
    if global_prof:
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv('LINE_PROFILE', '1')
            run_test()
    else:
        run_test()
    # This is written by the `atexit` hook that the global profiler
    # itself registers and should not be affected by our profiling
    assert pathlib.Path('profile_output.txt').exists() == global_prof
    assert pathlib.Path('profile_output.lprof').exists() == global_prof


@pytest.mark.parametrize(
    ('agp', 'targets'),
    [
        ('no', ()),
        ('yes', ('func1', 'func3')),
        ('always', ('func0', 'func1', 'func2', 'func3')),
    ],
)
def test_autoprof_global_profiler_explicit_enabling(
    check_complex: Checker,
    agp: str,
    targets: Collection[Annotated[str, Identifier]],
) -> None:
    """
    Test enabling and disabling `@line_profiler.profile` explicitly in
    the test code.
    """
    targets = frozenset(targets)
    func_names = {'func0', 'func1', 'func2', 'func3'}
    assert targets <= func_names
    presence = {func: func in targets for func in func_names}
    check_complex(
        utils.CheckPytestConfig(
            subprocess=True,
            test_count=1,  # type: ignore[arg-type]
            no_profiling=not targets,
        ),
        '--autoprof-global-profiler=' + agp, '--autoprof-subprocs',
        **presence,
    )
    # This is written by the `atexit` hook that the global profiler
    # itself registers and should not be affected by our profiling
    assert pathlib.Path('profile_output.txt').exists()
    assert pathlib.Path('profile_output.lprof').exists()
