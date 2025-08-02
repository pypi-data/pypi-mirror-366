"""
Tools used by the test suite;
meant for internal use only.
"""
import ast
import contextlib
import dataclasses
import functools
import importlib.util
import inspect
import os
import pathlib
import re
import shlex
import shutil
import sys
import textwrap
import types
import uuid
from itertools import chain
from operator import contains
from warnings import WarningMessage

import pytest

from . import _test_util_capture_warnings
from ._typing import (
    TYPE_CHECKING,
    Dict, FrozenSet, List, Set, Tuple,
    Collection, Generator, Iterable, Mapping, Sequence,
    Callable, ParamSpec,
    DefaultDict, TypedDict,
    Annotated, Any, Self, Type,
    Literal, Union, Optional,
    cast, overload,
    ChainedIdentifier, Identifier, Parsable,
)

if TYPE_CHECKING:
    # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811
    # Somehow `mypy` doesn't realize that `Config` and `RunResult` are
    # now public names...
    from _pytest.config import Config
    from _pytest.pytester import RunResult
else:
    from pytest import (  # type: ignore[no-redef] # noqa: F811
        Config, RunResult,
    )


__all__ = (
    'CheckPytestConfig',
    'CheckPytestResult',
    'TestEnvironment',
    'strip',
    'write_script',
    'parse_locs',
    'parse_profiler_output_lines',
    'find_line_locations',
    'environment_fixture',
    'propose_name',
    'check_pytest',
)

PS = ParamSpec('PS')
DefNode = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
_LineLocations = Dict[
    Tuple[pathlib.Path, Annotated[str, ChainedIdentifier]], Set[int]
]
LineLocations = Mapping[
    Tuple[pathlib.Path, Annotated[str, ChainedIdentifier]], FrozenSet[int]
]
_Paths = Union[
    pathlib.Path,
    Annotated[str, Parsable[pathlib.Path]],
    Sequence[pathlib.Path],
    Sequence[Annotated[str, Parsable[pathlib.Path]]],
]
_TestEnvironment = Tuple[_Paths, _Paths]


@dataclasses.dataclass
class TestEnvironment:
    """
    Parameters/Attributes
    ---------------------
    paths (default: ())
        Directories which should be added to `sys.path` to make the
        written packages import-able
    tests (default: ())
        Path(s) where the tests are located
    locs (default: mappingproxy())
        Mapping with keys `(path/to/file, func_name)` and values
        `frozenset[expected_line_number]`
    """
    __test__ = False
    paths: Tuple[pathlib.Path, ...] = ()
    tests: Tuple[pathlib.Path, ...] = ()
    # Note: check for default-value hashability was added in Python 3.11
    # and `mappingproxy` was made hashable in 3.12, so anything in
    # between will complain about a default of `mappingproxy({})`;
    # so just use a `dict` as the default factory (doesn't matter anyway
    # since we practically only instantiate this class with
    # `.from_paths_and_tests()`, which explicitly passes a value for
    # `.locs`)
    locs: LineLocations = dataclasses.field(default_factory=dict)

    def __post_init__(self, *args, **kwargs) -> None:
        self.paths = _normalize_paths(self.paths)
        self.tests = _normalize_paths(self.tests)
        if not self.tests:
            raise ValueError('`.tests` cannot be empty')
        self.locs = _freeze_line_location(self.locs)

    @classmethod
    def from_paths_and_tests(
        cls,
        paths: Optional[_Paths] = None,
        tests: Optional[_Paths] = None,
    ) -> Self:
        paths = paths or []
        tests = tests or []
        return cls(
            paths, tests,  # type: ignore[arg-type]
            find_line_locations(paths, tests),
        )


_PytestOutcomeKey = Literal[
    'passed',
    'skipped',
    'failed',
    'errors',
    'xpassed',
    'xfailed',
    'warnings',
    'deselected',
]


class _PytestOutcome(TypedDict, total=False):
    passed: int
    skipped: int
    failed: int
    errors: int
    xpassed: int
    xfailed: int
    warnings: int
    deselected: int


@overload
def _outcome_from_counts(
    passed: Union[Mapping[_PytestOutcomeKey, int], _PytestOutcome],
) -> _PytestOutcome:
    ...


@overload
def _outcome_from_counts(
    passed: Optional[int] = None,
    skipped: Union[int, None] = 0,
    failed: Union[int, None] = 0,
    errors: Union[int, None] = 0,
    xpassed: Union[int, None] = 0,
    xfailed: Union[int, None] = 0,
    warnings: Optional[int] = None,
    deselected: Optional[int] = None,
) -> _PytestOutcome:
    ...


