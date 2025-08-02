import functools
import re
import pathlib

import pytest

from pytest_autoprofile import _test_utils as utils
from pytest_autoprofile._typing import (
    Dict, List, Callable, Annotated, TypeAlias, Identifier,
)
from pytest_autoprofile.option_hooks import OptionParsingWarning


Checker: TypeAlias = Callable[..., utils.CheckPytestResult]


@utils.environment_fixture(setup_scope='module')
def simple_test_script(tmp_path_factory: pytest.TempPathFactory):
    """
    Fixture for a simple test.

    Packages
    --------
    nil

    Tests
    -----
    <test_dir>/test_misc.py::test_foo
        (1 test)
        A FAILING test with a bad string-comparison assertion
    """
    tmpdir = tmp_path_factory.mktemp('.test_autoprof_simple')
    return [], utils.write_script(
        tmpdir / 'test_misc.py',
        """
    def test_foo():
        assert 'foo bar baz' == 'foo bar bar'
        """,
    )


@utils.environment_fixture
def complex_packages_and_tests():
    """
    Fixture for a complex setup with two packages and a test suite.

    Packages
    --------
    <path_dir>/math_pkg
        Package implementing arimatic functions (`.arithmatics`) and
        Taylor-series approximations of various functions
        (`.taylor_series`)
    <path_dir>/string_pkg
        Package containing utility functions for working with strings
        (`.utils`), as well as defining a utility class on the top-level

    Tests
    -----
    <test_dir>/test_math.py::test_{exp,cosine,sine}
        (3 tests)
        Tests for the functions in `math_pkg.taylor_series`
    <test_dir>/test_string.py::test_{pascal_to_snake,snake_to_pascal}
        (2 tests, 4 subtests)
        Tests for the functions in `string_pkg.utils`
    <test_dir>/test_string.py::test_word_count
        (1 test, 3 subtests)
        Test for using a function in `string_pkg.utils` indirectly via
        the top-level utility class
    """
    path = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_autoprof'
    )
    assert path.is_dir()
    tests = path / 'my_test_package'
    assert tests.is_dir()
    return path, tests


def get_nhits(
    result: utils.CheckPytestResult
) -> Dict[Annotated[str, Identifier], int]:
    assert result.line_profiler is not None  # Help `mypy` out
    timings = utils.parse_profiler_output_lines(result.line_profiler.outlines)
    return {
        func: sum(n for _, n, _ in entries)
        for (*_, func), entries in timings.items()
    }


@pytest.fixture
def check_simple(
    pytester: pytest.Pytester, simple_test_script: utils.TestEnvironment,
) -> Checker:
    return functools.partial(utils.check_pytest, pytester, simple_test_script)


@pytest.fixture
def check_complex(
    pytester: pytest.Pytester,
    complex_packages_and_tests: utils.TestEnvironment,
) -> Checker:
    return functools.partial(
        utils.check_pytest, pytester, complex_packages_and_tests,
    )


@pytest.mark.parametrize('rewrite', [True, False])
def test_assertion_rewrite(
    pytester: pytest.Pytester, check_simple: Checker, rewrite: bool,
) -> None:
    """
    Test that `pytest-autoprofile` doesn't clobber `pytest`'s own
    assertion rewrites.
    """
    result = check_simple(
        # The test should fail
        utils.CheckPytestConfig(
            test_count={'failed': 1}, check_pytest_return_code=1,
        ),
        # Make sure rich diffs are used
        '--verbose', '--verbose', '--verbose',
        '--autoprof-tests',
        *(() if rewrite else ('--assert=plain',)),
        test_foo=1,
    ).pytest
    assertion_pattern = (
        # Note: the output in 'short test summary info' isn't
        # consistently there between Python versions...  so look for the
        # output in the 'FAILURES' section instead, which is somewhat
        # consistent and have a leading 'E' on each line of the failed
        # assertion
        'E' '( +)' '-'   '( +)' 'foo bar ba'   'r\n'
        'E' '\\1'  '\\?' '\\2'  '          ' '\\^\n'
        'E' '\\1'  '\\+' '\\2'  'foo bar ba'   'z\n'
        'E' '\\1'  '\\?' '\\2'  '          ' '\\^'
    )
    # Check if the assertion is properly formatted
    assert bool(re.search(assertion_pattern, str(result.stdout))) == rewrite


def test_packages_and_tests_fixture(check_complex: Checker) -> None:
    """
    Test that the tests in the `complex_packages_and_tests()` fixture
    behaves as expected.
    """
    check_complex(
        utils.CheckPytestConfig(
            test_count=10,  # type: ignore[arg-type]
            no_profiling=True,
        )
    )


def test_always_autoprof(check_complex: Checker) -> None:
    """
    Test the `--always-autoprof` and `--postimport-autoprof` flags.
    """
    check_complex(
        '--always-autoprof=math_pkg.arithmatics::add,math_pkg.taylor_series',
        add=True,
        sub=False,
        exp=True,
        sin=True,
        cos=True,
        wc=False,
    )
    check_complex(
        '--always-autoprof=string_pkg',
        sin=False,
        word_count=False,
        wc=True,
        pascal_to_snake=True,
        snake_to_pascal=True,
    )
    check_complex(
        '--always-autoprof=string_pkg.utils',
        word_count=True,
        wc=False,
        pascal_to_snake=True,
        snake_to_pascal=True,
    )
    # Test that imported names are also profiled (via calling
    # `profile.add_imported_function_or_module()`)
    # (`--postimport-autoprof` should be functionally the same here)
    nhits: List[Dict[str, int]] = []
    for flag in '--always-autoprof', '--postimport-autoprof':
        result = check_complex(
            flag + '=string_pkg::pascal_to_snake',
            word_count=False,
            wc=False,
            pascal_to_snake=True,
            snake_to_pascal=False,
        )
        nhits.append(get_nhits(result))
    assert nhits[0] == nhits[1]


