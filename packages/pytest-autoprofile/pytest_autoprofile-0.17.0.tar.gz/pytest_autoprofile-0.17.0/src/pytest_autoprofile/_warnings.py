"""
Warning classes, annotations, and utilities.
"""
import importlib
import os
import re
import string
import warnings
from sys import version_info

from ._typing import (
    TYPE_CHECKING,
    Dict, List, Set, Tuple,
    Collection, Mapping, Sequence,
    Callable,
    Annotated, Any, Self, Type, ClassVar,
    Literal, Union, Optional,
    overload,
    Identifier, ChainedIdentifier, _DeferredAttributes,
)

if TYPE_CHECKING:  # Help out `flake8`
    from typing import overload  # type: ignore[no-redef] # noqa: F811
    from warnings import (  # noqa: F401
        WarningMessage, catch_warnings, filterwarnings,
    )


__all__ = (
    'DoctestProfilingWarning', 'OptionParsingWarning',
    'warn',
    '__getattr__',
    '__dir__',
)


# Make this module a drop-in replacement for `warnings`

__dir__, __getattr__ = _DeferredAttributes.install(globals(), warnings)


class DoctestProfilingWarning(UserWarning):
    """
    Warnings for when doctests cannot be profiled.
    """


class OptionParsingWarning(UserWarning, ValueError):
    """
    Warning class for parsed option values which are invalid but aren't
    fatal.
    """
    @classmethod
    def get_warning(
        cls, name: Annotated[str, Identifier], /, *args, **kwargs
    ) -> Self:
        """
        Parameters
        ----------
        name
            `.register()`-ed warning name
        *args, **kwargs
            Passed to the `get_fields()` callable associated with the
            warning of `name`

        Return
        ------
        Warning instance
        """
        named_fields, _, pattern, get_fields = cls._registry[name]
        fields = get_fields(*args, **kwargs)
        if named_fields:
            assert isinstance(fields, Mapping)
            msg = pattern.format(**(fields or {}))
        else:
            assert isinstance(fields, Sequence)
            msg = pattern.format(*(fields or ()))
        return cls(msg)

    @classmethod
    def get_regex(cls, name: Annotated[str, Identifier]) -> str:
        """
        Parameters
        ----------
        name
            `.register()`-ed warning name

        Return
        ------
        Regex pattern to be matched against the full warning message
        of a warning of `name`
        """
        return cls._registry[name][1]

    @staticmethod
    def _format_regex(pattern: str, /, *args: str, **kwargs: str) -> str:
        r"""
        Examples
        --------
        >>> import re
        >>>
        >>>
        >>> format_regex = OptionParsingWarning._format_regex

        Pattern with named fields:

        >>> assert (
        ...     format_regex(
        ...         '{quantity:.{prec}f} ... {unit.abbr} ... ',
        ...         quantity=r'[0-9]+\.[0-9]{2}',
        ...         # Nested fields corresponding to specs of other
        ...         # fields are dropped
        ...         prec='',
        ...         # Item access on fields is dropped
        ...         unit='[mck]?m',
        ...     )
        ...     == (
        ...         r'[0-9]+\.[0-9]{2}'
        ...         + re.escape(' ... ')
        ...         + '[mck]?m'
        ...         + re.escape(' ... ')
        ...     )
        ... )

        Pattern with anonymous (numbered) fields:

        >>> assert (
        ...     format_regex(
        ...         # Item/attribute access on fields is dropped, and
        ...         # so are conversion specs
        ...         '{[1]}_{[0]}_{.foo.bar.baz:^{}!r}_{}',
        ...         '[abc]', '[def]', "'([0-9]+|None)'",
        ...         # This field is nested and omitted
        ...         '<IGNORED>',
        ...         'foo',
        ...     )
        ...     == re.escape('_').join((
        ...         '[abc]', '[def]', "'([0-9]+|None)'", 'foo',
        ...     ))
        ... )

        Pattern with numbered fields:

        >>> assert (
        ...     format_regex(
        ...         '{{}}{3.foo}{0.bar}{2.baz}',
        ...         'a.b', 'c.d', 'e.f', 'g.h',
        ...     )
        ...     == re.escape('{}') + 'g.ha.be.f'
        ... )
        """
        def parse_subpattern(pattern: str) -> int:
            nfields = 0
            field_name: Union[str, None]
            for prefix, field_name, spec, _ in parse(pattern):
                if field_name is None:
                    continue
                if not field_name:
                    field_type = None
                elif field_name[0].isdecimal():
                    field_type = False
                elif field_name[0].isidentifier():
                    field_type = True
                else:
                    field_type = None
                add_field_type(field_type)
                nfields += 1
                if spec is not None:
                    nfields += parse_subpattern(spec)
            return nfields

        def get_leading(s: str, check: Callable[[str], bool]) -> str:
            for stop in range(len(s), 0, -1):
                substring = s[:stop]
                if check(substring):
                    return substring
            raise ValueError(
                f'No starting substring of {s!r} satisfies {check!r}',
            )

        chunks: List[str] = []
        field_types: Set[Union[bool, None]] = set()
        field_name: Union[str, None]
        parse = string.Formatter().parse
        escape = re.escape
        add_chunk = chunks.append
        add_field_type = field_types.add
        offset = 0
        for i, (prefix, field_name, spec, _) in enumerate(parse(pattern)):
            add_chunk(escape(prefix))
            if field_name is None:
                continue
            if not field_name:
                field_type = None
            elif field_name[0].isdecimal():
                field_type = False
            elif field_name[0].isidentifier():
                field_type = True
            else:
                field_type = None
            add_field_type(field_type)
            if field_type is None:
                field = args[i + offset]
            elif field_type:  # Named field
                field = kwargs[get_leading(field_name, str.isidentifier)]
            else:  # Ordered field
                field = args[int(get_leading(field_name, str.isdecimal))]
            add_chunk(field)
            if spec is not None:
                offset += parse_subpattern(spec)
        if len(field_types) > 1:
            raise ValueError(
                f'pattern = {pattern!r}: invalid field IDs; '
                'fields must be all anonymous, all numbered, or all named'
            )
        named_fields: bool = bool(field_types.pop())
        if named_fields and args:
            raise ValueError(
                f'pattern = {pattern!r}, *args = {args!r}: '
                'fields are named and can\'t take positionals'
            )
        elif not named_fields and kwargs:
            raise ValueError(
                f'pattern = {pattern!r}, **kwargs= {kwargs!r}: '
                'fields are (implicitly) numbered and can\'t take keywords'
            )
        return ''.join(chunks)

    @staticmethod
    def _format_option_flag(dest: Annotated[str, Identifier]) -> str:
        return '--' + dest.replace('_', '-').strip('-')

    @overload
    @classmethod
    def register(
        cls,
        name: Annotated[str, Identifier],
        pattern: str,
        get_fields: Callable[..., Sequence],
        /,
        *args: str
    ) -> None:
        ...

    @overload
    @classmethod
    def register(
        cls,
        name: Annotated[str, Identifier],
        pattern: str,
        get_fields: Callable[..., Mapping[Annotated[str, Identifier], Any]],
        /,
        **kwargs: str
    ) -> None:
        ...

    @classmethod
    def register(
        cls,
        name: Annotated[str, Identifier],
        pattern: str,
        get_fields: Union[
            Callable[..., Sequence],
            Callable[..., Mapping[Annotated[str, Identifier], Any]],
        ],
        /,
        *args: str,
        **kwargs: str
    ) -> None:
        """
        Parameters
        ----------
        name
            String identifier the warning is to be `.register()`-ed
            under
        pattern
            Format string
        get_fields()
            Callable returning the sequence or mapping of fields to be
            passed to `pattern.format()`
        *args, **kwargs
            Regex sub-patterns corresponding to the fields of `pattern`

        Effect
        ------
        Warning `name` registered;
        such warnings can then be created with
        `OptionParsingWarning.get_warning(name, ...)`, and their message
        will match `OptionParsingWarning.get_regex(name)`
        """
        named_fields = bool(kwargs)
        regex = cls._format_regex(pattern, *args, **kwargs)
        flag = cls._format_option_flag(name)
        cls._registry[name] = (  # type: ignore[assignment]
            named_fields,
            '^{}: {}$'.format(re.escape(flag), regex),
            f'{flag}: {pattern}',
            get_fields,
        )

    _registry: ClassVar[
        Dict[
            Annotated[str, Identifier],
            Union[
                Tuple[Literal[True], str, str, Callable[..., Sequence]],
                Tuple[
                    Literal[False], str, str,
                    Callable[..., Mapping[Annotated[str, Identifier], Any]],
                ],
            ]
        ]
    ] = {}


