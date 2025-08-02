import contextlib
import functools
import re
import pathlib
import shlex
import textwrap
import types

import pytest
try:
    import pytest_doctestplus  # noqa: F401
except ImportError:
    HAS_PYTEST_DOCTEST_PLUS = False
else:
    HAS_PYTEST_DOCTEST_PLUS = True
try:
    import xdoctest  # noqa: F401
except ImportError:
    HAS_XDOCTEST = False
else:
    HAS_XDOCTEST = True

from pytest_autoprofile import _test_utils as utils
from pytest_autoprofile._typing import (
    TYPE_CHECKING,
    Dict, List, Tuple,
    Collection, ContextManager, Generator, Iterable, Mapping,
    Callable,
    Annotated, Type, TypeAlias, TypeVar,
    Literal, Union, Optional,
    cast, get_args,
    ImportPath, Parsable,
)
from pytest_autoprofile._warnings import DoctestProfilingWarning, WarningMessage
from pytest_autoprofile.option_hooks import resolve_hooked_option


HAS_XDOCTEST_ENV_EFFECTS = False
if HAS_XDOCTEST:
    for _method in 'effect', 'effects':  # <, >= 0.15
        try:
            func = (
                ImportPath('xdoctest.directive', 'Directive.' + _method)
                .import_target()
            )
            if callable(func) and 'REQUIRES(env:' in (func.__doc__ or ''):
                HAS_XDOCTEST_ENV_EFFECTS = True
        except (ImportError, AttributeError):
            continue
        else:
            del func
        finally:
            del _method

Checker: TypeAlias = Callable[..., utils.CheckPytestResult]
FunctionName = Literal[
    'foo', 'bar', 'baz', 'foobar', 'foofoo', 'barbar',
    '__init__', 'instance_method', 'class_method',
]
Context = Literal['body', 'call']

FUNCTION_NAMES: Tuple[str, ...] = get_args(FunctionName)
CONTEXTS: Tuple[str, ...] = get_args(Context)

S1 = TypeVar('S1', bound=str)
S2 = TypeVar('S2', bound=str)


@utils.environment_fixture
def doctest_environment():
    """
    Test environment containing a package with various forms of
    doctests, a doctest in a `.md` file, and also standard tests.

    Packages
    --------
    <path_dir>/my_pkg
        Dummy package defining functions, a class, and doctests

    Doctests
    --------
    <path_dir>/my_pkg/funcs.py::__doc__
        (1 test)
        A FAILING module-level test.
    <path_dir>/my_pkg/funcs.py::{foo,bar}.__doc__
        (2 tests)
        Statically-defined function-level doctests;
        in particular:
        - `foo()`'s doctest contains a function definition and an
          `xdoctest`-specific directive, and
        - `bar()`'s doctest, an import
    <path_dir>/my_pkg/funcs.py::{baz,foobar}.__doc__
        (2 tests)
        Function-level doctests which are dynamically defined (and thus
        cannot be profiled)
    <path_dir>/my_pkg/classes.py::SomeClass.__doc__
        (1 test)
        A class-level doctest
    <path_dir>/my_pkg/classes.py::SomeClass.class_method.__doc__
        (1 test)
        A method-level doctest
    <test_dir>/test_doc.md
        (1 test)
        A doctest in an independent `test_doc.md` file (cannot be
        profiled)

    Regular tests
    -------------
    <test_dir>/test_misc.py::test_barbar()
        (1 test)
        A regular test using a function that the doctests don't cover

    Notes
    -----
    The various `# PROF: ...` comments are not essential to the
    profiling, but helps the test in verifying that the individual lines
    have been profiled.
    """
    files = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_doctest'
    )
    pkg_dir = files / 'packages' / 'my_pkg'
    test_dir = files / 'tests'
    assert pkg_dir.is_dir()
    assert test_dir.is_dir()
    return pkg_dir.parent, [pkg_dir, test_dir]


