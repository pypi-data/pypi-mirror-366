import ast

import pytest

from ._typing import (
    TYPE_CHECKING,
    Dict, List, Tuple,
    Callable, MutableMapping, Sequence,
    Annotated, Any, TypeVar, ClassVar,
    Literal, Union, Optional,
    overload,
    Identifier, ImportPath, Parsable,
)

if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811


__all__ = ('NodeContextLabeller', 'LazyImporter', 'get_config')

THIS_PACKAGE = (lambda: None).__module__.partition('.')[0]

FuncDefNode = TypeVar('FuncDefNode', ast.FunctionDef, ast.AsyncFunctionDef)
DefNode = TypeVar(
    'DefNode', ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef,
)
AST = TypeVar('AST', bound=ast.AST)


class NodeContextLabeller(ast.NodeTransformer):
    """
    Label all the function and class definitions accessible from the
    module namespace with their qualified names.

    Notes
    -----
    The tree is transformed in-place.

    Example
    -------
    >>> import ast
    >>> import textwrap
    >>> from typing import Tuple, Union, Type, ClassVar
    >>>
    >>>
    >>> class Verifier(ast.NodeVisitor):
    ...     '''
    ...     Check that the nodes accessible from the module-level are
    ...     properly labelled.
    ...     '''
    ...     def __init__(self, **targets: Union[str, None]):
    ...         self.targets = targets
    ...
    ...     def _check_name(
    ...         self,
    ...         node: Union[
    ...             ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef,
    ...         ],
    ...     ) -> None:
    ...         if node.name not in self.targets:
    ...             return
    ...         qualname = getattr(node, 'quallified_name', None)
    ...         assert qualname == self.targets[node.name]
    ...
    ...     def generic_visit(self, node: ast.AST) -> None:
    ...         if isinstance(node, self.checked_nodes):
    ...             self._check_name(node)
    ...         super().generic_visit(node)
    ...
    ...     checked_nodes: ClassVar[
    ...         Tuple[Type[ast.AST], ...]
    ...     ] = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    ...
    >>>
    >>> module = ast.parse(textwrap.dedent('''
    ... def foo():
    ...     def bar(): pass
    ...
    ...     class FooBar():
    ...         def baz(): pass
    ...
    ...
    ... class Spam:
    ...     def ham(self):
    ...         def eggs(): pass
    ...
    ...     async def jam(self):
    ...         def butter(): pass
    ...
    ...     class Ham:
    ...         def ham_and_eggs(): pass
    ... '''))
    >>> named_module = NodeContextLabeller().visit(module)
    >>> assert named_module is module
    >>> verifier = Verifier(
    ...     foo='foo',
    ...     bar=None,
    ...     FooBar=None,
    ...     baz=None,
    ...     Spam='Spam',
    ...     ham='Spam.ham',
    ...     eggs=None,
    ...     jam='Spam.jam',
    ...     butter=None,
    ...     Ham='Spam.Ham',
    ...     ham_and_eggs='Spam.Ham.ham_and_eggs',
    ... )
    >>> verifier.visit(named_module)
    """
    # Attributes
    context: Union[ast.Module, ast.ClassDef, None]

    def __init__(
        self,
        context: Optional[Union[ast.Module, ast.ClassDef]] = None,
    ) -> None:
        self.context = context

    def generic_visit(self, node: AST) -> AST:  # Help `mypy`
        return super().generic_visit(node)  # type: ignore[return-value]

    def visit_Module(self, node: ast.Module) -> ast.Module:
        setattr(node, self.qualname_attr, '')
        try:
            self.context = node
            return self.generic_visit(node)
        finally:
            self.context = None

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        return self._set_name(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._set_name(node, descend=False)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef,
    ) -> ast.AsyncFunctionDef:
        return self._set_name(node, descend=False)

    @overload
    def _set_name(
        self, node: ast.ClassDef, descend: bool = True,
    ) -> ast.ClassDef:
        ...

    @overload
    def _set_name(
        self, node: FuncDefNode, descend: Literal[False],
    ) -> FuncDefNode:
        ...

    def _set_name(self, node: DefNode, descend: bool = True) -> DefNode:
        if self.context is None:
            # Local definition in functions, no need to descend into it
            return node
        old_ctx = self.context
        old_ctx_name = getattr(old_ctx, self.qualname_attr)
        if old_ctx_name:
            ctx_name = f'{old_ctx_name}.{node.name}'
        else:
            ctx_name = node.name
        setattr(node, self.qualname_attr, ctx_name)
        if not descend:
            return node
        if TYPE_CHECKING:  # Help out `mypy`
            assert isinstance(node, ast.ClassDef)
        try:
            self.context = node
            return self.generic_visit(node)
        finally:
            self.context = old_ctx

    qualname_attr: ClassVar[Annotated[str, Identifier]] = 'quallified_name'


class LazyImporter:
    """
    Helper class for allowing lazy imports.
    """
    targets: Dict[Annotated[str, Identifier], ImportPath]
    namespace: MutableMapping[Annotated[str, Identifier], Any]

    def __init__(
        self,
        namespace: Optional[
            MutableMapping[Annotated[str, Identifier], Any]
        ] = None,
        /,
        **targets: Annotated[str, Parsable[ImportPath]],
    ) -> None:
        self.targets = {}
        for alias, path in targets.items():
            ipath = ImportPath.parse(path)
            if alias is None:
                if ipath.object:
                    alias = ipath.object.rpartition('.')[-1]
                else:
                    alias = ipath.module.rpartition('.')[-1]
            self.targets[alias] = ipath
        self.namespace = namespace

    def dir(self) -> List[Annotated[str, Identifier]]:
        names = set(self.namespace or {})
        return sorted(names.union(self.targets))

    def getattr(self, attr: Annotated[str, Identifier]) -> Any:
        try:
            ipath = self.targets[attr]
        except KeyError:
            raise AttributeError(attr) from None
        try:
            result = ipath.import_target()
        except ImportError as e:
            raise AttributeError(attr) from e
        if self.namespace is not None:
            self.namespace[attr] = result
        return result

    @classmethod
    def install(
        cls, namespace: MutableMapping[Annotated[str, Identifier], Any],
        /,
        **siblings: Annotated[str, Parsable[ImportPath]],
    ) -> Tuple[
        Callable[[], List[Annotated[str, Identifier]]],
        Callable[[Annotated[str, Identifier]], Any],
    ]:
        """
        Create an instance and return its `.dir()` and `.getattr()`
        methods in a 2-tuple. The `siblings` paths are relative to the
        package top level.

        Example
        -------
        >>> from types import ModuleType
        >>>
        >>>
        >>> install = LazyImporter.install
        >>> my_module = ModuleType('my_module')
        >>> my_module.__dir__, my_module.__getattr__ = install(
        ...     vars(my_module), L='utils::LazyImporter',
        ... )
        >>> assert 'L' not in vars(my_module)
        >>> assert 'L' in dir(my_module)
        >>> assert my_module.L is LazyImporter
        >>> assert vars(my_module)['L'] is LazyImporter
        """
        targets = {
            alias: f'{THIS_PACKAGE}.{path}' for alias, path in siblings.items()
        }
        instance = cls(namespace, **targets)
        result = instance.dir, instance.getattr
        namespace['__dir__'], namespace['__getattr__'] = result
        return result


def get_config(args: Sequence[str]) -> pytest.Config:
    """
    Convenience function for getting a `pytest.Config` object from
    command-line arguments to `pytest.main()`.
    """
    return pytest.Config.fromdictargs({}, list(args))