def _outcome_from_counts(
    passed: Optional[Union[
        int, Mapping[_PytestOutcomeKey, int], _PytestOutcome,
    ]] = None,
    skipped: Union[int, None] = 0,
    failed: Union[int, None] = 0,
    errors: Union[int, None] = 0,
    xpassed: Union[int, None] = 0,
    xfailed: Union[int, None] = 0,
    warnings: Optional[int] = None,
    deselected: Optional[int] = None,
) -> _PytestOutcome:
    """
    Examples
    --------
    Normal use:

    >>> assert _outcome_from_counts(10) == {
    ...     'passed': 10, 'skipped': 0, 'failed': 0, 'errors': 0,
    ...     'xpassed': 0, 'xfailed': 0,
    ... }
    >>> assert _outcome_from_counts(passed=10, xfailed=5) == {
    ...     'passed': 10, 'failed': 0, 'skipped': 0, 'errors': 0,
    ...     'xfailed': 5, 'xpassed': 0,
    ... }

    Use a mapping to avoid implicitly setting the keys which default
    to 0:

    >>> assert _outcome_from_counts({
    ...     'passed': 10, 'xfailed': 5,
    ... }) == {'passed': 10, 'xfailed': 5}
    """
    d = {
        'passed': passed,
        'skipped': skipped,
        'failed': failed,
        'errors': errors,
        'xpassed': xpassed,
        'xfailed': xfailed,
        'warnings': warnings,
        'deselected': deselected,
    }
    d_: Dict[_PytestOutcomeKey, Union[int, None]]
    if isinstance(passed, Mapping):
        p = d.pop('passed')
        if TYPE_CHECKING:
            assert isinstance(p, Mapping)
        assert not any(d.values())
        d_ = dict(p)  # type: ignore[arg-type]
    else:
        d_ = d  # type: ignore[assignment]
    result: _PytestOutcome = {}
    for key, value in d_.items():
        if value is not None:
            result[key] = value
    return result


@dataclasses.dataclass
class CheckPytestConfig:
    """
    Parameters/Attributes
    ---------------------
    `pytest`-related:

    subprocess (default: False)
        If true, run `pytest` with `pytester.runpytest_subprocess()`;
        otherwise, use `pytester.runpytest_inprocess()`
    generate_config (default: False)
        If true, construct a `pytest.Config` object and attach it to the
        `CheckPytestResult` object returned by `check_pytest()`
    test_count (default: None)
        If an integer, assume that many tests and that they all pass;
        if a mapping (with keys 'passed', 'failed', 'warnings', etc.,
        and integer values), assume that many
        integer values)
    check_pytest_return_code (default: 0)
        If an integer, check `pytest`'s return code against it
    capture_reported_warnings (default: False)
        If true, capture the warnings reported by `pytester`;
        if a warning type or types, only capture those warnings

    `line_profiler`-related:

    no_profiling (default: False)
        If true, profiling output is not expected
    view_profiling_results (default: False)
        If true, instead of calling `python -m line_profiler` in a
        subprocess after writing the `.lprof` file, use the
        `--autoprof-view` flag to have `pytest` output the results
    profiling_flags (default: None)
        Optional strings representing command-line arguments to be
        passed to `python -m line_profiler`
    check_line_nums (default: True)
        If true, parse the `python -m line_profiler` output to check if
        the line-number attributions are valid
    check_lines_have_hits (default: False)
        If true, parse the `python -m line_profiler` output to check if
        the profiler has seen line events on the profiled functions
    check_line_profiler_return_code (default: 0)
        If an integer, check `python -m line_profiler`'s return code
        against it
    """
    subprocess: bool = False
    generate_config: bool = False
    test_count: Optional[_PytestOutcome] = None
    check_pytest_return_code: Union[int, None] = 0
    capture_reported_warnings: Union[
        bool, Type[Warning], Collection[Type[Warning]],
    ] = False

    no_profiling: bool = False
    view_profiling_results: bool = False
    check_line_nums: bool = True
    check_lines_have_hits: bool = False
    profiling_flags: Optional[Sequence[str]] = None
    check_line_profiler_return_code: Union[int, None] = 0

    def __post_init__(self) -> None:
        self._check_count()
        self._normalize_warnings()
        self._normalize_flags()

    def replace(self, **attrs) -> Self:
        d = dataclasses.asdict(self)
        for name, value in d.items():
            try:
                d[name] = attrs[name]
            except KeyError:
                pass
            else:
                continue
            try:
                d[name] = value.copy()  # type: ignore[attr-defined]
            except (AttributeError, TypeError):
                pass
        return type(self)(**d)

    def _normalize_warnings(self) -> None:
        warnings: Collection[Type[Warning]]
        if self.capture_reported_warnings in (True, False):
            warnings = [Warning] if self.capture_reported_warnings else []
        elif (
            isinstance(self.capture_reported_warnings, type)
            and issubclass(self.capture_reported_warnings, Warning)
        ):
            warnings = self.capture_reported_warnings,
        else:
            if TYPE_CHECKING:  # Help `mypy`
                assert not isinstance(self.capture_reported_warnings, bool)
            warnings = self.capture_reported_warnings
        self.capture_reported_warnings = tuple(warnings)

    def _normalize_flags(self) -> None:
        self.profiling_flags = list(self.profiling_flags or [])

    def _check_count(self) -> None:
        if self.test_count is None:
            return
        self.test_count = counts = _outcome_from_counts(self.test_count)
        if self.check_pytest_return_code != 0:
            return
        # If we're here, `pytest` isn't alloed to fail
        if counts.get('failed') or counts.get('errors'):
            raise ValueError(
                f'.test_count = {counts!r}, .check_pytest_return_code = 0: '
                'incompatible values'
            )