@pytest.fixture
def check(
    pytester: pytest.Pytester,
    doctest_environment: utils.TestEnvironment,
) -> Checker:
    """
    Run the test suite with `doctest_environment()` and check how they
    have been profiled.
    """
    def indent_warning_message(w: WarningMessage) -> str:
        return '- ' + textwrap.indent(get_message(w), '  ')[2:]

    @contextlib.contextmanager
    def preserve_locals(
        module: Annotated[str, Parsable[ImportPath]],
    ) -> Generator[None, None, None]:
        mod_object = ImportPath(module).import_target()
        assert isinstance(mod_object, types.ModuleType)
        namespace = vars(mod_object)
        old = namespace.copy()
        try:
            yield
        finally:
            namespace.clear()
            namespace.update(old)

    # Note: `xdoctest` up to version 1.2.0 destructively monkey-patches
    # `_pytest.doctest` (see `xdoctest` issue #173 and PR #174);
    # guard against that by using a context manager to freeze the module
    # content

    @preserve_locals('_pytest.doctest')
    def checker(
        *args,
        body_profiled: Optional[Mapping[FunctionName, bool]] = None,
        call_profiled: Optional[Mapping[FunctionName, bool]] = None,
        expect_warnings: Union[bool, None] = False,
        **kwargs
    ) -> utils.CheckPytestResult:
        if expect_warnings is not None:
            if not args:
                config = utils.CheckPytestConfig(
                    capture_reported_warnings=DoctestProfilingWarning,
                )
            elif isinstance(args[0], utils.CheckPytestConfig):
                config, *args = args  # type: ignore[assignment]
                crw = cast(
                    Tuple[Type[Warning], ...],
                    config.capture_reported_warnings,
                )
                if crw in ((), (Warning,)):
                    # Warning types not explicitly given
                    crw = *crw, DoctestProfilingWarning
                    config = config.replace(capture_reported_warnings=crw)
            else:
                config = utils.CheckPytestConfig(
                    capture_reported_warnings=DoctestProfilingWarning,
                )
            args = config, *args
        result = inner_check(*args, **kwargs)
        if not (
            expect_warnings is None
            or expect_warnings == bool(result.reported_warnings)
        ):
            wlist = result.reported_warnings
            raise AssertionError(
                'Expected {}, got {}:\n{}'
                .format(
                    'warnings' if expect_warnings else 'no warnings',
                    len(wlist),
                    '\n'.join(indent_warning_message(w) for w in wlist),
                )
            )
        if not (body_profiled or call_profiled):
            return result
        if args and not isinstance(args[0], str):
            args = args[1:]
        lp_result = result.line_profiler
        assert lp_result
        lp_stats = parse_line_profiler_stats(lp_result.outlines)
        ctx: Context
        for ctx, expected in [  # type: ignore[assignment]
            ('body', (body_profiled or {})), ('call', (call_profiled or {})),
        ]:
            stats = lp_stats[ctx]
            failures: List[str] = []
            for name, profiled in expected.items():
                if profiled == stats[name]:
                    continue
                failures.append(
                    '{}(): {} expected'
                    .format(name, 'presence' if profiled else 'absence')
                )
            if not failures:
                continue
            raise AssertionError('\n'.join((
                'pytest {} -> {} failure(s) ({} profiled?):'
                .format(shlex.join(args), len(failures), ctx),
                *('- ' + line for line in failures),
            )))
        return result

    inner_check = functools.partial(
        utils.check_pytest, pytester, doctest_environment,
    )
    return checker


