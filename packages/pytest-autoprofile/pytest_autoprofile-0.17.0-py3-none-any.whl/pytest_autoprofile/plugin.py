"""
Set up the `pytest` hooks.
"""
import contextlib
import dataclasses
import enum
import functools
import io
import os
import pathlib
import re
import shlex
import sys
import shutil
import textwrap
import types

import pytest
try:
    from pytest import TerminalReporter
except ImportError:  # Not public API as of 8.3.5
    from _pytest.terminal import (  # type: ignore[no-redef]
        TerminalReporter,
    )

from . import _warnings as warnings, importers, option_hooks, setup
from ._multiprocessing import apply_monkey_patches
from ._typing import (
    Dict, List, Set, Tuple,
    Callable, Collection, Iterable, Generator, Mapping,
    Annotated, Any, Union, Optional,
    ChainedIdentifier, Identifier, LineProfilerViewOptions, ImportPath,
)
from .profiler import _LineStatsCollator
from .startup_hook import write_pth_hook


__all__ = (
    'pytest_addhooks',
    'pytest_addoption',
    'pytest_runtest_protocol',
    'pytest_sessionstart',
    'pytest_sessionfinish',
    'pytest_terminal_summary',
    'write_profiler_output',
    'get_modules_to_purge',
)

get_modules_to_purge = setup.get_modules_to_purge  # Compatibility

# -------------------------------------------------------------------- #
#                     Command-line/Config options                      #
# -------------------------------------------------------------------- #


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """
    Add the hooks in `~.option_hooks`.
    """
    pluginmanager.add_hookspecs(option_hooks)


def pytest_addoption(
    parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager,
) -> None:
    """
    Add the command-line options associated with the hooks in
    `~.option_hooks`.

    Notes
    -----
    New defaults supplied aren't necessarily visible at the time when
    command-line options are generated:
    - `conftest.py` values are NOT available.
    - Values supplied via other plugins MAY be available, if they are
      loaded BEFORE this plugin is.
    they are however consistently resolved at run-time by
    `~.option_hooks.resolve_hooked_option()`.
    """
    group = parser.getgroup('auto-profiling options (requires `line-profiler`)')
    for hook in option_hooks.Hook.hooks.values():
        hook.add_option(group)()


# -------------------------------------------------------------------- #
#                              Profiling                               #
# -------------------------------------------------------------------- #


def _get_short_path(
    fname: Union[pathlib.PurePath, str], *, quote: bool = False,
) -> str:
    get_realpath = os.path.realpath
    rpath = get_realpath(fname)
    result = min(
        rpath, os.path.relpath(rpath, get_realpath(os.curdir)), key=len,
    )
    if quote:
        result = shlex.quote(result)
    return result


_VERBOSITY_THRESHOLDS = types.SimpleNamespace(
    list_rewritten_modules=2,
    summarize_rewritten_modules=1,
    list_individual_doctests=3,
    list_doctests=2,
    summarize_doctests=1,
    implicit_outfile_dest=0,
    explicit_outfile_dest=1,
    line_profiler_usage=2,
)
_PROFILE_OUTPUT_MARKUPS = types.SimpleNamespace(
    lineno='yellow',
    metrics=('cyan', 'bold'),
    info=None,
    template='purple',
)


def _should_profile_subprocs(config: pytest.Config) -> bool:
    if not option_hooks.resolve_hooked_option(config, 'autoprof_subprocs'):
        return False
    stash = config.stash[importers.AUTOPROF_STASH_KEY]
    return setup._should_profile_subprocs(stash)


@contextlib.contextmanager
def _reemit_as_config_warnings(config: pytest.Config):
    def get_args(w: warnings.WarningMessage) -> list:
        if isinstance(w.message, Warning):
            return list(w.message.args)
        return [w.message]

    try:
        with warnings.catch_warnings(record=True) as record:
            yield
    finally:
        for warning_message in record:
            WClass = warning_message.category
            wargs = get_args(warning_message)
            # Note: it takes 2 to get back to this frame, and we add
            # another 2 to get beyond the `contextlib` frame, going back
            # to the frame using the context manager
            config.issue_config_time_warning(WClass(*wargs), stacklevel=4)