@dataclasses.dataclass
class CheckPytestResult:
    """
    Parameters/Attributes
    ---------------------
    pytest
        `pytest.RunResult` of the `pytest` call
    line_profiler
        `pytest.RunResult` of the `python -m line_profiler` call, or
        `None` if no profiling file is written
    config
        `pytest.Config` object corresponding to the `pytest` call
        (constructed from the same arguments passed to
        `pytest.Pytester.runpytest()`), or `None` if it isn't requested
        via `CheckPytestConfig.generate_config`
    reported_warnings
        `warnings.WarningMessage` objects captured in the `pytest` call
    """
    pytest: RunResult
    line_profiler: Optional[RunResult] = None
    config: Optional[Config] = None
    reported_warnings: List[WarningMessage] = dataclasses.field(
        default_factory=list,
    )


class _FindDefs(ast.NodeVisitor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.defs = {}

    def _visit_definition(self, node: DefNode) -> None:
        self.defs.setdefault(node.name, set()).add(
            min(child.lineno for child in (node, *node.decorator_list))
        )
        return self.generic_visit(node)

    visit_FunctionDef = visit_AsyncFunctionDef = _visit_definition
    visit_ClassDef = _visit_definition

    @classmethod
    def locate_definitions(
        cls, file: Union[pathlib.Path, str],
    ) -> LineLocations:
        visitor = cls()
        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)
        with file.open() as fobj:
            module = ast.parse(fobj.read())
        visitor.visit(module)
        defs = visitor.defs
        # Module-level doctests are named after the module, so add an
        # entry for that too
        if (
            module.body and
            isinstance(getattr(module.body[0], 'value', None), ast.Constant) and
            isinstance(
                module.body[0]
                .value.value,  # type: ignore[attr-defined]
                str,
            )
        ):
            name = file.name
            if name.endswith('.py'):
                name = name[:-len('.py')]
            defs.setdefault(name, set()).add(1)
        return _freeze_line_location({
            (file, func_name): line_nums
            for func_name, line_nums in defs.items()
        })

    defs: Dict[Annotated[str, ChainedIdentifier], Set[int]]


def strip(s: str) -> str:
    """
    Parameters
    ----------
    s
        String

    Return
    ------
    Stripped and dedented string
    """
    return textwrap.dedent(s).strip('\n')


def write_script(
    script: pathlib.Path, content: Optional[str] = None,
) -> pathlib.Path:
    """
    Parameters
    ----------
    script
        `pathlib.Path` to the file
    content
        Optional content to write thereto;
        if `None`, just `touch` the file

    Return
    ------
    `script`
    """
    script.parent.mkdir(parents=True, exist_ok=True)
    if content:
        script.write_text(strip(content))
    else:
        script.touch()
    return script


def _normalize_paths(paths: _Paths) -> Tuple[pathlib.Path, ...]:
    Path = pathlib.Path
    try:
        return Path(paths),  # type: ignore[arg-type]
    except TypeError:
        pass
    assert isinstance(paths, Sequence)
    return tuple(Path(p) for p in paths)