def _parse_line_profiler_stats(
    funcs: Collection[S1], ctxs: Collection[S2], lines: Iterable[str],
) -> Dict[S2, Dict[S1, bool]]:
    """
    Check if the line suffixed with `  # PROF: {func}[{ctx}]` has
    profiling stats attached thereto.

    Example
    -------
    >>> import os
    >>> from contextlib import ExitStack
    >>> from functools import partial
    >>> from io import StringIO
    >>> from tempfile import TemporaryDirectory
    >>>
    >>> from line_profiler.line_profiler import show_func
    >>>
    >>> from pytest_autoprofile._test_utils import strip
    >>>
    >>>
    >>> content = strip('''
    ... def foo():
    ...     pass  # PROF: foo[spam]
    ...     pass  # PROF: foo[eggs]
    ...
    ...
    ... def bar():
    ...     pass  # PROF: bar[ham]
    ...     pass  # PROF: bar[eggs]
    ... ''')
    >>>
    >>> with ExitStack() as stack:
    ...     enter = stack.enter_context
    ...     tmpdir = enter(TemporaryDirectory())
    ...     sio = enter(StringIO(newline=None))
    ...     fname = os.path.join(tmpdir, 'sample_funcs.py')
    ...     with open(fname, mode='w') as fobj:
    ...         print(content, file=fobj)
    ...     write = partial(
    ...         show_func, filename=fname, unit=1, stream=sio,
    ...     )
    ...     write(
    ...         start_lineno=1,
    ...         func_name='foo',
    ...         timings=[(2, 2.5e9, 35000)],  # foo[spam]
    ...     )
    ...     write(
    ...         start_lineno=6,
    ...         func_name='bar',
    ...         timings=[(7, 1, 0)],  # bar[ham] (no time -> % hidden)
    ...     )
    ...     sio.flush()
    ...     lines = sio.getvalue().splitlines()
    ...
    >>> stats = _parse_line_profiler_stats(
    ...     ['foo', 'bar'], ['spam', 'ham', 'eggs'], lines,
    ... )
    >>> assert stats == {
    ...     'spam': {'foo': True, 'bar': False},
    ...     'ham': {'foo': False, 'bar': True},
    ...     'eggs': {'foo': False, 'bar': False},
    ... }, (lines, stats)
    """
    result = {ctx: dict.fromkeys(funcs, False) for ctx in ctxs}
    decimal = r'[0-9]+(?:\.[0-9]+)?(?:[eE][-+][0-9]{2,3})?'
    matcher = re.compile(
        r'^ *[0-9]+(?: +{}){{3,4}}'  # Line #, metrics (% may be absent)
        r' .*'  # Line content
        r'  # PROF: (?P<name>{})\[(?P<ctx>{})\]$'  # PROF comment
        .format(
            decimal,
            '|'.join(re.escape(func) for func in set(funcs)),
            '|'.join(re.escape(ctx) for ctx in set(ctxs)),
        ),
        re.MULTILINE,  # Ignore possible trailing linebreaks
    ).match
    for line in lines:
        match = matcher(line)
        if not match:
            continue
        if TYPE_CHECKING:
            assert match['name']
            assert match['ctx']
        key1: S1 = match['name']  # type: ignore[assignment]
        key2: S2 = match['ctx']  # type: ignore[assignment]
        result[key2][key1] = True
    return result


parse_line_profiler_stats: Callable[
    [Iterable[str]], Dict[Context, Dict[FunctionName, bool]]
] = functools.partial(  # type: ignore[assignment]
    _parse_line_profiler_stats, FUNCTION_NAMES, CONTEXTS,
)


def get_message(w: WarningMessage) -> str:
    return str(w.message)


@pytest.mark.parametrize(
    'autoprof_doctests, expected',
    [
        ('t', True),
        ('0', False),
        (None, 'all'),
        ('A', 'all'),
        ('aLl', 'all'),
        ('al', None),
    ],
)
def test_parse_autoprof_doctests(
    pytester: pytest.Pytester,
    autoprof_doctests: Union[str, bool, None],
    expected: Union[Literal['all'], bool, None],
) -> None:
    """
    Test the parsing of the `--autoprof-doctests` option.
    """
    flag = '--autoprof-doctests'
    if autoprof_doctests is not None:
        flag = '{}={}'.format(flag, autoprof_doctests)
    if expected is None:
        ctx: ContextManager = pytest.raises(pytest.UsageError)
    else:
        ctx = contextlib.nullcontext()
    with ctx:
        config = pytester.parseconfig(flag)
    if expected is None:
        return
    assert resolve_hooked_option(config, 'autoprof_doctests') == expected


