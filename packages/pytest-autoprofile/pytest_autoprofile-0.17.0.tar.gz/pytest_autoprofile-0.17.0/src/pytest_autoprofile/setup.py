"""
Functionalities which have to do with managing global states, to be
used when starting a test session or a subprocess.
"""
import dataclasses
from importlib import invalidate_caches as _invalidate_caches
from operator import methodcaller
from types import ModuleType

from ._typing import (
    Dict, Set,
    Callable, Iterable,
    Annotated, Any, Optional,
    ChainedIdentifier,
)
from .importers import _AutoProfImporterBase, AutoProfStash


__all__ = ('get_modules_to_purge',)


@dataclasses.dataclass
class _ModuleScrubbingResult:
    scrubbed_modules: Dict[str, ModuleType] = dataclasses.field(
        default_factory=dict,
    )
    use_modules_importer: bool = False
    use_tests_importer: bool = False


def get_modules_to_purge(
    all_modules: Iterable[Annotated[str, ChainedIdentifier]],
    purged: Iterable[Annotated[str, ChainedIdentifier]],
) -> Set[Annotated[str, ChainedIdentifier]]:
    """
    Example
    -------
    >>> assert (
    ...     get_modules_to_purge(
    ...         ['foo', 'foo.bar', 'baz'], ['foo', 'bar'],
    ...     )
    ...     == {'foo', 'foo.bar'}
    ... )
    """
    all_modules = set(all_modules)
    purged = set(purged)
    results = all_modules & purged
    prefixes = tuple({target + '.' for target in purged})
    results |= {module for module in all_modules if module.startswith(prefixes)}
    return results


def _should_profile_subprocs(stash: AutoProfStash) -> bool:
    return bool(stash.importers) or bool(stash.profiler.tee_global_prof)


def _scrub_imported_modules(
    mods: Dict[Annotated[str, ChainedIdentifier], ModuleType],
    modules_importer: Optional[_AutoProfImporterBase] = None,
    tests_importer: Optional[_AutoProfImporterBase] = None,
    *,
    scrubbed_modules: Optional[
        Dict[Annotated[str, ChainedIdentifier], ModuleType]
    ] = None,
    register_importer: Callable[
        [_AutoProfImporterBase], Any
    ] = methodcaller('install'),
    invalidate_caches: bool = True,
) -> _ModuleScrubbingResult:
    """
    Scrub modules affected by the importers from `mods`.

    Parameters
    ----------
    mods
        `sys.modules`
    modules_importer, tests_importer
        Optional importer objects with interfaces like
        `~.importers.ProfileModulesImporter` and
        `~.importers.ProfileTestsImporter` resp.
    scrubbed_modules
        Optional dictionary to store the scrubbed modules (with the
        same format as `sys.modules`);
        default is to create a new dictionary
    register_importer
        Callable to call on the importers if they are to be registered
        as used for altering imports;
        default is to call the importer objects' `.install()` method
    invalidate_caches
        Whether to invalidate the caches of `importlib` if any module
        has been scrubbed

    Return
    ------
    Object with the following attributes:
        .scrubbed_modules
            `scrubbed_modules`
        .use_modules_importer, .use_tests_importer
            Whether `modules_importer` and `tests_importer` have resp.
            been registered as used
    """
    pop_mod = mods.pop
    get_mod = mods.get
    if scrubbed_modules is None:
        scrubbed_modules = {}
    # Module importer
    use_modules_importer = False
    if modules_importer is None:
        always_autoprof_targets: Set[Annotated[str, ChainedIdentifier]] = set()
    else:
        always_autoprof_targets = {
            module for module, _ in modules_importer.autoprof_targets
        }
    if always_autoprof_targets:
        assert modules_importer is not None
        use_modules_importer = True
        register_importer(modules_importer)
        scrubbed_modules.update(
            (name, pop_mod(name)) for name in get_modules_to_purge(
                mods, always_autoprof_targets,
            )
        )
    # Test importer
    use_tests_importer = False
    remember_module = scrubbed_modules.setdefault
    if (
        tests_importer is not None and
        (
            tests_importer.autoprof_targets or
            tests_importer.autoprof_tests or
            tests_importer.autoprof_mod
        )
    ):
        use_tests_importer = True
        register_importer(tests_importer)
        assert hasattr(tests_importer, 'matcher')
        matcher: Callable[[str], bool] = tests_importer.matcher
        for name in set(mods):
            try:
                orig = (
                    get_mod(name)
                    .__spec__.origin  # type: ignore[union-attr]
                )
                reimport = matcher(orig)  # type: ignore[arg-type]
            except Exception:
                reimport = False
            if reimport:
                remember_module(name, pop_mod(name))
    # Bookkeeping
    if scrubbed_modules and invalidate_caches:
        _invalidate_caches()
    return _ModuleScrubbingResult(
        scrubbed_modules, use_modules_importer, use_tests_importer,
    )
