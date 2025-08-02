"""
Test that default values for the command-line flags are properly read
from the `conftest.py` hooks.
"""
import contextlib
import importlib.util
import itertools
import os
import pathlib
import re
import shlex
import sys
import uuid

import pytest

from pytest_autoprofile import _test_utils as utils
from pytest_autoprofile._typing import (
    List, Tuple,
    Callable, ContextManager, Generator, Iterable, Sequence,
    Annotated, Any, Protocol,
    Literal, Union,
    Parsable, Identifier, ImportPath,
)
from pytest_autoprofile.option_hooks import (
    resolve_hooked_option, OptionParsingWarning,
)
from pytest_autoprofile.importers import AutoProfImporter


PLUGIN_AUTOPROF_MOD = 'foo.bar::baz,spam.eggs'
PLUGIN_AUTOPROF_TESTS = 'yes'

PLUGIN_PATTERN = """
def pytest_autoprof_mod_default() -> str:
    return {autoprof_mod!r}


def pytest_autoprof_tests_default() -> {autoprof_tests_type}:
    return {autoprof_tests!r}
"""


class ConfigGetter(Protocol):
    def __call__(self, *args: str) -> pytest.Config:
        ...


@pytest.fixture
def get_config(pytester: pytest.Pytester) -> ConfigGetter:
    return pytester.parseconfig


@pytest.fixture
def conftest(pytester: pytest.Pytester) -> pathlib.Path:
    return pytester.makeconftest(get_plugin_content())


@pytest.fixture
def plugin(
    pytester: pytest.Pytester,
) -> Tuple[Annotated[str, Identifier], pathlib.Path]:
    plugin_name = gen_plugin_name()
    plugin_basename = plugin_name.replace('_', '-')
    plugin_path = pytester.mkdir(plugin_basename)
    (plugin_path / 'pyproject.toml').write_text(
        utils.strip("""
    [build-system]
    requires = ['setuptools']
    build-backend = 'setuptools.build_meta'

    [project]
    name = {0!r}
    version = '0.0'

    [project.entry-points.pytest11]
    {1} = {1!r}
        """)
        .format(plugin_basename, plugin_name),
    )
    (plugin_path / (plugin_name + '.py')).write_text(get_plugin_content())
    return plugin_name, plugin_path


@pytest.fixture
def install_plugin(
    pytester: pytest.Pytester,
    plugin: Tuple[Annotated[str, Identifier], pathlib.Path],
) -> Generator[Annotated[str, Identifier], None, None]:
    def pip(*args) -> None:
        # Note: it isn't any faster to try to run `pip` in-process with
        # `runpy`...
        argv = ['pip', *args]
        if pytester.run(sys.executable, '-m', *argv).ret:
            raise RuntimeError('Failed to run ' + repr(shlex.join(argv)))

    name, path = plugin
    assert os.path.isdir(path)
    # Note: don't install as `--editable` because that requires a
    # new metapath entry
    pip('install', '--quiet', '--quiet', '--quiet', str(path))
    yield name
    pip('uninstall', '--quiet', '--quiet', '--quiet', '--yes', name)


def gen_plugin_name(
    base_name: str = 'temp-plugin',
    nchunks: Union[int, None] = 3,
    nretries: Union[int, None] = 10,
) -> Annotated[str, Identifier]:
    find_spec = importlib.util.find_spec
    get_uuid = uuid.uuid4
    if nretries is None:
        iterable: Iterable[int] = itertools.cycle((0,))
    else:
        iterable = range(nretries)
    name_prefix_chunks: List[str] = (
        base_name.replace('-', ' ').replace('_', ' ').split()
    )
    for _ in iterable:
        chunks = name_prefix_chunks + str(get_uuid()).split('-')[:nchunks]
        name = '_'.join(chunks)
        # Prevent accidentally overwriting an existing package
        if find_spec(name) is None:
            return name
    raise RuntimeError(
        f'base_name = {base_name!r}, nchunks = {nchunks!r}: '
        f'failed to find a package name not taken within {nretries} retry/-ies'
    )


def get_plugin_content(
    autoprof_mod: Annotated[
        str, Parsable[List[ImportPath]]
    ] = PLUGIN_AUTOPROF_MOD,
    autoprof_tests: Union[
        bool, Annotated[str, Parsable[bool]],
    ] = PLUGIN_AUTOPROF_TESTS,
) -> str:
    return utils.strip(PLUGIN_PATTERN.format(
        autoprof_mod=autoprof_mod,
        autoprof_tests=autoprof_tests,
        autoprof_tests_type=(
            'bool' if autoprof_tests in (True, False) else 'str'
        ),
    ))