def test_env_fixture(pytestconfig: pytest.Config, check: Checker) -> None:
    """
    Test that the tests in the `doctest_environment()` fixture
    behaves as expected.
    """
    # 1 passing non-doc test
    # (Also check that the test environment has a config source that is
    # separate from the project's)
    pytester_config = check(
        utils.CheckPytestConfig(
            test_count=1,  # type: ignore[arg-type]
            generate_config=True, no_profiling=True,
        ),
    ).config
    for attr in 'rootpath', 'inipath':
        assert getattr(pytester_config, attr) != getattr(pytestconfig, attr)
    # 1 passing non-module doctest
    check(
        utils.CheckPytestConfig(
            test_count=2,  # type: ignore[arg-type]
            no_profiling=True,
        ),
        '--doctest-glob=*.md',
    )
    # 1 failing and 6 passing module doctests
    check(
        utils.CheckPytestConfig(
            test_count={'failed': 1, 'passed': 8},
            check_pytest_return_code=1,
            no_profiling=True,
        ),
        '--doctest-glob=*.md',
        '--doctest-modules',
    )


def test_profiling_requirements(check: Checker) -> None:
    """
    Test that we only do doctest profiling when all the pieces of the
    puzzle are here.
    """
    def run_check(profiled: bool, *args, **kwargs) -> utils.CheckPytestResult:
        return check(
            utils.CheckPytestConfig(
                check_pytest_return_code=1, no_profiling=not profiled,
            ),
            '--doctest-modules',
            *args,
            **kwargs,
        )

    # This alone doesn't trigger profiling
    run_check(False, '--autoprof-rewrite-doctests')
    # ... and neither does this because `True` only profiles doctests
    # in files specified by `--autoprof-mod`
    run_check(False, '--autoprof-doctests=True')
    # This however does because of the implicit `'all'`
    # (and issues a warning because of the two untractable tests)
    wlist = run_check(
        True, '--autoprof-doctests', expect_warnings=True,
    ).reported_warnings
    msg, = [get_message(w) for w in wlist]
    assert 'Doctests (2) omitted from profiling output in file (1)' in msg
    assert 'my_pkg.funcs.baz' in msg
    assert 'my_pkg.funcs.foobar' in msg


def test_profiling_warnings(check: Checker) -> None:
    """
    Check that the correct warnings are issued when doctests are not
    profiled, and when they are omitted from the profiling report.
    """
    wlist = check(
        utils.CheckPytestConfig(check_pytest_return_code=1),
        '--autoprof-doctests',
        '--doctest-glob=*.md',  # Non-Python file -> can't profile
        '--doctest-modules',  # 2 dynamic.-def. doctests -> omitted
        expect_warnings=True,
    ).reported_warnings
    msg_1, msg_2 = [get_message(w) for w in wlist]
    if not msg_1.startswith('Doctest '):
        msg_1, msg_2 = msg_2, msg_1
    assert 'Doctest (1) could not be profiled in file (1)' in msg_1
    assert 'test_doc.md' in msg_1
    assert 'Doctests (2) omitted from profiling output in file (1)' in msg_2
    assert 'my_pkg.funcs.baz' in msg_2
    assert 'my_pkg.funcs.foobar' in msg_2