def find_line_locations(*paths: _Paths) -> LineLocations:
    """
    Parameters
    ----------
    *paths
        Python script(s) and/or directory/-ies containing them

    Return
    ------
    Dictionary with keys `(path/to/file, func_name)` and values
    `set[expected_line_number]`
    """
    sources: Iterable[pathlib.Path]
    locs: _LineLocations = {}
    path: pathlib.Path
    find_defs = _FindDefs.locate_definitions
    for path in set(sum((_normalize_paths(p) for p in paths), ())):
        if path.is_file() and path.match('*.py'):
            sources = [path]
        elif path.is_dir():
            sources = path.glob('**/*.py')
        else:
            continue
        for source in sources:
            locs.update(
                (key, set(value)) for key, value in find_defs(source).items()
            )
    return _freeze_line_location(locs)


@overload
def environment_fixture(
    fixture: None = None, /, *,
    setup_scope: Optional[
        Literal['session', 'package', 'module', 'class', 'function']
    ] = None,
    **kwargs
) -> Callable[
    [
        Union[
            Callable[PS, Tuple[_Paths, _Paths]],
            Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
        ]
    ],
    Callable[PS, Generator[TestEnvironment, None, None]]
]:
    ...


@overload
def environment_fixture(
    fixture: Union[
        Callable[PS, Tuple[_Paths, _Paths]],
        Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
    ],
    /,
    *,
    setup_scope: Optional[
        Literal['session', 'package', 'module', 'class', 'function']
    ] = None,
    **kwargs
) -> Callable[PS, Generator[TestEnvironment, None, None]]:
    ...


def environment_fixture(
    fixture: Optional[
        Union[
            Callable[PS, Tuple[_Paths, _Paths]],
            Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
        ]
    ] = None,
    /,
    *,
    setup_scope: Optional[
        Literal['session', 'package', 'module', 'class', 'function']
    ] = None,
    **kwargs
) -> Union[
    Callable[
        [
            Union[
                Callable[PS, Tuple[_Paths, _Paths]],
                Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
            ]
        ],
        Callable[PS, Generator[TestEnvironment, None, None]]
    ],
    Callable[PS, Generator[TestEnvironment, None, None]]
]:
    """
    Parameters
    ----------
    fixture()
        Fixture function to decorate, which should return or yield in a
        2-tuple:
        - Directory/-ies which should be added to `sys.path` to make the
          written packages import-able
        - Path(s) where the tests are located
    setup_scope
        Optional scope which should be broader than
        `kwargs.get('scope', 'function')`;
        if provided, `fixture()` will be shunted to a separate setup
        fixture with said scope, while the returned fixture refers to
        said setup fixture.
    **kwargs
        Passed to `@pytest.fixture`

    Return
    ------
    Decorated fixture function which yields:
    - Directories which should be added to `sys.path` to make the
      written packages import-able
    - Paths where the tests are located
    - Mapping with keys `(path/to/file, func_name)` and values
      `frozenset[expected_line_number]`
    When using said fixture, the directories are prepended to `sys.path`
    via monkey-patching.
    """
    if fixture is None:
        return functools.partial(  # type: ignore[return-value]
            environment_fixture, **kwargs, setup_scope=setup_scope,
        )

    @overload
    def wrap_call(
        patch_sys_path: bool,
        process: Literal[True],
        fixture: Union[
            Callable[PS, Tuple[_Paths, _Paths]],
            Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
        ],
        /,
        *args,
        **kwargs
    ) -> Generator[TestEnvironment, None, None]:
        ...

    @overload
    def wrap_call(
        patch_sys_path: bool,
        process: Literal[False],
        fixture: Union[
            Callable[PS, TestEnvironment],
            Callable[PS, Generator[TestEnvironment, None, None]],
        ],
        /,
        *args,
        **kwargs
    ) -> Generator[TestEnvironment, None, None]:
        ...

    def wrap_call(
        patch_sys_path: bool,
        process: bool,
        fixture: Union[
            Callable[PS, Tuple[_Paths, _Paths]],
            Callable[PS, Generator[Tuple[_Paths, _Paths], None, None]],
            Callable[PS, TestEnvironment],
            Callable[PS, Generator[TestEnvironment, None, None]],
        ],
        /,
        *args,
        **kwargs
    ) -> Generator[TestEnvironment, None, None]:
        # Get result
        if inspect.isgeneratorfunction(fixture):
            gen = fixture(*args, **kwargs)
            result = next(gen)
        else:
            gen = None
            result = fixture(*args, **kwargs)
        # Process, add to path, yield
        if process:
            result = TestEnvironment.from_paths_and_tests(*result)
        with (
            pytest.MonkeyPatch.context()
            if patch_sys_path else
            contextlib.nullcontext()
        ) as mp:
            if mp:
                for path in reversed(result.paths):
                    mp.syspath_prepend(path)
            yield result
            # Trigger cleanup by exhausting the generator
            for _ in (() if gen is None else gen):
                pass

    class SigReplaceArgs(TypedDict, total=False):
        parameters: Sequence[inspect.Parameter]
        return_annotation: Any

    sig = inspect.signature(fixture)
    replacements: SigReplaceArgs = {'return_annotation': TestEnvironment}
    fixture_scope = kwargs.get('scope', 'function')
    if fixture_scope == setup_scope:
        setup_scope = None

    if setup_scope is None:
        @functools.wraps(fixture)
        def wrapper(*args, **kwargs):
            yield from wrap_call(True, True, fixture, *args, **kwargs)

        wrapper.__signature__ = (  # type: ignore[attr-defined]
            sig.replace(**replacements)
        )
        return pytest.fixture(wrapper, **kwargs)

    fixture_order = 'session', 'package', 'module', 'class', 'function'
    if fixture_order.index(setup_scope) > fixture_order.index(fixture_scope):
        pytest.fail(
            f'ScopeMismatch: cannot wrap a {setup_scope!r} fixture '
            f'with a {fixture_scope!r} one',
        )

    @functools.wraps(fixture)
    def inner_wrapper(*args, **kwargs):
        # This processes the fixture output in the final value the
        # outer fixture should yield, yields it, but avoids doing the
        # monkey-patching
        yield from wrap_call(False, True, fixture, *args, **kwargs)

    inner_wrapper.__signature__ = (  # type: ignore[attr-defined]
        sig.replace(**replacements)
    )
    inner_wrapper.__name__ = inner_name = '_' + inner_wrapper.__name__
    inner_fixture = pytest.fixture(
        inner_wrapper, **{**kwargs, 'scope': setup_scope},
    )

    # Seek to the last module-scoped frame and insert the inner fixture
    # there
    frame = inspect.currentframe()
    while frame:
        if frame.f_locals is not frame.f_globals:
            frame = frame.f_back
            if frame is None:
                pytest.fail(
                    'reached frame stack bottom without finding a '
                    'module-scoped frame'
                )
            continue
        namespace = frame.f_locals
        del frame
        if inner_name in namespace:
            pytest.fail(
                'module at file {} already defines the name `{}`'
                .format(namespace.get('__file__', '???'), inner_name)
            )
        namespace[inner_name] = inner_fixture
        del namespace
        break

    @functools.wraps(fixture)
    def outer_wrapper(*args, **kwargs):
        # This just yields the output yielded from the inner fixture,
        # and handles the monkey-patching of `sys.path`
        fixture_value, = outer_wrapper.__signature__.bind(*args, **kwargs).args
        yield from wrap_call(True, False, lambda: (yield fixture_value))

    replacements['parameters'] = [inspect.Parameter(
        inner_name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=TestEnvironment,
    )]
    outer_wrapper.__signature__ = (  # type: ignore[attr-defined]
        sig.replace(**replacements)
    )
    return pytest.fixture(outer_wrapper, scope=fixture_scope)


