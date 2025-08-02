"""
Targeted AST rewriting inspired by `line_profiler.autoprofile`, but
not quite doing the same thing.
"""
import ast
import functools
import importlib.machinery
import operator
import os
import pathlib

from ._typing import (
    TYPE_CHECKING,
    FrozenSet, Set, Tuple,
    Callable, Collection,
    Literal, Union, Optional,
    Annotated, TypeVar, ClassVar, Self,
    Parsable, ChainedIdentifier, Identifier, ImportPath,
)
from .utils import NodeContextLabeller


__all__ = ('StrictModuleRewriter',)

AST = TypeVar('AST', bound=ast.AST)


class StrictModuleRewriter(ast.NodeTransformer):
    """
    Handle both whole-module rewriting (like `line_profiler
    .autoprofile.ast_profile_transformer.AstProfileTransformer`) and
    more fine-grained partial rewriting.

    Notes
    -----
    - The tree is modified in-place.
    - Unlike `AstProfileTransformer`, this does not rewrite imports.

    Examples
    --------
    >>> import ast
    >>> import textwrap
    >>> from typing import Tuple, Type, ClassVar, Union
    >>>
    >>> from pytest_autoprofile._typing import ImportPath
    >>>
    >>>
    >>> def get_module() -> ast.Module:
    ...     return ast.parse(textwrap.dedent('''
    ... def foo():
    ...     def bar(): pass
    ...
    ...     class FooBar():
    ...         def baz(): pass
    ...
    ...
    ... class Spam:
    ...     @staticmethod
    ...     def ham():
    ...         def eggs(): pass
    ...
    ...     async def jam(self):
    ...         def butter(): pass
    ...
    ...     class Ham:
    ...         def ham_and_eggs(): pass
    ...
    ...     class Jam:  # This class has no methods to be rewritten
    ...         pass
    ...     '''))
    ...
    >>>
    >>> class Counter(ast.NodeVisitor):
    ...     '''
    ...     Check the number of function definitions decorated with
    ...     the profiler.
    ...     '''
    ...     def __init__(self):
    ...         self.count = 0
    ...
    ...     def _check_def(
    ...         self,
    ...         node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ...     ) -> None:
    ...         try:
    ...             *_, decorator = node.decorator_list
    ...         except ValueError:
    ...             return
    ...         if not isinstance(decorator, ast.Name):
    ...             return
    ...         if decorator.id == 'profile':
    ...             self.count += 1
    ...
    ...     def generic_visit(self, node: ast.AST) -> None:
    ...         if isinstance(node, self.checked_nodes):
    ...             self._check_def(node)
    ...         super().generic_visit(node)
    ...
    ...     @classmethod
    ...     def count_profiled_defs(cls, node: ast.AST) -> int:
    ...         counter = cls()
    ...         counter.visit(node)
    ...         return counter.count
    ...
    ...     checked_nodes: ClassVar[
    ...         Tuple[Type[ast.AST], ...]
    ...     ] = (ast.FunctionDef, ast.AsyncFunctionDef)
    ...
    >>>
    >>> count = Counter.count_profiled_defs

    Basic whole-module rewrite:

    >>> transformer = StrictModuleRewriter(
    ...     'my_module', rewrite_targets='my_module,another_module',
    ... )
    >>> assert transformer.rewrite_whole_module
    >>> assert not transformer.specific_rewrite_targets
    >>> module = transformer(get_module())
    >>> prof_count = count(module)
    >>> assert prof_count == 4, prof_count
    >>> assert transformer.rewritten == set(ImportPath.parse_multiple(
    ...     'my_module,'  # The module itself
    ...     'my_module::foo,'  # A top-level function
    ...     'my_module::Spam,'  # A top-level class
    ...     # ... and its nested methods and classes accessible via
    ...     # chained attribute access
    ...     'my_module::Spam.ham,my_module::Spam.jam,'
    ...     'my_module::Spam.Ham,my_module::Spam.Ham.ham_and_eggs'
    ...     # Note that 'my_module::Spam.Jam' doesn't appear here,
    ...     # becuase it doesn't have any method to be rewritten
    ... )), sorted(str(ipath) for ipath in transformer.rewritten)

    Partial rewrite:

    >>> transformer = StrictModuleRewriter(
    ...     'my_module',
    ...     rewrite_targets='my_module::Spam.Ham,another_module::foo',
    ... )
    >>> assert not transformer.rewrite_whole_module
    >>> assert len(transformer.specific_rewrite_targets) == 1
    >>> module = transformer(get_module())
    >>> prof_count = count(module)
    >>> assert prof_count == 1, prof_count
    >>> assert transformer.rewritten == set(ImportPath.parse_multiple(
    ...     'my_module::Spam.Ham,'  # The target class
    ...     'my_module::Spam.Ham.ham_and_eggs'  # And its method
    ... )), sorted(str(ipath) for ipath in transformer.rewritten)

    Convenience method: `transform_module()`:

    >>> from importlib.util import find_spec
    >>>
    >>>
    >>> spec = find_spec('argparse')
    >>> module_total, rewritten = StrictModuleRewriter.transform_module(
    ...     spec,
    ... )
    >>> assert count(module_total) > 10
    >>> assert rewritten & set(ImportPath.parse_multiple(
    ...     'argparse::Namespace,'
    ...     'argparse::ArgumentParser.add_subparsers'
    ... )), sorted(str(ipath) for ipath in rewritten)
    >>> module_partial, rewritten = (
    ...     StrictModuleRewriter.transform_module(
    ...         spec, 'argparse::ArgumentParser',
    ...     )
    ... )
    >>> assert count(module_total) > count(module_partial)
    >>> assert rewritten > set(ImportPath.parse_multiple(
    ...     'argparse::ArgumentParser.parse_known_args,'
    ...     'argparse::ArgumentParser.parse_args,'
    ...     'argparse::ArgumentParser.add_subparsers'
    ... )), sorted(str(ipath) for ipath in rewritten)
    >>> assert 'argparse::Namespace' not in rewritten, sorted(
    ...     str(ipath) for ipath in rewritten
    ... )
    """
    # Attributes
    canonical_path: Annotated[str, ChainedIdentifier]
    full_path: Annotated[str, ChainedIdentifier]
    rewrite_targets: FrozenSet[ImportPath]
    _rewritten: Set[Annotated[str, ChainedIdentifier]]

    def __init__(
        self,
        canonical_path: Annotated[str, ChainedIdentifier],
        *,
        full_path: Optional[Annotated[str, ChainedIdentifier]] = None,
        rewrite_targets: Optional[
            Union[
                Collection[ImportPath],
                Annotated[str, Parsable[Collection[ImportPath]]],
            ]
        ] = None,
    ) -> None:
        self.canonical_path = canonical_path
        self.full_path = full_path or canonical_path
        if isinstance(rewrite_targets, str):
            rewrite_targets = ImportPath.parse_multiple(rewrite_targets)
        self.rewrite_targets = frozenset(rewrite_targets or ())
        self._rewritten = set()

    def __call__(self, node: AST) -> AST:
        """
        Calculate the paths to the definitions with
        `~.utils.NodeContextLabeller`, `.visit()` the `node`, and return
        it with all the added nodes repaired with
        `ast.fix_missing_locations()`.
        """
        return ast.fix_missing_locations(
            self.visit(NodeContextLabeller().visit(node)),
        )

    def match_node(self, qualname: Annotated[str, ChainedIdentifier]) -> bool:
        """
        Return
        ------
        Whether the node with `qualname` should be decorated
        """
        if self.rewrite_whole_module:
            return True
        if qualname in self.specific_rewrite_targets:
            return True
        return self._is_subtarget(qualname)

    def generic_visit(self, node: ast.AST) -> ast.AST:
        """
        Insert the decorator into the decorator stacks of function and
        method definitions matching `self.rewrite_targets`.

        Return
        ------
        `node`, but possibly modified
        """
        super_impl = super().generic_visit
        qualname: Union[
            Annotated[Identifier, str], Literal[''], None,
        ] = getattr(node, self.qualname_attr, None)
        if not (qualname and self.match_node(qualname)):
            return super_impl(node)
        if isinstance(node, ast.ClassDef):  # Descend into class defs
            rewritten = self._rewritten
            method_count = len(rewritten)
            result = super_impl(node)
            # Only label a class as being profiled if we actually
            # profiled any of its methods
            if len(rewritten) > method_count:
                rewritten.add(qualname)
            return result
        # If we're here, we have an (async) function definition to be
        # profiled
        if TYPE_CHECKING:
            assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        self._rewritten.add(qualname)
        node.decorator_list.append(
            ast.Name(id=self.profiler_name, ctx=ast.Load()),
        )
        return super_impl(node)

    @staticmethod
    def get_tree_from_filename(
        fname: Union[str, pathlib.PurePath],
    ) -> ast.Module:
        """
        Return
        ------
        `ast.Module` object compile from `fname`
        """
        with open(fname) as fobj:
            return ast.parse(fobj.read())

    @classmethod
    def from_module_spec(
        cls,
        spec: importlib.machinery.ModuleSpec,
        rewrite_targets: Optional[
            Union[
                Collection[ImportPath],
                Annotated[str, Parsable[Collection[ImportPath]]],
            ]
        ] = None,
    ) -> Self:
        """
        Return
        ------
        Instance
        """
        if TYPE_CHECKING:
            assert spec.origin is not None
        canonical_path = spec.name
        base_name = os.path.basename(spec.origin)
        if base_name in ('__init__.py', '__main__.py'):
            full_path = f'{canonical_path}.{base_name.partition(".")[0]}'
        else:
            full_path = canonical_path
        return cls(
            canonical_path,
            rewrite_targets=rewrite_targets,
            full_path=full_path,
        )

    @classmethod
    def transform_module(
        cls,
        spec: importlib.machinery.ModuleSpec,
        rewrite_targets: Optional[
            Union[
                Collection[ImportPath],
                Annotated[str, Parsable[Collection[ImportPath]]],
            ]
        ] = None,
    ) -> Tuple[ast.Module, FrozenSet[ImportPath]]:
        """
        Return
        ------
        Two-tuple of:
        - Transformed `ast.Module` object representing the module
        - Frozen set of import paths representing the modules/classes/
          methods/functions profiled

        Notes
        -----
        If `rewrite_targets` is `None`, it defaults to the entire
        module.
        """
        if TYPE_CHECKING:
            assert spec.origin is not None
        if rewrite_targets is None:
            rewrite_targets = spec.name
        inst = cls.from_module_spec(spec, rewrite_targets)
        return inst(cls.get_tree_from_filename(spec.origin)), inst.rewritten

    @functools.cached_property
    def rewrite_whole_module(self) -> bool:
        module_aliases = {self.canonical_path, self.full_path}
        whole_module_rewrite_targets: Set[Annotated[str, ChainedIdentifier]] = {
            module for module, object in self.rewrite_targets if not object
        }
        return bool(module_aliases & whole_module_rewrite_targets)

    @functools.cached_property
    def specific_rewrite_targets(
        self,
    ) -> FrozenSet[Annotated[str, ChainedIdentifier]]:
        module_aliases = {self.canonical_path, self.full_path}
        return frozenset(
            object for module, object in self.rewrite_targets
            if object and module in module_aliases
        )

    @functools.cached_property
    def _is_subtarget(self) -> Callable[[str], bool]:
        prefixes: Tuple[str, ...] = tuple(
            target + '.' for target in self.specific_rewrite_targets
        )
        return operator.methodcaller('startswith', prefixes)

    @property
    def rewritten(self) -> FrozenSet[ImportPath]:
        result: FrozenSet[ImportPath] = frozenset()
        if self.full_path.endswith('.__init__'):
            module_name = self.canonical_path
        else:
            module_name = self.full_path
        get_path = functools.partial(ImportPath, module_name)
        rewrote: FrozenSet[
            Union[Annotated[str, ChainedIdentifier], None]
        ] = frozenset(self._rewritten)
        # Only label a module as being rewritten if there was actually
        # anything in it to be rewritten
        if rewrote and self.rewrite_whole_module:
            rewrote |= {None}
        return result | {get_path(obj) for obj in rewrote}

    profiler_name: ClassVar[Annotated[str, Identifier]] = 'profile'
    qualname_attr: ClassVar[Annotated[str, Identifier]] = (
        NodeContextLabeller.qualname_attr
    )