def test_autoprof_rewrite_doctests(check: Checker) -> None:
    """
    Test doctest rewriting with the `--autoprof-rewrite-doctests`
    option.
    """
    # Test the profiling of rewritten doctests
    check(
        utils.CheckPytestConfig(
            test_count=1,  # type: ignore[arg-type]
        ),
        '--autoprof-imports',  # Doctest of `bar()` imports `SomeClass`
        '--doctest-modules',  # Don't collect the `doctest.md` test
        '--autoprof-doctests',  # Profile all doctests when possible
        '--autoprof-rewrite-doctests',  # Rewrite doctests
        # Only run the doctest of `foo()`
        '-k', 'foo and not foobar',
        body_profiled={
            **dict.fromkeys(FUNCTION_NAMES, False),
            'foofoo': True,  # Defined in `foo.__doc__`
        },
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, False),
            'foo': True,
            'foofoo': True,
        },
        **{
            **dict.fromkeys(FUNCTION_NAMES, False),
            'foo': True,
        },
    )
    # Test running more or less the entire test suite
    wlist = check(
        utils.CheckPytestConfig(check_pytest_return_code=1),
        '--autoprof-imports',
        '--doctest-modules',
        '--autoprof-doctests',
        '--autoprof-rewrite-doctests',
        body_profiled={
            **dict.fromkeys(FUNCTION_NAMES, False),
            # Def. lives in `foo.__doc__` which is rewritten
            'foofoo': True,
            # `SomeClass` imported in `bar.__doc__` which is
            # rewritten, and then we called `.class_method()` in it
            'class_method': True,
        },
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, True),
            'barbar': False,  # Not called in doctests
            'foobar': False,  # Doctest failed before we called it
        },
        expect_warnings=True,
        **{
            **dict.fromkeys(FUNCTION_NAMES, True),
            'SomeClass': True,  # From the class doctest
            'barbar': False,  # Not called in doctests
            'baz': False,  # Cannot be profiled (dynam. defined)
            'foobar': False,  # Cannot be profiled (dynam. defined)
            # It's defined in `foo()`'s doctest and doesn't have its
            # own profiling entry
            'foofoo': False,
            'funcs': True,  # From the module doctest
        },
    ).reported_warnings
    assert len(wlist) == 1
    # If we don't pass `--autoprof-rewrite-doctests`, the
    # defined-in-doctest `foofoo()` and the imported `SomeClass` aren't
    # profiled
    check(
        utils.CheckPytestConfig(check_pytest_return_code=1),
        '--autoprof-imports',
        '--doctest-modules',
        '--autoprof-doctests',
        body_profiled=dict.fromkeys(FUNCTION_NAMES, False),
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, True),
            'barbar': False,  # Not called in doctests
            'foobar': False,  # Doctest failed before we called it
        },
        expect_warnings=True,
        **{
            **dict.fromkeys(FUNCTION_NAMES, False),
            'SomeClass': True,  # From the class doctest
            'funcs': True,  # From the module doctest
            'foo': True,  # From its doctest
            'bar': True,  # From its doctest
            'instance_method': True,  # From its doctest
        },
    )


def test_autoprof_doctests_true(check: Checker) -> None:
    """
    Test the interaction between `--autoprof-doctests=yes` and
    `--autoprof-mod=...`.
    """
    run_check = functools.partial(
        check,
        utils.CheckPytestConfig(
            test_count={'passed': 7, 'failed': 1},
            check_pytest_return_code=1,
        ),
        '--autoprof-imports',
        '--doctest-modules',
        '--autoprof-doctests=true',
        '--autoprof-rewrite-doctests',
    )
    # Only profile doctests in `my_pkg.funcs`
    run_check(
        '--autoprof-mod=my_pkg.funcs',
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, True),
            'barbar': False,  # Not called in doctests
            'foobar': False,  # Doctest failed before we called it
            '__init__': False,  # Doctests not profiled
            'instance_method': False,  # Doctests not profiled
        },
        expect_warnings=True,
        **{
            **dict.fromkeys(FUNCTION_NAMES, True),
            'baz': False,  # Cannot be profiled (dynam. defined)
            'foobar': False,  # Cannot be profiled (dynam. defined)
            # It's defined in `foo()`'s doctest and doesn't have its
            # own profiling entry
            'foofoo': False,
            'funcs': True,  # From the module doctest
            # Since we're only profiling `my_pkg.funcs`,
            # `my_pkg.classes`'s doctests aren't profiled
            'SomeClass': False,
        },
    )
    # Only profile `my_pkg.funcs.foo`
    run_check(
        '--autoprof-mod=my_pkg.funcs::foo',
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, False),
            'foo': True,
            'foofoo': True,
        },
        expect_warnings=False,
        **{
            **dict.fromkeys(FUNCTION_NAMES, False),
            'foofoo': False,
            'funcs': False,
            'foo': True,
        },
    )