def _freeze_line_location(
    locs: Union[_LineLocations, LineLocations],
) -> LineLocations:
    return types.MappingProxyType({
        key: frozenset(value) for key, value in locs.items()
    })


def parse_locs(line_profiler_output: str) -> LineLocations:
    r"""
    Example
    -------
    >>> from pathlib import Path
    >>>
    >>>
    >>> filename = Path('my') / 'file.py'
    >>> func_name = 'foo_bar'
    >>> lineno = 50
    >>> output = (
    ...     f'File: {filename!s}\n'
    ...     f'Function: {func_name} at line {lineno}'
    ... )
    >>> assert parse_locs(output) == {(filename, func_name): {lineno}}
    """
    result: _LineLocations = {}
    Path = pathlib.Path
    find = LINE_PROFILER_FUNCTION_FULL_LOCATION_PATTERN.findall
    for filename, func_name, lineno in find(line_profiler_output):
        result.setdefault((Path(filename), func_name), set()).add(int(lineno))
    return _freeze_line_location(result)


def parse_profiler_output_lines(
    output_lines: Iterable[str],
) -> Dict[
    Tuple[
        str,  # filename
        int,  # 1st lineno
        Annotated[str, ChainedIdentifier],  # func .__[qual]name__
    ],
    List[Tuple[int, int, float]]  # lineno, nhits, time
]:
    r"""
    Example
    -------
    >>> lines = '''
    ... Timer unit: 1e-09 s
    ...
    ... Total time: 1.1e-05 s
    ... File: FOO.py
    ... Function: f at line 1
    ...
    ... Line #      Hits         Time  Per Hit   % Time  Line Contents
    ... ==============================================================
    ...      1                                           def f(x, y):
    ...      2        79         11.0      0.1    100.0      foo
    ...
    ... Total time: 5.2e-05 s
    ... File: BAR.py
    ... Function: Foo.g at line 11
    ...
    ... Line #      Hits         Time  Per Hit   % Time  Line Contents
    ... ==============================================================
    ...     11                                           def g():
    ...     12         1      14000.0  14000.0     26.0      bar
    ...     13         1      16000.0  16000.0     30.0      baz
    ...     14         1      22000.0  22000.0     42.5      foobar
    ...
    ... Total time: 4.4e-05 s
    ... File: BAR.py
    ... Function: h at line 17
    ...
    ... Line #      Hits         Time  Per Hit   % Time  Line Contents
    ... ==============================================================
    ...     17                                           def h():
    ...     18         1      27000.0  27000.0     61.5      spam
    ...     19         1      17000.0  17000.0     38.5      eggs
    ...
    ...   0.00 seconds - FOO.py:1 - f
    ...   0.00 seconds - BAR.py:11 - Foo.g
    ...   0.00 seconds - BAR.py:17 - h
    ... '''
    >>> parse_profiler_output_lines(
    ...     lines.splitlines(),  # doctest: +NORMALIZE_WHITESPACE
    ... )
    {('FOO.py', 1, 'f'): [(2, 79, 11.0)],
     ('BAR.py', 11, 'g'): [(12, 1, 14000.0), (13, 1, 16000.0),
                           (14, 1, 22000.0)],
     ('BAR.py', 17, 'h'): [(18, 1, 27000.0), (19, 1, 17000.0)]}
    """
    is_seeing_data = False

    def write_entries() -> None:
        nonlocal is_seeing_data
        is_seeing_data = False
        results[filename, int(firstlineno), func_name] = entries.copy()
        entries.clear()
        stops.clear()

    headers = ['Line #', 'Hits', 'Time', 'Per Hit', '% Time']
    results: Dict[
        Tuple[str, int, Annotated[str, ChainedIdentifier]],
        List[Tuple[int, int, float]]
    ] = {}
    filename = ''
    firstlineno = ''
    func_name = ''
    entries: List[Tuple[int, int, float]] = []
    stops: List[int] = []
    for line in output_lines:
        if line.startswith('File: '):
            filename = line[len('File: '):]
            continue
        elif line.startswith('Function: '):
            match = LINE_PROFILER_FUNCTION_LINE_PATTERN.match(line)
            assert match
            func_name, firstlineno = match.groups()
            continue
        elif line.startswith('Line #'):
            stops[:] = (line.index(header) + len(header) for header in headers)
            continue
        elif (not line) or line.isspace():
            continue
        elif set(line) == {'='}:
            is_seeing_data = True
            continue
        # Parse the timing lines
        if not stops:
            continue
        try:
            lineno = int(line[:stops[0]])
            maybe_nhits = line[stops[0]:stops[1]]
            if maybe_nhits.isspace():  # No data on this line
                continue
            nhits = int(maybe_nhits)
            time = float(line[stops[1]:stops[2]])
            entries.append((lineno, nhits, time))
        except ValueError:
            write_entries()
    if entries:
        write_entries()
    return results