def _get_warn_kwargs(
    modules: Collection[Annotated[str, ChainedIdentifier]],
    skip_this_module: bool = True,
    /,
    **kwargs
) -> Dict[str, Any]:
    def canonize_path(module_fname: str) -> str:
        if get_base_name(module_fname) == '__init__.py':
            dname = get_dir_name(module_fname)
            if not dname.endswith(path_sep):
                dname += path_sep
            return dname
        return module_fname[:fname_stop]

    find_spec = importlib.util.find_spec
    get_dir_name = os.path.dirname
    get_base_name = os.path.basename
    path_sep = os.path.sep

    skip_file_prefixes = list(kwargs.pop('skip_file_prefixes', ()))
    if version_info[:2] < (3, 12):
        return kwargs

    fname_stop: Union[int, None] = None
    if version_info[:5] < (3, 14, 0, 'alpha', 2):
        try:
            c_warnings = importlib.import_module('_warnings')
        except ImportError:  # The pure-Python implementation is OK...
            pass
        else:  # ... but the C implementation was bugged pre-3.14.0a2
            if c_warnings.warn is warnings.warn:
                fname_stop = -1

    skip_file_prefixes.extend(
        spec.origin
        for spec in (find_spec(module) for module in set(modules))
        if spec and spec.origin
    )
    if skip_this_module:
        skip_file_prefixes.append(__file__)
    kwargs['skip_file_prefixes'] = tuple({
        canonize_path(path) for path in skip_file_prefixes
    })
    return kwargs


def warn(
    message: Union[str, Warning],
    category: Optional[Type[Warning]] = None,
    stacklevel: int = 1,
    source: Optional[str] = None,
    *,
    skip_file_prefixes: Collection[str] = (),
    skip_modules: Collection[Annotated[str, ChainedIdentifier]] = (),
) -> None:
    """
    Convenience wrapper around `warnings.warn()`.

    Parameters
    ----------
    skip_modules
        Alternative for `skip_file_prefixes`, allowing skipping packages
        by name
    *args, **kwargs
        Passed to `warnings.warn()`

    Notes
    -----
    - Python module file names in `skip_file_prefixes` are truncated to
      circumvent the off-by-one error in `_warnings.warn()` (CPython
      issue #126209; fixed in 3.14.0a2).
    - `stacklevel` is padded by one to counteract the additional frame
      incurred by this function.
    """
    kwargs = _get_warn_kwargs(
        skip_modules, skip_file_prefixes=skip_file_prefixes,
    )
    warnings.warn(message, category, stacklevel + 1, source, **kwargs)