@pytest.mark.skipif(
    (not HAS_PYTEST_DOCTEST_PLUS), reason='No `pytest_doctestplus`',
)
def test_doctest_plus(check: Checker) -> None:
    """
    Test that doctests are profiled when using
    `pytest_doctestplus.plugin` instead of `_pytest.doctest` to run
    them.

    Note
    ----
    A module-level (failing) doctest is skipped by `pytest_doctestplus`.
    """
    # Run with vanilla `_pytest.doctest`
    check(
        utils.CheckPytestConfig(
            test_count={'passed': 7, 'failed': 1},
            check_pytest_return_code=1,
        ),
        '--doctest-modules',
        '--autoprof-doctests',
        body_profiled=dict.fromkeys(FUNCTION_NAMES, False),
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, True),
            'barbar': False,
            'foobar': False,
        },
        expect_warnings=True,
        **{
            **dict.fromkeys(FUNCTION_NAMES, False),
            **dict.fromkeys(
                ('foo', 'bar', 'funcs', 'SomeClass', 'instance_method'), True,
            ),
        },
    )
    # Run with `pytest_doctestplus`, which skips the failing
    # `my_pkg.funcs` doctest
    check(
        utils.CheckPytestConfig(
            test_count=7,  # type: ignore[arg-type]
        ),
        '--doctest-modules',
        '--doctest-plus',
        '--autoprof-doctests',
        body_profiled=dict.fromkeys(FUNCTION_NAMES, False),
        call_profiled={
            **dict.fromkeys(FUNCTION_NAMES, True),
            **dict.fromkeys(('baz', 'barbar', 'foobar'), False),
        },
        expect_warnings=True,
        **{
            **dict.fromkeys(FUNCTION_NAMES, False),
            **dict.fromkeys(
                ('foo', 'bar', 'SomeClass', 'instance_method'), True,
            ),
        },
    )


@pytest.mark.skipif((not HAS_XDOCTEST), reason='No `xdoctest`')
@pytest.mark.parametrize('test_env_skip', [True, False, None])
def test_xdoctest(check: Checker, test_env_skip: Union[bool, None]) -> None:
    """
    Test that doctests are profiled when using `xdoctest.plugin` instead
    of `_pytest.doctest` to run them.

    Notes
    -----
    - A section of the doctest calling `foofoo()` is skipped by
      `xdoctest` when `test_env_skip` is true.
    - If `test_env_skip` is `None`, the doctest containing the
      `xdoctest` directive is not collected. This is useful for testing
      older `xdoctest` versions (< 0.14) where the `REQUIRES(env:...)`
      directive was illegal.
    """
    config = utils.CheckPytestConfig(
        test_count={'passed': 7, 'failed': 1}, check_pytest_return_code=1,
    )
    call_profiled = {
        **dict.fromkeys(FUNCTION_NAMES, True),
        'barbar': False,
        'foobar': False,
    }
    kwargs = {
        'body_profiled': dict.fromkeys(FUNCTION_NAMES, False),
        'call_profiled': call_profiled,
        'expect_warnings': True,
        **dict.fromkeys(FUNCTION_NAMES, False),
        **dict.fromkeys(
            ('foo', 'bar', 'funcs', 'SomeClass', 'instance_method'), True,
        ),
    }
    # Run with vanilla `_pytest.doctest`
    check(config, '--doctest-modules', '--autoprof-doctests', **kwargs)
    # Run with `xdoctest`, which skips the failing
    # `my_pkg.funcs` doctest, but only when `${MYXDOCTEST_CONT}` is set
    if not (test_env_skip is None or HAS_XDOCTEST_ENV_EFFECTS):
        version = ImportPath('xdoctest', '__version__').import_target()
        pytest.skip(
            f'`xdoctest` v{version} doesn\'t support '
            'the `REQUIRES(env:...)` directive'
        )
    with pytest.MonkeyPatch.context() as mp:
        # Since `--xdoctest` uses static analysis, it misses the two
        # non-profiled, dynamically-defined doctests which issue the
        # warning
        config.test_count['passed'] -= 2  # type: ignore[index]
        kwargs['expect_warnings'] = False
        flags = ['--xdoctest', '--autoprof-doctests']
        if test_env_skip:
            should_cont = 'false'
            # Note: partially skipped tests don't count as skipped in
            # `xdoctest`
            call_profiled['foofoo'] = False
        else:
            if test_env_skip is None:
                config.test_count['passed'] -= 1  # type: ignore[index]
                flags.extend(['-k', 'not foo'])
                # Since the `foo()` doctest is skipped:
                # - `foofoo()` has never been created, and is thus never
                #   called
                # - No timing info exists under `foo()`
                call_profiled['foofoo'] = kwargs['foo'] = False
            should_cont = 'true'
        mp.setenv('MYXDOCTEST_CONT', should_cont)
        check(config, *flags, **kwargs)