def get_verbosity(config: pytest.Config, /, *args, **kwargs) -> int:
    """
    Backwards-compatible way to get verbosity from a `config`.
    """
    try:
        return config.get_verbosity(*args, **kwargs)
    except AttributeError:  # `pytest < 8.0`
        pass
    if args or kwargs:
        msg = (
            f'*args = {args!r}, **kwargs = {kwargs!r}: '
            'ignoring arguments (`pytest.Config.get_verbosity()` not '
            f'available in version {pytest.__version__})'
        )
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
    return config.getoption('verbose')


def write_profiler_output(
    config: pytest.Config,
    write_line: Callable[[str], None],
    write: Callable[[str], None],
    collate: Collection[Union[str, pathlib.PurePath]] = (),
) -> None:
    """
    Parameters
    ----------
    config
        `pytest.Config`
    write_line(), write()
        Callables with the same signature as
        `pytest.TerminalReporter.write_line()` and `write()` resp.
    collate
        Optional collection of paths from which additional profiling
        data is to be collated

    Side effects
    ------------
    - Line-profiling result written to either:
      - `config.option.autoprof_outfile` (if parsed from the command
        line),
      - The appropriate default provided by a
        `pytest_autoprof_outfile_default()` implementation (if it
        exists), or
      - `cache_dir / 'pytest_autoprofile.lprof'`, where
        `cache_dir = config.rootpath / config.getini('cache_dir')`
    - Information about the output destination and how to read it
      (like what `kernprof` outputs) written with `write_line()`
    """
    class LineType(enum.Enum):
        SPACE = enum.auto()
        FUNC_HEADER = enum.auto()
        MISC_HEADER = enum.auto()
        TABLE_COLS = enum.auto()
        TABLE_SEP = enum.auto()
        PROFILING_OUTPUT = enum.auto()
        SUMMARY_OUTPUT = enum.auto()
        MISC_OUTPUT = enum.auto()

    LineAccumulator = Generator[
        Tuple[LineType, Dict[Annotated[str, Identifier], Any]], None, None,
    ]
    Markup = Union[
        Collection[Union[Annotated[str, Identifier], None]],
        Annotated[str, Identifier],
        None,
    ]

    def message(string: str, verbosity: float, **markup: bool) -> None:
        if get_verbosity(config) < verbosity:
            return
        write_line(string, **markup)

    def write_formatted_line(*chunks: Tuple[str, Markup]) -> None:
        kwargs: Dict[Annotated[str, Identifier], bool]
        for string, markup in chunks:
            kwargs = {}
            if markup is None or isinstance(markup, str):
                markup = markup,
            for m in markup:
                if m is None:
                    continue
                kwargs[m] = True
            write(string, **kwargs)
        write('\n')

    def classify_line(
        line: str, stop: int, parse_summary: bool,
    ) -> Tuple[LineType, Dict[Annotated[str, Identifier], Any]]:
        if not line or line.isspace():
            return LineType.SPACE, {}
        elif line.startswith('===='):
            return LineType.TABLE_SEP, {}
        elif line.startswith(('Total time: ', 'Timer unit: ', 'File: ')):
            field, _, value = line.rpartition(': ')
            return LineType.MISC_HEADER, {'field': field, 'value': value}
        table_cols = table_cols_line_match(line)
        if table_cols:
            stops = tuple(
                len(table_cols[field]) for field in ('lineno', 'percent')
            )
            return LineType.TABLE_COLS, {'stops': stops}
        func_header = func_header_line_match(line)
        if func_header:
            return LineType.FUNC_HEADER, func_header.groupdict()
        if parse_summary:
            summary_item = summary_line_match(line)
            if summary_item:
                return LineType.SUMMARY_OUTPUT, summary_item.groupdict()
        # Handle line-profiling output (lineno + metrics + source)
        # (Note: there could be edge cases where the source lines can't
        # be read/parsed, and an error message is output instead of a
        # line number, profiling data, and the source; catch that)
        try:
            int(line[:stop])
        except ValueError:  # No leading line number
            return LineType.MISC_OUTPUT, {}
        return LineType.PROFILING_OUTPUT, {}

    def accumulate_profiling_lines(
        lines: Iterable[str], parse_summary: bool,
    ) -> LineAccumulator:
        def get_prof_result() -> LineAccumulator:
            if not metrics:
                return
            info = {
                'metrics': metrics.copy(), 'source': '\n'.join(profiled_lines),
            }
            metrics.clear()
            profiled_lines.clear()
            yield LineType.PROFILING_OUTPUT, info

        metrics: List[Tuple[str, str]] = []
        profiled_lines: List[str] = []
        stops = (6, 47)  # Defaults
        for line in lines:
            ltype, info = classify_line(line, stops[0], parse_summary)
            if ltype == LineType.TABLE_COLS:
                stops = info['stops']
            if ltype == LineType.PROFILING_OUTPUT:
                # Consolidate all the source lines in the profiling
                # output
                metrics.append((line[:stops[0]], line[stops[0]:stops[1]]))
                profiled_lines.append(line[stops[1]:])
            else:
                # If we have any profiling lines gathered, yield them
                yield from get_prof_result()
                info['line'] = line
                yield ltype, info
        # Output trailing profiling lines, in any
        yield from get_prof_result()

    def write_results(result: str) -> None:
        if stat_kwargs['rich']:
            try:
                ImportPath('rich').import_target()
            except ImportError:
                pass
            else:  # Output already colorized with `rich`
                write_line(result)
                return
        # Use `pytest` facilities to colorize the output
        m_lineno = _PROFILE_OUTPUT_MARKUPS.lineno
        m_metrics = _PROFILE_OUTPUT_MARKUPS.metrics
        m_info = _PROFILE_OUTPUT_MARKUPS.info
        m_template = _PROFILE_OUTPUT_MARKUPS.template
        for ltype, info in accumulate_profiling_lines(
            result.splitlines(), stat_kwargs['summarize'],
        ):
            if ltype == LineType.SPACE:
                write_line(info['line'])
            elif ltype == LineType.FUNC_HEADER:
                write_formatted_line(
                    ('Function: ', m_template),
                    (info['func_name'], m_info),
                    (' at line ', m_template),
                    (info['lineno'], m_lineno),
                )
            elif ltype == LineType.MISC_HEADER:
                if info['field'] == 'Total time':
                    markup = m_metrics
                else:
                    markup = m_info
                write_formatted_line(
                    (info['field'] + ': ', m_template),
                    (info['value'], markup),
                )
            elif ltype in (LineType.TABLE_COLS, LineType.TABLE_SEP):
                write_formatted_line((info['line'], m_template))
            elif ltype == LineType.PROFILING_OUTPUT:
                highlighted_lines = highlight(info['source']).splitlines()
                assert len(info['metrics']) == len(highlighted_lines)
                for (lineno, other_metrics), source_line in zip(
                    info['metrics'], highlighted_lines,
                ):
                    write_formatted_line(
                        (lineno, m_lineno),
                        (other_metrics, m_metrics),
                        (source_line, None),
                    )
            elif ltype == LineType.SUMMARY_OUTPUT:
                write_formatted_line(
                    (info['time'], m_metrics),
                    (' seconds - ', m_template),
                    (info['filename'], m_info),
                    (':', m_template),
                    (info['lineno'], m_lineno),
                    (' - ', m_template),
                    (info['func_name'], m_info),
                )
            else:  # Misc
                write_formatted_line((info['line'], m_info))

    resolve = functools.partial(option_hooks.resolve_hooked_option, config)
    prof = config.stash[importers.AUTOPROF_STASH_KEY].profiler
    highlight = config.get_terminal_writer()._highlight
    func_header_line_match = re.compile(
        '^Function: +(?P<func_name>.*) +at line +(?P<lineno>[0-9]+)$'
    ).match
    table_cols_line_match = re.compile(
        '^(?P<percent>(?P<lineno> *Line #).*% Time)'
    ).match
    summary_line_match = re.compile(
        '^(?P<time> *.+)'  # Total time
        ' +seconds +-'
        ' +(?P<filename>.+):(?P<lineno>[0-9]+)'  # Filename, lineno
        ' +- +(?P<func_name>.+)$'  # Function name
    ).match

    try:
        outfile = config.option.autoprof_outfile
        if outfile is None:
            raise AttributeError
        dest_verbosity = _VERBOSITY_THRESHOLDS.explicit_outfile_dest
    except AttributeError:
        # Since the .lprof file isn't written to a destination
        # explicitly specified on the command line, output with a lower
        # verbosity threshold
        outfile = resolve('autoprof_outfile', kwargs={'config': config})
        dest_verbosity = _VERBOSITY_THRESHOLDS.implicit_outfile_dest
    outfile = _get_short_path(outfile)

    for alias in 'python', 'python3':
        which = shutil.which(alias)
        if not which:
            continue
        if os.path.samefile(sys.executable, which):
            python = alias
            break
    else:
        python = _get_short_path(sys.executable, quote=True)

    stats = _LineStatsCollator(prof.get_stats(refresh_cache=False), *collate)
    stats.dump(outfile)
    msg_chunks = ['Wrote profile results']
    if collate:
        n = len(collate)
        note = '(main process + {} subprocess{})'.format(
            n, '' if n == 1 else 'es',
        )
        msg_chunks.append(note)
    msg_chunks.extend(['to', shlex.quote(outfile) + '\n'])
    message(' '.join(msg_chunks), dest_verbosity, bold=True)

    view: Union[bool, LineProfilerViewOptions] = resolve('autoprof_view')
    if view:
        if view in (True,):
            stat_kwargs = dataclasses.asdict(LineProfilerViewOptions())
        else:
            assert view is not True  # Help `mypy` out
            stat_kwargs = dataclasses.asdict(view)
        with io.StringIO(newline=None) as sio:
            stats.show(stream=sio, **stat_kwargs)
            write_results(sio.getvalue().rstrip('\n'))
        write_line('')
    else:
        message(
            'Inspect results with:\n\n'
            f'  {python} -m line_profiler -rmt {shlex.quote(outfile)}\n',
            _VERBOSITY_THRESHOLDS.line_profiler_usage,
        )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item):
    """
    Clean up extra 'enable counts' that the profiler has accrued over
    the test, which may happen if a test did a profiled import and thus
    semi-permanently incremented the count.

    Notes
    -----
    Not sure why this matters, but if we don't clean up the
    `.enable_count`, it seems to disrupt the profiling of further tests
    in some cases.
    """
    prof = item.config.stash[importers.AUTOPROF_STASH_KEY].profiler
    count = prof.enable_count
    try:
        return (yield)
    finally:
        delta = prof.enable_count - count
        for _ in range(delta):
            prof.disable_by_count()