def _check_existence_in_output(
    func_is_profiled: Mapping[Annotated[str, Identifier], bool],
    args: Sequence[str],
    result_lines: Iterable[str],
) -> None:
    """
    Check if the right functions are present in the
    `python -m line_profiler` output.
    """
    failures: List[str] = []
    for name, profiled in func_is_profiled.items():
        match = re.compile(
            r' *[0-9]+\.[0-9]+ +seconds - .*:[0-9]+ - '
            rf'(?:.+\.)?{name}$',
        ).match
        found = any(match(line) for line in result_lines)
        if found == profiled:
            continue
        failures.append(
            '{}(): {} expected'
            .format(name, 'presence' if profiled else 'absence')
        )
    if failures:
        raise AssertionError('\n'.join((
            'pytest {} -> {} failure(s) '
            '(presence in `line_profiler` summary):'
            .format(shlex.join(args), len(failures)),
            *('- ' + line for line in failures),
        )))


def _check_line_num_attrib(
    func_is_profiled: Mapping[Annotated[str, Identifier], bool],
    args: Sequence[str],
    result: str,
    locs: LineLocations,
    repr_path: Callable[[Union[pathlib.PurePath, str]], str],
) -> None:
    """
    Check whether line events are attributed to the right functions/code
    blocks.
    """
    failures: DefaultDict[
        Annotated[str, ChainedIdentifier], List[str]
    ] = DefaultDict(list)
    attributions = parse_locs(result)
    for name in (n for n, p in func_is_profiled.items() if p):
        matches: Dict[pathlib.Path, Set[int]] = {
            path: set(lines) for (path, func), lines in attributions.items()
            if func == name
        }
        if not matches:
            failures[name].append('not found')
            continue
        for path, lines in matches.items():
            try:
                expected_lines = locs[path, name]
            except KeyError:
                failures[name].append(
                    'found in unexpected file {}'
                    .format(shlex.quote(repr_path(path)))
                )
                continue
            if lines <= expected_lines:
                continue
            failures[name].append(
                'in file {}: '
                'attributed to unexpected lines {!r} (expected {!r})'
                .format(
                    shlex.quote(repr_path(path)),
                    lines - expected_lines,
                    expected_lines,
                )
            )
    if failures:
        raise AssertionError('\n'.join((
            'pytest {} -> {} failure(s) '
            '(`line_profiler` line-location attributions):'
            .format(shlex.join(args), len(failures)),
            *(
                '- {}: {}'.format(name, '; '.join(reasons))
                for name, reasons in failures.items()
            ),
        )))