def _test_with_plugin(get_config: ConfigGetter) -> None:
    """
    Notes
    -----
    The options tested are so chosen:
    - `--autoprof-mod` for a non-boolean option
    - `--autoprof-tests` for a boolean option
    - `--autoprof-outfile` for an option whose hook spec taks an
      argument.
    """
    def get_outfile(
        root: pathlib.Path,
        cache_dir: Union[pathlib.PurePath, str] = '.pytest_cache',
        basename: Union[
            pathlib.PurePath, str,
        ] = 'pytest_autoprofile.lprof',
    ) -> pathlib.Path:
        return root / cache_dir / basename

    for args, mod, test, out in [
        ((), PLUGIN_AUTOPROF_MOD, True, {}),
        (
            (
                '--autoprof-mod=foobar.baz',
                '--autoprof-tests',
                f'--autoprof-outfile={pathlib.Path(os.curdir) / "baz.lproj"}',
            ),
            'foobar.baz',
            True,
            {'cache_dir': os.curdir, 'basename': 'baz.lproj'},
        ),
        (
            (
                '--autoprof-mod=spam,eggs',
                '--autoprof-tests=no',
                '-o',
                'cache_dir=.myothercache',
            ),
            'spam,eggs',
            False,
            {'cache_dir': '.myothercache'},
        ),
    ]:
        config = get_config(*args)
        assert (
            resolve_hooked_option(config, 'autoprof_mod')
            == ImportPath.parse_multiple(mod)
        )
        assert resolve_hooked_option(config, 'autoprof_tests') == test
        expected_outfile = get_outfile(config.rootpath, **out)
        resolved_outfile = resolve_hooked_option(
            config, 'autoprof_outfile', kwargs={'config': config},
        )
        assert (
            os.path.abspath(resolved_outfile)
            == os.path.abspath(expected_outfile)
        )


def test_options_conftest(
    get_config: ConfigGetter, conftest: pathlib.Path,
) -> None:
    """
    Test what happens when alternative defaults for `--autoprof-mod`,
    `--autoprof-tests`, and `--autoprof-outfile` are supplied via
    `pytest_*_default()` in a `conftest.py`.
    """
    _test_with_plugin(get_config)


@pytest.mark.skipif(
    sys.prefix == sys.base_prefix,
    reason="""
    test temporarily `pip install`s a plugin, potentially polluting the
    system Python
    """,
)
def test_options_plugin(
    get_config: ConfigGetter, install_plugin: Annotated[str, Identifier],
) -> None:
    """
    Test what happens when alternative defaults for `--autoprof-mod`,
    `--autoprof-tests`, and `--autoprof-outfile` are supplied via
    `pytest_*_default()` in another plugin.
    """
    _test_with_plugin(get_config)


def test_no_arg_outfile_default(pytester: pytest.Pytester) -> None:
    """
    Test that hooks which takes arguments in their spec (e.g.
    `--autoprof-outfile`) can have implementations which takes fewer,
    and that they are correctly handled by
    `~.option_hooks.resolve_hooked_option()` regardless of whether
    positional or keyword (preferred) args are passed.
    """
    pytester.makeconftest("""
    def pytest_autoprof_outfile_default() -> str:
        return 'foobar.lprof'
    """)
    config = pytester.parseconfig()
    outfile_kwargs = resolve_hooked_option(
        config, 'autoprof_outfile', kwargs={'config': config},
    )
    config = pytester.parseconfig()
    outfile_args = resolve_hooked_option(
        config, 'autoprof_outfile', args=(config,),
    )
    assert outfile_kwargs == outfile_args == 'foobar.lprof'


def test_stray_option(get_config: ConfigGetter) -> None:
    """
    Test feeding a nonexistent option to `resolve_hooked_option()`.
    """
    config = get_config()
    non_existent_flag = '--autoprof-some-nonexistent-flag'
    with pytest.raises(ValueError):
        resolve_hooked_option(config, non_existent_flag)
    sentinel = object()
    assert (
        resolve_hooked_option(config, non_existent_flag, default=sentinel)
        is sentinel
    )