@pytest.hookimpl(wrapper=True)
def pytest_sessionstart(session: pytest.Session):
    """
    Install the importers, which rewrite tests and/or other modules on
    import to profile them.
    """
    config = session.config
    stash = importers.AutoProfStash.from_config(config, add_to_config=True)
    stash.profiler.install()
    # Get the importers and scrub the existing modules affected thereby
    # Note: it's more convenient (and makes for prettier output) to
    # centralize the emission of warnings here
    with _reemit_as_config_warnings(config):
        _handle_session_start(config, stash)
    # Set up subprocess tracing
    if _should_profile_subprocs(config):
        serialized_stash = stash._dump()
        write_pth_hook(stash=stash, serialized_stash=serialized_stash)
        apply_monkey_patches(
            stash=stash, serialized_stash=str(serialized_stash),
        )
    # Instead of manually calling the cleanup in
    # `pytest_sessionfinish()`, it is better to register it here,
    # because the execution order of the various implementations thereof
    # (one of which would do this cleanup, and the other writes the
    # output) is ill-defined
    config.add_cleanup(stash.cleanup)
    yield


def _handle_session_start(
    config: pytest.Config, stash: importers.AutoProfStash,
) -> None:
    modules_importer = importers.ProfileModulesImporter(config)
    tests_importer = importers.ProfileTestsImporter(config)
    # Trigger the `--recursive-autoprof` warnings by fetching
    # `.autoprof_targets`
    modules_importer.autoprof_targets
    tests_importer.autoprof_targets
    # Note: for the meta-paths to function, the modules in question must
    # not already be in `sys.modules` -- so we have to scrub it
    scrubbing_result = setup._scrub_imported_modules(
        sys.modules, modules_importer, tests_importer,
        scrubbed_modules=stash.existing,
        register_importer=stash.add_importer,
    )

    if modules_importer.postimport_autoprof:
        # Handle `--postimport-autoprof` (this may trigger warnings)
        modules_importer.add_targets_explicitly()
    elif not scrubbing_result.use_modules_importer:
        del modules_importer

    if not scrubbing_result.use_tests_importer:
        del tests_importer


