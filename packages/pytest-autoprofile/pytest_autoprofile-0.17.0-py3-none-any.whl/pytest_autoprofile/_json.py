"""
Augmented JSON handling.
"""
import json
from functools import partial
from io import StringIO
from pathlib import PurePath

from ._typing import (
    TYPE_CHECKING,
    Dict, Set,
    Collection, Iterator, Mapping, Sequence,
    TextIO,
    Any, Union, Optional,
    ImportPath,
)


class JSONHelper(json.JSONEncoder):
    """
    Helper object for handling JSON (de-)serialization.

    Example
    -------
    >>> import json
    >>> from pytest_autoprofile._typing import ImportPath
    >>>
    >>>
    >>> def roundtrip(obj, helper=False):
    ...     namespace = JSONHelper if helper else json
    ...     return namespace.loads(namespace.dumps(obj))
    ...
    >>>
    >>> def strict_eq(x, y):
    ...     return (type(x) is type(y)) and x == y

    Handling sets:

    >>> roundtrip({1, 2})
    Traceback (most recent call last):
      ...
    TypeError: ...
    >>> roundtripped = roundtrip({1, 2}, helper=True)
    >>> assert strict_eq(roundtripped, {1, 2})

    Handling tuples:

    >>> roundtrip((1, (2, 3)))
    [1, [2, 3]]
    >>> roundtrip((1, (2, 3)), helper=True)
    (1, (2, 3))

    Handling strings:

    >>> roundtrip('foo')
    'foo'
    >>> assert strict_eq(roundtrip('foo', helper=True), 'foo')

    Handling mappings:

    >>> roundtrip({1: 2})
    {'1': 2}
    >>> assert strict_eq(roundtrip({1: 2}, helper=True), {1: 2})

    Handling `~.typing.ImportPath`:

    >>> path = ImportPath('foo', 'bar')
    >>> roundtrip(path)
    ['foo', 'bar']
    >>> assert strict_eq(roundtrip(path, helper=True), path)

    Handling recursion:

    >>> recursive = [[]]
    >>> recursive.append(recursive)
    >>> roundtrip(recursive)
    Traceback (most recent call last):
      ...
    ValueError: Circular reference detected
    >>> roundtrip(recursive, helper=True)
    Traceback (most recent call last):
      ...
    ValueError: Circular reference detected
    """
    @classmethod
    def dump(
        cls, obj: Any, file: Union[TextIO, str, PurePath], **kwargs
    ) -> None:
        if not callable(getattr(type(file), 'write', None)):
            if TYPE_CHECKING:
                assert isinstance(file, (str, PurePath))
            with open(file, mode='w') as fobj:
                return cls.dump(obj, fobj, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(file, TextIO)
        kwargs.setdefault('cls', cls)
        json.dump(obj, file, **kwargs)

    @classmethod
    def load(cls, file: Union[TextIO, str, PurePath], **kwargs) -> Any:
        if not callable(getattr(type(file), 'read', None)):
            if TYPE_CHECKING:
                assert isinstance(file, (str, PurePath))
            with open(file, mode='r') as fobj:
                return cls.load(fobj, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(file, TextIO)
        kwargs.setdefault('object_hook', cls.object_hook)
        return json.load(file, **kwargs)

    @classmethod
    def dumps(cls, obj: Any, **kwargs) -> str:
        with StringIO(newline=None) as sio:
            cls.dump(obj, sio, **kwargs)
            return sio.getvalue()

    @classmethod
    def loads(cls, string: str, **kwargs) -> Any:
        with StringIO(string) as sio:
            return cls.load(sio, **kwargs)

    @staticmethod
    def object_hook(deserialization: Dict[str, Any]) -> Any:
        if set(deserialization) != {
            '_importer_json_helper', '__class__', 'args', 'kwargs',
        }:
            return deserialization
        if not deserialization['_importer_json_helper']:
            return deserialization
        cls = (
            ImportPath.parse(deserialization['__class__']).import_target()
        )
        return cls(*deserialization['args'], **deserialization['kwargs'])

    def iterencode(  # type: ignore[override]
        self, obj: Any, *args, **kwargs
    ) -> Iterator[str]:
        return super().iterencode(self.default(obj), *args, **kwargs)

    def default(self, obj, seen: Optional[Set[int]] = None):
        if seen is None:
            seen = set()
        default = partial(self.default, seen=seen)
        format_cls = '{0.__module__}::{0.__qualname__}'.format
        proxy: Sequence
        if isinstance(obj, ImportPath):
            return {
                '_importer_json_helper': True,
                '__class__': format_cls(type(obj)),
                'args': (),
                'kwargs': {'module': obj.module, 'object': obj.object},
            }
        if isinstance(obj, Mapping):
            if id(obj) in seen:
                raise ValueError('Circular reference detected')
            seen.add(id(obj))
            proxy = [
                (default(key), default(value)) for key, value in obj.items()
            ]
            return {
                '_importer_json_helper': True,
                '__class__': format_cls(type(obj)),
                'args': (proxy,),
                'kwargs': {},
            }
        if isinstance(obj, Collection):
            # Escape simple strings
            if type(obj) in (str, bytes):
                return obj
            if id(obj) in seen:
                raise ValueError('Circular reference detected')
            seen.add(id(obj))
            if isinstance(obj, str):
                proxy = str(obj)
            elif isinstance(obj, bytes):
                proxy = bytes(obj)
            else:
                proxy = [default(item) for item in obj]
            return {
                '_importer_json_helper': True,
                '__class__': format_cls(type(obj)),
                'args': (proxy,),
                'kwargs': {},
            }
        ImporterBase = _IMPORTER_BASE_PATH.import_target()
        if isinstance(obj, ImporterBase):
            if id(obj) in seen:
                raise ValueError('Circular reference detected')
            seen.add(id(obj))
            return {
                '_importer_json_helper': True,
                '__class__': format_cls(type(obj)),
                'args': (),
                'kwargs': obj._get_serializable_attrs(),
            }
        return obj


_IMPORTER_BASE_PATH = ImportPath(
    (lambda: None).__module__.rpartition('.')[0] + '.importers',
    '_AutoProfImporterBase',
)