def test_recursive_autoprof(check_complex: Checker) -> None:
    """
    Test the `--recursive-autoprof` and `--postimport-autoprof` flags.
    """
    check_complex(
        # No-op because no profiling target specified
        utils.CheckPytestConfig(no_profiling=True),
        '--recursive-autoprof',
        add=False,
        sin=False,
        wc=False,
    )
    check_complex(
        # Bare `--recursive-autoprof` -> recursively autoprof all
        # `--always-autoprof` targets
        '--always-autoprof=math_pkg',
        '--recursive-autoprof',
        add=True,
        sin=True,
        wc=False,
    )
    check_complex(
        # Otherwise, only recursively profile the specified targets
        '--always-autoprof=string_pkg',
        '--recursive-autoprof=math_pkg',
        add=True,
        sin=True,
        wc=True,
        word_count=False,
    )
    # Compare between `--recursive-autoprof`, `--postimport-autoprof`:
    # - `--recursive-autoprof`:
    #   - Warn against the 2 non-package targets, moving them to
    #     `--always-autoprof`
    #   - Not concerned about the nonexistent non-package target bacause
    #     it is never imported to begin with
    # - `--postimport-autoprof`:
    #   - Not concerned about either module or object targets,
    #     automatically distinguishing between them and only recursing
    #     into the former
    #   - Warn against the 2 nonexistent targets
    bad_module = next(utils.propose_name('nonexistent_pkg')) + '.submodule'
    bad_func = next(utils.propose_name()) + '::func'
    targets = [
        'math_pkg.arithmatics::add', 'string_pkg', bad_module, bad_func,
    ]
    for option, WarningType, msg in [
        (
            'recursive',
            OptionParsingWarning,
            re.escape(
                '--recursive-autoprof: '
                'found 2 invalid (non-module) targets '
                f'(math_pkg.arithmatics::add,{bad_func}), '
                'moving them to `--always-autoprof`'
            ),
        ),
        (
            'postimport',
            UserWarning,
            re.escape(
                '--postimport-autoprof: '
                '2 targets cannot be profiled:\n'
                f'- ModuleNotFoundError (2): {bad_func}, {bad_module}'
            ),
        ),
    ]:
        flag = '--{}-autoprof={}'.format(option, ','.join(targets))
        record = check_complex(
            utils.CheckPytestConfig(capture_reported_warnings=WarningType),
            flag,
            add=True, sin=False, wc=True, word_count=True,
        ).reported_warnings
        # Warning should be issued exactly once
        if len(record) == 1:
            continue
        warnings = [
            '{0.filename}:{0.lineno}: {0.category.__name__}: {0.message}'
            .format(warning_message)
            for warning_message in record
        ]
        raise AssertionError(
            f'Expected 1 {WarningType.__name__}, got {len(warnings)}: '
            f'{warnings!r}',
        )


def test_postimport_autoprof(check_complex: Checker) -> None:
    """
    Test that we are able to get more profiling data with
    `--postimport-autoprof` than `--always-autoprof` when profiling
    `line_profiler` itself.
    """
    pattern = (
        '--{}-autoprof=line_profiler::LineProfiler.wrap_callable'
    )
    check = functools.partial(
        check_complex,
        utils.CheckPytestConfig(
            # `wrap_callable()` isn't part of the test environment, we
            # have to disable line-number checks or it will error out
            check_line_nums=False,
        ),
        '--recursive-autoprof=math_pkg',
    )
    try:
        always = check(pattern.format('always'), wrap_callable=True)
    except AssertionError as e:  # Not profiled at all
        msg, = e.args
        if 'wrap_callable' not in msg:
            raise
        check(pattern.format('always'), wrap_callable=False)
    else:  # Profiled by no data collected
        assert not get_nhits(always)['wrap_callable']
    postimport = check(pattern.format('postimport'), wrap_callable=True)
    assert get_nhits(postimport)['wrap_callable']


def test_autoprof_tests(check_complex: Checker) -> None:
    """
    Test the `--autoprof-tests`, `--autoprof-mod` and
    `--autoprof-imports` flags.
    """
    check_complex(
        # Nothing whose imports are to be profiled -> no profiling
        utils.CheckPytestConfig(no_profiling=True),
        '--autoprof-imports',
        sin=False,
        wc=False,
        test_exp=False,
        test_word_count=False,
    )
    check_complex(
        # Tests are profiled, imports aren't
        '--autoprof-tests',
        sin=False,
        wc=False,
        test_exp=True,
        test_word_count=True,
    )
    check_complex(
        # Tests and their direct imports are profiled
        '--autoprof-tests', '--autoprof-imports',
        sin=True,
        add=True,
        sub=False,
        wc=True,
        word_count=False,
        test_exp=True,
        test_word_count=True,
    )
    check_complex(
        (
            # Only profile the matching imports
            '--autoprof-mod=math_pkg.arithmatics,'
            # This is indirectly used, but isn't imported by the tests
            'operator::neg'
        ),
        # `math_pkg`
        sin=False,
        add=True,
        sub=False,
        # `string_pkg`
        wc=False,
        word_count=False,
        # Tests
        test_exp=False,
        test_word_count=False,
        # `operator`
        neg=False,
    )


def test_autoprof_view(check_complex: Checker) -> None:
    """
    Test the `--autoprof-view` flag.
    """
    check_complex(  # Lifted from a `test_autoprof_tests()` example
        utils.CheckPytestConfig(view_profiling_results=True),
        '--autoprof-tests',
        sin=False,
        wc=False,
        test_exp=True,
        test_word_count=True,
    )