def _check_line_has_hits(
    func_is_profiled: Mapping[Annotated[str, Identifier], bool],
    args: Sequence[str],
    result_lines: Iterable[str],
) -> None:
    """
    Check whether the profiler actually recorded any hits with the
    functions it is supposed to have profiled.
    """
    funcs_with_data: Set[Annotated[str, ChainedIdentifier]] = {
        name
        for (*_, name), entries
        in parse_profiler_output_lines(result_lines).items()
        if entries
    }
    failures: Set[str] = set()
    for name, profiled in func_is_profiled.items():
        if profiled == (name in funcs_with_data):
            continue
        failures.add(
            '{}(): {} data expected'
            .format(name, 'profiling' if profiled else 'no profiling')
        )
    if failures:
        raise AssertionError('\n'.join((
            'pytest {} -> {} failure(s) '
            '(presence of actual profiling data):'
            .format(shlex.join(args), len(failures)),
            *('- ' + line for line in sorted(failures)),
        )))


def propose_name(
    template: Annotated[str, Identifier] = 'nonexistent_module',
    guard: Optional[Callable[[Annotated[str, Identifier]], Any]] = None,
) -> Generator[Annotated[str, Identifier], None, None]:
    """
    Generate names that don't correspond to preexisting modules.
    Alternatively, `guard()` can be another callable which takes a name
    and returns a truey object if it is unsuitable (e.g. if it clashes
    with existing resources).
    """
    if guard is None:
        guard = importlib.util.find_spec
    while True:
        target = '_'.join([template, *str(uuid.uuid4()).split('-')])
        if not guard(target):
            yield target


def _write_warning_capturing_plugin_module(
    tempdir: pathlib.Path,
) -> Annotated[str, Identifier]:
    module_name = next(propose_name('my_warning_capturing_plugin'))
    module_file = tempdir / (module_name + '.py')
    assert not module_file.exists()
    fname = _test_util_capture_warnings.__file__
    assert isinstance(fname, str)
    shutil.copy(fname, module_file)
    return module_name


