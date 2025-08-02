"""
Tests for AST rewriting.
"""
import ast
import types

import pytest

from pytest_autoprofile import _test_utils as utils, profiler, rewriting
from pytest_autoprofile._typing import (
    List, Set, Tuple,
    Callable, Generator,
    Annotated, Type, TypeVar,
    Union,
    Parsable, ImportPath,
)


@pytest.mark.parametrize(
    'rewrite_targets',
    [
        'my_module',
        'my_module::foo,my_module::Baz',
        'my_module::bar,my_module::Baz.a_class_method',
    ],
)
def test_module_rewrite_line_number_preservation(
    get_line_profiler: Callable[..., profiler.LineProfiler],
    rewrite_targets: Annotated[str, Parsable[ImportPath]],
) -> None:
    """
    Test that after rewriting the module with
    `~.rewriting.StrictModuleRewriter`, the line numbers as seen by the
    profiler are preserved.
    """
    DefNodes = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
    DEF_NODES = ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
    AST = TypeVar('AST', bound=ast.AST)

    def iter_nodes(
        node: ast.AST,
        NodeType: Union[Type[AST], Tuple[Type[AST], ...]],
    ) -> Generator[AST, None, None]:
        for node in ast.walk(node):
            if isinstance(node, NodeType):
                yield node  # type: ignore[misc]

    def find_defs(node: ast.AST) -> List[DefNodes]:
        return list(iter_nodes(node, DEF_NODES))

    def get_lineno(node: ast.AST) -> int:
        if not isinstance(node, DEF_NODES):
            return node.lineno  # type: ignore[attr-defined]
        return min(nd.lineno for nd in (node, *node.decorator_list))

    source = utils.strip("""
    import functools
    from typing import Collection, Sequence


    def foo(
        strings: Sequence[str], sep: str = ', ',
    ) -> str:
        return sep.join(strings)


    @functools.wraps(foo)
    def bar(strings: Collection[str], sep: str = ' ') -> str:
        return foo(sorted(strings), sep)


    class Baz:
        def __init__(self) -> None:
            pass

        @staticmethod
        def a_static_method(x: int) -> int:
            return x

        @staticmethod
        def a_class_method(cls, x: int, y: int = 127) -> int:
            for char in cls.__name__:
                x += ind(char)
                x <<= 1
                x %= y
            return x
    """)
    # Before manipulations
    module_ast = ast.parse(source)
    defs = find_defs(module_ast)
    locs = {node.name: get_lineno(node) for node in defs}
    # After rewriting
    transformer = rewriting.StrictModuleRewriter(
        'my_module', rewrite_targets=rewrite_targets,
    )
    transformed_ast = transformer(module_ast)
    defs = find_defs(transformed_ast)
    assert {node.name: get_lineno(node) for node in defs} == locs
    # After compilation
    rt: Set[str] = {str(ipath) for ipath in transformer.rewrite_targets}
    profile_entire_module = 'my_module' in rt
    profile_entire_class = 'my_module::Baz' in rt
    expected_in_profiler = {
        name: profile_entire_module or (
            'my_module::' + ('' if name in ('foo', 'bar') else 'Baz.') + name
            in rt
        )
        for name in locs if name != 'Baz'
    }
    for method in '__init__', 'a_static_method', 'a_class_method':
        expected_in_profiler[method] |= profile_entire_class
    module_obj = types.ModuleType('my_module')
    prof = get_line_profiler()
    module_obj.profile = prof  # type: ignore[attr-defined]
    fname = '<string>'
    exec(
        compile(transformed_ast, fname, 'exec'),
        module_obj.__dict__,
        module_obj.__dict__,
    )
    assert {func.__name__ for func in prof.functions} == {
        name for name, profiled in expected_in_profiler.items() if profiled
    }
    # Normalize the timings (since `line_profiler` PR #345 qualnames are
    # used instead of names when available)
    timings = {
        (fname, loc, name.rpartition('.')[-1]): entries
        for (fname, loc, name), entries in prof.get_stats().timings.items()
    }
    assert timings == {
        (fname, locs[name], name): []
        for name, profiled in expected_in_profiler.items() if profiled
    }
