"""
Helper module for capturing warnings from without a `pytester` test
session;
meant for internal use only.
"""
import os
from ast import literal_eval
from warnings import WarningMessage
from pytest_autoprofile._typing import (
    List, TypedDict,
    TextIO,
    Annotated, Union,
    ImportPath, Parsable,
)


__all__ = ('pytest_warning_recorded', 'retrieve_warnings')


class WarningMessageSerialization(TypedDict):
    message: str
    category: Annotated[str, Parsable[ImportPath]]
    filename: str
    lineno: int
    line: Union[str, None]


def serialize(w: WarningMessage) -> WarningMessageSerialization:
    return {
        'message': str(w.message),
        'category': '{0.__module__}::{0.__qualname__}'.format(w.category),
        'filename': w.filename,
        'lineno': w.lineno,
        'line': w.line,
    }


def deserialize(fobj: TextIO) -> List[WarningMessage]:
    result: List[WarningMessage] = []
    for line in fobj:
        asdict = literal_eval(line.strip())
        assert isinstance(asdict, dict)
        category = ImportPath.parse(asdict['category']).import_target()
        result.append(WarningMessage(**{**asdict, 'category': category}))
    return result


def pytest_warning_recorded(
    warning_message: WarningMessage,
) -> None:
    with open(FILENAME, mode='a') as fobj:
        print(serialize(warning_message), file=fobj)


def retrieve_warnings() -> List[WarningMessage]:
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, mode='r') as fobj:
        return deserialize(fobj)


FILENAME = __file__ + '.txt'