@pytest.hookimpl(wrapper=True)
def pytest_sessionfinish(session: pytest.Session):
    """
    Uninstall the importers installed in `pytest_sessionstart()` (if
    any).
    """
    try:
        return (yield)
    finally:
        with _reemit_as_config_warnings(session.config):
            _handle_session_end(session)


def _handle_session_end(session: pytest.Session) -> None:
    def fill(s: str, indent: Union[str, int], **kwargs) -> str:
        try:
            indent = ' ' * indent  # type: ignore[operator]
        except TypeError:  # Already a string
            pass
        kwargs.setdefault('initial_indent', indent)
        kwargs.setdefault('subsequent_indent', indent)
        kwargs.setdefault('break_long_words', False)
        return textwrap.fill(s, **kwargs)

    def pl(noun: str, count: int, bracket: bool = False) -> str:
        if count == 1:
            pass
        elif noun.endswith(('s', 'x')):
            noun += 'es'
        elif noun.endswith('y'):
            noun = noun[:-1] + 'ies'
        else:
            noun += 's'
        return ('{1} ({0})' if bracket else '{} {}').format(count, noun)

    def format_fname(fname: Union[str, None]) -> str:
        if fname is None:
            return '???'
        return _get_short_path(fname, quote=True)

    def get_doctest_message(
        tests: Mapping[Union[str, None], Set[str]],
        *,
        verbose: Optional[float] = None,
        verb: str = 'profiled',
        passive: Optional[str] = None,
    ) -> List[Tuple[str, Dict[Annotated[str, Identifier], Any]]]:
        def log(msg: str, verbosity: int = 1, **markup: bool) -> None:
            result.append((msg, {'verbosity': verbosity, **markup}))

        tests_ = {
            format_fname(fname): items
            for fname, items in sorted(tests.items()) if items
        }
        if verbose is None:
            verbose = verbosity
        if passive is None:
            passive = verb
        if not tests_:
            return []
        result: List[Tuple[str, Dict[Annotated[str, Identifier], Any]]] = []
        ntests = sum(len(items) for items in tests_.values())
        nfiles = len(tests_)
        if verbose >= list_indev_threshold:
            pattern = '{1} {0} in {2}:'
            btests = bfiles = True
            use_passive = True
        elif verbose >= list_files_threshold:
            pattern = '{1} {0} in {2}:'
            btests, bfiles = False, True
            use_passive = True
        else:
            pattern = '{} {} in {}'
            btests = bfiles = False
            use_passive = False
        if use_passive:
            verb = passive
        message = pattern.format(
            verb, pl('doctest', ntests, btests), pl('file', nfiles, bfiles),
        ).capitalize()
        log(message, summarize_threshold, bold=True)
        log_detail = functools.partial(log, verbosity=list_files_threshold)
        if verbose >= list_indev_threshold:
            for fname, items in tests_.items():
                log_detail('{}\n{}'.format(
                    fill(f'{fname} ({pl("doctest", len(items))}):', 2),
                    fill(', '.join(sorted(items)), 4),
                ))
        else:
            log_detail(fill(', '.join(tests_), 2))
        return result

    config = session.config
    verbosity = get_verbosity(config)
    stash = config.stash[importers.AUTOPROF_STASH_KEY]
    prof = stash.profiler
    log = stash.log
    # Uninstall importers, restore `sys.modules`, summarize the profiled
    # imports
    list_threshold = _VERBOSITY_THRESHOLDS.list_rewritten_modules
    summarize_threshold = min(
        _VERBOSITY_THRESHOLDS.summarize_rewritten_modules, list_threshold,
    )
    old_modules: Dict[
        Annotated[str, ChainedIdentifier], Union[types.ModuleType, None]
    ] = dict(stash.existing)
    remember = old_modules.setdefault
    if verbosity >= list_threshold:
        log_pattern = '{0.__module__}.{0.__qualname__}: rewrote {1}:'
        bnames = True
    else:
        log_pattern = (
            '{0.__module__}.{0.__qualname__}: rewrote and profiled {1}'
        )
        bnames = False
    for importer in stash.importers:
        names = importer.imported_names
        if names:
            summary = log_pattern.format(
                type(importer), pl('module', len(names), bnames),
            )
            log(summary, summarize_threshold, bold=True)
            log(fill(', '.join(sorted(names)), 2), list_threshold)
        importer.uninstall()
        for name in importer.imported_names:
            remember(name)
    mods = sys.modules
    pop_mod = mods.pop
    for name, module in old_modules.items():
        pop_mod(name, None)
        if module is not None:
            mods[name] = module
    # Summarize the profiled doctests
    list_indev_threshold = _VERBOSITY_THRESHOLDS.list_individual_doctests
    list_files_threshold = min(
        _VERBOSITY_THRESHOLDS.list_doctests, list_indev_threshold,
    )
    summarize_threshold = min(
        _VERBOSITY_THRESHOLDS.summarize_doctests, list_files_threshold,
    )
    if prof.autoprof_doctests:
        prof.get_stats()  # Fetch all the profiling results
        package, *_ = __spec__.name.rpartition('.')
        for msg, kwargs in get_doctest_message(prof.profiled_doctests):
            log(msg, **kwargs)
        # If we're already outputting the individual tests which aren't
        # profiled, don't do it again in the warning text
        if verbosity >= list_indev_threshold:
            warning_verbosity = summarize_threshold
        else:
            warning_verbosity = list_indev_threshold
        for tests, verb, passive in [
            (
                prof.non_profiled_doctests,
                'could not profile',
                'could not be profiled',
            ),
            (prof.omitted_doctests, 'omitted from profiling output', None),
        ]:
            if not tests:
                continue
            get_message = functools.partial(
                get_doctest_message, tests, verb=verb, passive=passive,
            )
            for msg, kwargs in get_message():
                log(msg, **kwargs)
            warning_msg = '\n'.join(
                msg for msg, _ in get_message(verbose=warning_verbosity)
            )
            warnings.warn(warning_msg, warnings.DoctestProfilingWarning)