@pytest.mark.parametrize(
    'targets',
    [
        # Single-target
        'foo::bar', 'foo.bar::baz', 'foo::bar.baz', 'foo.bar::baz.foobar',
        # Multiple-target
        'foo::bar,baz::foobar',
        'foo.bar::baz.foobar,spam.ham::eggs',
        'foo::bar,baz::foobar,spam.ham::eggs',
    ],
)
def test_recursive_autoprof_warning_regex(
    targets: Annotated[str, Parsable[List[ImportPath]]],
) -> None:
    """
    Test the formatting of `OptionParsingWarning` messages by
    `OptionParsingWarning.get_warning('recursive_autoprof', ...)`.
    """
    ipaths = ImportPath.parse_multiple(targets)
    pattern = OptionParsingWarning.get_regex('recursive_autoprof')
    warning = OptionParsingWarning.get_warning('recursive_autoprof', ipaths)
    message, *_ = warning.args
    assert f'found {len(ipaths)} ' in message
    if len(ipaths) == 1:
        assert ' it ' in message
        assert ' target ' in message
    else:
        assert ' them ' in message
        assert ' targets ' in message
    assert re.match(pattern, message)


@pytest.mark.parametrize(
    'paths',
    ['foo.bar', 'foo.bar,foo.baz', ('foo.bar::baz,foo.bar', 'spam.ham')],
)
@pytest.mark.parametrize(
    ('option', 'resolver'),
    [
        ('--autoprof-mod', AutoProfImporter.get_autoprof_mod),
        ('--always-autoprof', AutoProfImporter.get_always_autoprof),
    ],
)
def test_import_path_option_parsing(
    get_config: ConfigGetter,
    option: Literal['--autoprof-mod', '--always-autoprof'],
    resolver: Callable[[pytest.Config], Any],
    paths: Union[
        Annotated[str, Parsable[List[ImportPath]]],
        Sequence[Annotated[str, Parsable[List[ImportPath]]]],
    ],
) -> None:
    """
    Test the parsing of import-path options like `--autoprof-mod` and
    `--always-autoprof`, which accept multiple copies of the flag.
    """
    if isinstance(paths, str):
        paths = paths,
    flags = [f'{option}={path}' for path in paths]
    config = get_config(*flags)
    assert resolver(config) == ImportPath.parse_multiple(','.join(paths))


@pytest.mark.parametrize(
    ('paths', 'expected', 'expect_warning'),
    [
        # No flag -> no target (by default)
        ((), '', False),
        # Supplying multiple copies of `--recursive-autoprof` still
        # sets it to true...
        (None, True, False),
        ((None, None), True, False),
        # ... but as long as at least one explicit target is provided,
        # it is used instead
        ((None, 'foo.bar'), 'foo.bar', False),
        (('foo', 'bar,baz', None), 'foo,bar,baz', False),
        # The target with an object part is dropped from
        # `--recursive-autoprof`, and handled by `--always-autoprof`
        # with a warning)
        ((None, 'foo.bar,foobar::baz,spam', None), 'foo.bar,spam', True),
    ],
)
def test_recursive_autoprof_parsing(
    get_config: ConfigGetter,
    paths: Union[
        None,
        Annotated[str, Parsable[List[ImportPath]]],
        Sequence[Union[Annotated[str, Parsable[List[ImportPath]]], None]],
    ],
    expected: Union[Annotated[str, Parsable[List[ImportPath]]], Literal[True]],
    expect_warning: bool,
) -> None:
    """
    Test the parsing of `--recursive-autoprof`, which has special-casing
    compared to what `--autoprof-mod` and `--always-autoprof` do.
    """
    flags = []
    if isinstance(paths, str) or paths is None:
        paths = paths,
    for path in paths:
        if path is None:
            flags.append('--recursive-autoprof')
        else:
            flags.append('--recursive-autoprof=' + path)
    config = get_config(*flags)
    if expected in (True,):
        expected_ipaths: Union[Literal[True], List[ImportPath]] = True
    else:
        assert expected is not True  # Help `mypy` out
        expected_ipaths = ImportPath.parse_multiple(expected)
    if expect_warning:
        ctx: ContextManager = pytest.warns(OptionParsingWarning)
    else:
        ctx = contextlib.nullcontext()
    with ctx:
        assert (
            AutoProfImporter.get_recursive_autoprof(config) == expected_ipaths
        )