def check_pytest(
    pytester: pytest.Pytester,
    environment: TestEnvironment,
    config: Optional[CheckPytestConfig] = None,
    /,
    *args: str,
    **func_is_profiled: bool,
) -> CheckPytestResult:
    """
    Run `pytest` in a defined environment and check the profiling
    output.

    Parameters
    ----------
    pytester
        `pytest.Pytester`
    environment
        `TestEnvironment`, as yielded from a fixture decorated with
        `@environment_fixture`
    config
        Optional `CheckPytestConfig`
    *args
        Passed to `pytester.runpytest()`
    **func_is_profiled
        Whether a function of the corresponding name should be present
        in the `python -m line_profiler` output

    Return
    ------
    Object containg the following fields:
    - `.pytest`: `pytest.RunResult` of `pytest ...`
    - `.line_profiler`: `pytest.RunResult` of
      `python -m line_profiler ...`, or `None` if it wasn't run
    """
    def syspath_extend(
        mp: pytest.MonkeyPatch,
        paths: Sequence[Union[str, pathlib.PurePath]],
    ) -> None:
        all_paths = [str(p) for p in paths]
        assert config is not None
        if config.subprocess:
            if os.environ.get('PYTHONPATH'):
                all_paths.insert(0, os.environ['PYTHONPATH'])
            mp.setenv('PYTHONPATH', ':'.join(all_paths))
        else:
            sys.path.extend(all_paths)

    prof_outfile = 'out.lprof'
    rp: Callable[
        [Union[pathlib.PurePath, str]], str
    ] = functools.partial(os.path.relpath, start=pytester.path)
    ctx_callbacks: List[Callable[[pytest.MonkeyPatch], None]] = []
    plugins: List[str] = []

    if isinstance(config, str):
        args = (config, *args)
        config = None
    if config is None:
        config = CheckPytestConfig()

    if config.subprocess:
        runner = pytester.runpytest_subprocess
        ctx_callbacks.append(
            functools.partial(syspath_extend, paths=environment.paths),
        )
    else:
        # No need to manipulate `sys.path` here, the `env` fixture has
        # already done that
        runner = pytester.runpytest_inprocess

    if config.capture_reported_warnings:
        # Use a plugin module generated on-the-fly to handle the
        # capturing of warnings
        already_exists = functools.partial(contains, os.listdir(pytester.path))
        tempdir_name = next(propose_name('my_temp_path', guard=already_exists))
        tempdir = pytester.mkdir(tempdir_name)
        ctx_callbacks.append(
            functools.partial(syspath_extend, paths=[tempdir]),
        )
        cap_module_name = _write_warning_capturing_plugin_module(tempdir)
        plugins.append(cap_module_name)

    lprof_path = pytester.path / prof_outfile
    options = [*args, '--autoprof-outfile=' + prof_outfile]
    tests = [str(test) for test in environment.paths + environment.tests]
    if config.view_profiling_results:
        opts: List[str] = (
            config.profiling_flags  # type: ignore[assignment]
        )
        options.append('--autoprof-view=' + ' '.join([*opts, '--summarize']))
    args = tuple(chain(
        options,
        (arg for p in plugins for arg in ('-p', p)),
        tests,
    ))

    try:
        warnings: List[WarningMessage] = []
        config_result: Union[pytest.Config, None] = None

        with pytest.MonkeyPatch.context() as mp:
            for callback in ctx_callbacks:
                callback(mp)
            pytest_result = runner(*args)
            # Pull the captured warnings from the temporary module
            if config.capture_reported_warnings:
                cap_mod = importlib.import_module(cap_module_name)
                warning_types = cast(
                    Tuple[Type[Warning], ...], config.capture_reported_warnings,
                )
                warnings.extend(
                    w for w in cap_mod.retrieve_warnings()
                    if issubclass(w.category, warning_types)
                )

        if config.generate_config:
            config_result = pytester.parseconfig(*args)
        get_result = functools.partial(
            CheckPytestResult, pytest_result,
            config=config_result, reported_warnings=warnings,
        )

        if config.check_pytest_return_code is not None:
            assert pytest_result.ret == config.check_pytest_return_code
        if config.test_count is not None:
            pytest_result.assert_outcomes(**config.test_count)
        if config.no_profiling:
            assert not lprof_path.exists()
            return get_result()

        # Check the profiling
        assert lprof_path.exists()
        # - Existence of the target functions in the profiling report
        if config.view_profiling_results:
            lp_result = pytest_result
        else:
            lp_result = pytester.run(
                sys.executable, '-m', 'line_profiler',
                *(config.profiling_flags or []), '--summarize',
                '--', prof_outfile,
            )
            if config.check_line_profiler_return_code is not None:
                assert lp_result.ret == config.check_line_profiler_return_code
        _check_existence_in_output(func_is_profiled, args, lp_result.outlines)
        # - Attribution of their line numbers
        if config.check_line_nums:
            _check_line_num_attrib(
                func_is_profiled,
                args,
                str(lp_result.stdout),
                environment.locs,
                rp,
            )
        # - Existence of line events
        if config.check_lines_have_hits:
            _check_line_has_hits(func_is_profiled, args, lp_result.outlines)
        return get_result(lp_result)
    finally:  # Prevent pollution
        lprof_path.unlink(missing_ok=True)


_LINE_PROFILER_FUNCTION_LINE = strip(r"""
^Function: (?:.+\.)?(?P<func_name>\w+) at line (?P<lineno>[0-9]+)$
""")
LINE_PROFILER_FUNCTION_LINE_PATTERN = re.compile(
    _LINE_PROFILER_FUNCTION_LINE,
)
LINE_PROFILER_FUNCTION_FULL_LOCATION_PATTERN = re.compile(
    '{}\n{}'.format(
        r'^File: (?P<filename>.+\.py)$', _LINE_PROFILER_FUNCTION_LINE,
    ),
    re.MULTILINE,
)