def pytest_terminal_summary(
    terminalreporter: TerminalReporter, config: pytest.Config,
) -> None:
    """
    Write the profiling results and print the location of the output
    like `kernprof` does.
    """
    @functools.wraps(terminalreporter.write_line)
    def write_line_later(
        text: str, *, insert_blank_line: bool = False, **kwargs
    ) -> None:
        lines_to_write.append((text, kwargs, write_line, insert_blank_line))

    @functools.wraps(terminalreporter.write)
    def write_later(text: str, **kwargs) -> None:
        lines_to_write.append((text, kwargs, write, False))

    lines_to_write: List[
        Tuple[
            str,  # Text to write
            Dict[Annotated[str, Identifier], Any],  # Markup
            Callable[[str], Any],  # Writer
            bool,  # Write trailing blank line
        ]
    ] = []
    write = terminalreporter.write
    write_line = terminalreporter.write_line
    stash = config.stash[importers.AUTOPROF_STASH_KEY]
    verbosity = get_verbosity(config)
    subprocs_profiled = _should_profile_subprocs(config)
    # Gather all the lines to write
    for msg, threshold, markup in stash.log_messages:
        if verbosity < threshold:
            continue
        write_line_later(msg, **{'insert_blank_line': True, **markup})
    if subprocs_profiled:
        collate = [
            result for result in stash.scratch_dir.glob('autoprof-*.lprof')
            if result.stat().st_size
        ]
    else:
        collate = []
    if stash.profiler_used or collate:
        write_profiler_output(
            config, write_line_later, write_later, collate=collate,
        )
    # Write the lines with a leading separator
    if not lines_to_write:
        return
    main_color, _ = terminalreporter._get_main_color()
    write_line('')
    terminalreporter.write_sep('=', 'auto-profiling', **{main_color: True})
    write_line('')
    for text, markup, writer, insert_blank_line in lines_to_write:
        writer(text, **markup)
        if insert_blank_line:
            write_line('')
