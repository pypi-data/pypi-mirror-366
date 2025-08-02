import functools
import importlib
import io
import pathlib
import re
import types

import line_profiler
import pytest

from pytest_autoprofile._typing import Dict, Callable, Union
from pytest_autoprofile._test_utils import strip
from pytest_autoprofile.profiler import LineProfiler


@pytest.fixture
def test_module(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    path = (
        pathlib.Path(__file__).parent
        / 'test-modules-and-tests'
        / 'test_profiler'
    )
    monkeypatch.syspath_prepend(str(path))
    return importlib.import_module('profiler_test_module')


@pytest.mark.parametrize('double_add', [True, False])
def test_profiling_classmethod(
    get_line_profiler: Callable[..., LineProfiler], double_add: bool,
) -> None:
    """
    Test `LineProfiler.wrap_classmethod()`.
    """
    profile = get_line_profiler()

    class Object:
        @profile
        @classmethod
        def foo(cls) -> str:
            return cls.__name__ * 2

    if double_add:
        profile.add_imported_function_or_module(Object)
    assert profile.object_count == 1
    assert Object.foo() == Object().foo() == 'ObjectObject'
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    # Check that we have profiled `Object.foo()`
    assert re.search(r'- (?:.+\.)?foo$', output)
    line, = (line for line in output.splitlines() if line.endswith('* 2'))
    # Check that it has been run twice
    assert int(line.split()[1]) == 2


@pytest.mark.parametrize('double_add', [True, False])
def test_profiling_staticmethod(
    get_line_profiler: Callable[..., LineProfiler], double_add: bool,
) -> None:
    """
    Test `LineProfiler.wrap_staticmethod()`.
    """
    profile = get_line_profiler()

    class Object:
        @profile
        @staticmethod
        def bar(x: int) -> int:
            return x * 2

    if double_add:
        profile.add_imported_function_or_module(Object)
    assert profile.object_count == 1
    assert Object.bar(3) == Object().bar(3) == 6
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    # Check that we have profiled `Object.bar()`
    assert re.search(r'- (?:.+\.)?bar$', output)
    line, = (line for line in output.splitlines() if line.endswith('* 2'))
    # Check that it has been run twice
    assert int(line.split()[1]) == 2


@pytest.mark.parametrize('double_add', [True, False])
def test_profiling_property(
    get_line_profiler: Callable[..., LineProfiler], double_add: bool,
) -> None:
    """
    Test `LineProfiler.wrap_property()`.
    """
    profile = get_line_profiler()

    class Object:
        def __init__(self, x: int) -> None:
            self.x = x

        @profile  # type: ignore[prop-decorator]
        @property
        def baz(self) -> int:
            return self.x * 2

    if double_add:
        profile.add_imported_function_or_module(Object)
    assert profile.object_count == (
        # Note: if we added the whole class, `__init__()` is also added
        2 if double_add else 1
    )
    assert Object(3).baz == 6
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    # Check that we have profiled `Object.baz`
    assert re.search(r'- (?:.+\.)?baz$', output)
    line, = (line for line in output.splitlines() if line.endswith('* 2'))
    # Check that it has been run once
    assert int(line.split()[1]) == 1


def test_profiling_boundmethod() -> None:
    """
    Test `LineProfiler.wrap_boundmethod()`.
    """
    profile = LineProfiler()

    class Object:
        def foobar(self, x: int) -> int:
            return id(self) * x

    obj = Object()
    # check that calls are aggregated
    profiled_foobar_1 = profile(obj.foobar)
    profiled_foobar_2 = profile(obj.foobar)
    assert isinstance(profiled_foobar_1, types.MethodType)
    assert isinstance(profiled_foobar_2, types.MethodType)
    assert profile.functions == [Object.foobar]
    assert (
        profiled_foobar_1(2)
        == profiled_foobar_2(2)
        == obj.foobar(2)
        == id(obj) * 2
    )
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    # Check that we have profiled `Object.foobar()`
    assert re.search(r'- (?:.+\.)?foobar$', output)
    line, = (line for line in output.splitlines() if line.endswith('* x'))
    # Check that the wrapped methods has been run twice in total
    assert int(line.split()[1]) == 2


def test_profiling_partial() -> None:
    """
    Test `LineProfiler.wrap_partial()`.
    """
    profile = LineProfiler()

    def foofoo(x: int, y: int) -> int:
        return x + y

    foofoo2 = functools.partial(foofoo, 2)
    profiled_foofoo2_1 = profile(foofoo2)
    profiled_foofoo2_2 = profile(foofoo2)
    assert isinstance(profiled_foofoo2_1, functools.partial)
    assert isinstance(profiled_foofoo2_2, functools.partial)
    assert profile.functions == [foofoo]
    assert (
        profiled_foofoo2_1(3)
        == profiled_foofoo2_2(3)
        == foofoo2(3)
        == foofoo(2, 3)
        == 5
    )
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    # Check that we have profiled `foofoo()`
    assert re.search(r'- (?:.+\.)?foofoo$', output)
    line, = (line for line in output.splitlines() if line.endswith('x + y'))
    # Check that the wrapped partials has been run twice in total
    assert int(line.split()[1]) == 2


def test_add_imported_function_or_module(
    get_line_profiler: Callable[..., LineProfiler],
    test_module: types.ModuleType,
) -> None:
    """
    Test our patch for `LineProfiler.add_imported_function_or_module()`.
    """
    profile = get_line_profiler()
    profile.add_imported_function_or_module(test_module)
    assert profile.object_count == 6
    assert test_module.foobar(2, 3) == 'Object' * 48
    assert test_module.spam(2) == 3
    assert test_module.eggs(5) == 'Object' * 40
    with io.StringIO() as sio:
        profile.print_stats(stream=sio, summarize=True)
        output = strip(sio.getvalue())
    lines = output.splitlines()
    failures: Dict[str, Union[str, int]] = {}
    expected_ncalls: Dict[str, int] = dict(
        # Note: we instantiated 3 `test_module.Object` objects, but
        # since one of the objects was instantiated in the module
        # namespace and before profiling happened, only two calls are
        # profiled
        __init__=2,
        # All these are called twice via `test_module.foobar()`
        foo=2, bar=2, baz=2, foobar=2,
        # This is called via `test_module.spam()`
        _spam=1,
    )
    for method, expected in expected_ncalls.items():
        # Check that we have profiled the method
        pattern = re.compile(rf'- (?:.+\.)?{method}$')
        if not any(pattern.search(line) for line in lines):
            failures[method] = 'ABS'
            continue
        # Check that it's been run the expected number of times
        ncalls = sum(
            int(line.split()[1]) for line in lines
            if line.endswith('  # ' + method)
        )
        if ncalls != expected:
            failures[method] = ncalls
    if failures:
        print('\n' + output)
        raise AssertionError(
            'number(s) of calls different from expected value(s): '
            + ', '.join(
                '{}: {} -> {}'.format(method, expected_ncalls[method], ncalls)
                for method, ncalls in failures.items()
            )
        )


@pytest.mark.parametrize('double_add', [True, False])
def test_global_profiler(
    get_line_profiler: Callable[..., LineProfiler], double_add: bool,
) -> None:
    """
    Test that the profiler is correctly added to the global
    `@line_profiler.profile` when `.install()`-ed.
    """
    profile = get_line_profiler(tee_global_prof='always')
    profile.install()
    try:
        class Object:
            @line_profiler.profile
            def foo(self, x: int) -> int:
                return id(self) * x

        if double_add:
            profile.add_imported_function_or_module(Object)
        assert profile.object_count == 1
        obj = Object()
        assert obj.foo(2) == id(obj) * 2
        with io.StringIO() as sio:
            profile.print_stats(stream=sio, summarize=True)
            output = strip(sio.getvalue())
        # Check that we have profiled `foo()`
        assert re.search(r'- (?:.+\.)?foo$', output)
        line, = (line for line in output.splitlines() if line.endswith('* x'))
        # Check that it has been run once
        assert int(line.split()[1]) == 1
    finally:
        profile.uninstall()


def test_multiple_profilers(
    get_line_profiler: Callable[..., LineProfiler],
) -> None:
    """
    Test that it is possible to use multiple profiler instances in the
    same interpretor as long as they are `.install()`-ed and
    `.uninstall()`-ed in order, so that names in class and module
    namespaces are restored to their pre-add states.

    Note
    ----
    This test is largely obsolete since it `line_profiler` PR 347 made
    it possible for multiple profilers to be used simultaneously.
    """
    class Object:
        @classmethod
        def method(cls, n: int) -> int:
            x = 0
            for n in range(1, n + 1):
                x += n
            return x

    def get_method_impl() -> types.FunctionType:
        return vars(Object)['method'].__func__

    original_method = get_method_impl()
    prof1 = get_line_profiler()
    prof2 = get_line_profiler()
    for prof, n in (prof1, 700), (prof2, 500):
        prof.install()
        try:
            prof.add_imported_function_or_module(Object)
            assert prof.functions == [original_method]
            assert get_method_impl() is not original_method
            assert Object.method(n) == n * (n + 1) / 2
        finally:
            prof.uninstall()
            assert get_method_impl() is original_method
        timings, = prof.get_stats().timings.values()
        *_, (_, nhits, _), _ = sorted(timings)
        assert nhits == n
