`pytest-autoprofile`
====================

![Repo mascot: a snake wearing a watch, looking at test results][repo-mascot]

Table of contents
-----------------

<details>
<summary> Click to expand </summary>

[[_TOC_]]

</details>

Overview
--------

This plugin package brings the full power of
[`line_profiler.autoprofile`][line-profiler-autoprofile] to your
[`pytest`][pytest-source] test suite –
and then more.

Features
--------

- Automatic line profiling of normal tests and
  [doctests](#doctest-profiling)
- [Import-time rewriting](#module-rewriting) of arbitrary
  (test, codebase, external, standard-lib)
  Python modules
- Aggregation of in-process and
  [subprocess line-profiling](#subprocess-profiling) results

Motivation
----------

Leveraging the pre-existing test suite can be a good start for some
quick-and-dirty benchmarking and profiling.
<sup>[[citation needed][wikipedia-citation-needed]]</sup>
While existing solutions like
[`pytest-line-profiler`][pytest-line-profiler-source] already serve to
bridge [`pytest`][pytest-source] and
[`line_profiler`][line-profiler-source],
they aren't using newer features of the latter like
[auto-profiling][line-profiler-autoprofile],
which mitigates the need to explicitly supply the profiled items via
either the command line,
or _shudders_ changing the source code to insert the
[`@profile`][line-profiler-profile] decorator.
And what's a quicker and dirtier way to do your profiling,
than to just feed the whole test suite to the profiler and see what
happens?

Requirements
------------

- `python >= 3.8`
- `pytest >= 7.0`
- `pluggy >= 1.2`
- `line_profiler >= 5.0`

### Optional requirements

These packages/plugins are not required for `pytest-autoprofile` to
function independently;
but if you want to use them *in conjunction* with `pytest-autoprofile`,
they have to be of the appropriate versions:
- `pytest-doctestplus >= 0.10`
- `xdoctest >= 0.12`

### <a name='notes-requirements'></a> Notes

If you're having issues with installation,
try upgrading `pip`:
```console
$ pip install --upgrade pip
```

Example
-------

<details>
<summary> Click to expand </summary>

```console
$ pytest --help
usage: pytest [options] [file_or_dir] [file_or_dir] [...]

...

auto-profiling options (requires `line-profiler`):
  --always-autoprof=MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]
                        ...
  --recursive-autoprof=[MODULE.DOTTED.PATH[,...]]
                        ...
  --postimport-autoprof=[MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]]
                        ...
  --autoprof-mod=MODULE.DOTTED.PATH[::OBJECT.DOTTED.PATH][,...]
                        ...
  --autoprof-imports=[yes|no]
                        ...
  --autoprof-tests=[yes|no]
                        ...
  --autoprof-doctests=[all|yes|no]
                        ...
  --autoprof-rewrite-doctests=[yes|no]
                        ...
  --autoprof-subprocs=[yes|no]
                        ...
  --autoprof-outfile=FILENAME
                        ...
  --autoprof-view=[yes|no|FLAGS]
                        ...
  --autoprof-global-profiler=[always|yes|no]
                        ...

...

$ pytest --verbose --verbose --verbose \
> --autoprof-imports --autoprof-tests --autoprof-doctests \
> --always-autoprof=my_pkg.funcs::foo --autoprof-view=-tm
================================= test session starts ==================================

...

==================================== auto-profiling ====================================

pytest_autoprofile.importers.ProfileTestsImporter: rewrote module (1):

  test_misc

pytest_autoprofile.importers.ProfileModulesImporter: rewrote module (1):

  my_pkg.funcs

Doctests (5) profiled in files (2):

  packages/my_pkg/classes.py (2 doctests):
    my_pkg.classes.SomeClass, my_pkg.classes.SomeClass.instance_method

  packages/my_pkg/funcs.py (3 doctests):
    my_pkg.funcs, my_pkg.funcs.bar, my_pkg.funcs.foo

Doctests (2) omitted from profiling output in file (1):

  packages/my_pkg/funcs.py (2 doctests):
    my_pkg.funcs.baz, my_pkg.funcs.foobar

Wrote profile results to .pytest_cache/pytest_autoprofile.lprof

...
Function: foo at line 20

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    20                                           def foo():
    21                                               """This test has a statically-defined doctest which will be
    22                                               profiled. The docstring is also formatted differently (no leading
    23                                               newline) to test if it has an effect (which it shouldn't) on
    24                                               profiling and collection.
    25                                           
    26         1          2.0      2.0     33.3      >>> x = foo() + 1
    27         1          0.0      0.0      0.0      >>> assert x == 2
    28                                           
    29                                               Doctest chunk containing a function definition:
    30                                           
    31         1          0.0      0.0      0.0      >>> def foofoo(s):
    32                                               ...     stop = foo()
    33                                               ...     return s[:stop]
    34                                               ...
    35                                               >>>
    36         1          3.0      3.0     50.0      >>> foofoo('string')
    37                                               's'
    38                                               """
    39         3          1.0      0.3     16.7      return 1

...

=============================== short test summary info ================================
...
```

</details>

How it works
------------

The [meta-path finders-slash-loaders][python-import-system]
[`~.importers.AutoProfImporter`](src/pytest_autoprofile/importers.py)
rewrite modules/packages and tests on import,
much like how [`pytest`][pytest-source] also does its own
[rewrites for assertions][pytest-assert] in tests.
A specialized [`doctest.DocTestRunner`][python-doctest-DocTestRunner]
subclass is used for doctest profiling and rewriting.

### Module rewriting

Modules and packages are rewritten with
`~.importers.ProfileModulesImporter`,
which does profiling on full module objects and/or specific objects
therein with
[`~.rewriting.StrictModuleRewriter.transform_module()`](src/pytest_autoprofile/rewriting.py).
This allows for more fine-grained control over module profiling than
what [`AstTreeModuleProfiler`][line-profiler-AstTreeModuleProfiler]
affords,
before they are even imported by tests,
and regardless of whether they are directly imported or not.

- <a name='always-autoprof'>`--always-autoprof`</a>
  ([dotted-path flag](#dotted-path-parsing); default: nil):  
  importable targets to auto-profile throughout the entire test session,
  not only when imported by individual tests:
  - If a module-level target,
    all function and method definition local to the module
    (see [Notes](#notes-module-rewriting))
    are rewritten on import to be decorated with
    [`@line_profiler.profile`][line-profiler-profile],
    like what
    [`AstProfileTransformer`][line-profiler-AstProfileTransformer]
    does;
  - Otherwise
    (i.e. if the target has an [object part](#dotted-path-parsing)),
    it is either decorated as above
    (if a function/method/class definition local to its module),
    or via (a patched version of)
    `line_profiler.LineProfiler.add_imported_function_or_module()`
    ([original][line-profiler-utils],
    [patched](src/pytest_autoprofile/profiler.py)).
- <a name='recursive-autoprof'>`--recursive-autoprof`</a>
  ([dotted-path flag](#dotted-path-parsing) (optional); default: nil):  
  module- or package-name targets to auto-profile as with above,
  but inclusive of all their sub-modules and -packages;
  can also be supplied without the argument,
  which indicates that all module-level targets in
  [`--always-autoprof`](#always-autoprof) are to be treated recursively.

#### <a name='notes-module-rewriting'></a> Notes

- Only targets accessible from the module-local namespace are decorated:
  ```python
  def some_func():  # This is decorated
      def nested_func(): ...  # This isn't
  
  
  class SomeClass:
      def some_method(self):  # This is decorated
          def nested_method(): ...  # This isn't
  
      class SomeInnerClass:
          def some_inner_method(self):  # This is decorated
              def nested_inner_method(): ...  # This isn't
  ```
- If a target in [`--recursive-autoprof`](#recursive-autoprof) has an
  [object part](#dotted-path-parsing),
  it is transferred to [`--always-autoprof`](#always-autoprof) with a
  warning:
  ```console
  $ pytest --recursive-autoprof=foo.bar::baz,spam,ham::eggs ...
  ...
  ...: OptionParsingWarning: --recursive-autoprof: found 2 invalid (non-module) targets (foo.bar::baz,ham::eggs), moving them to `--always-autoprof`
  ...
  ```
- [`--recursive-autoprof`](#recursive-autoprof) resolves to `True`
  (i.e. all [`--always-autoprof`](#always-autoprof) module targets
  should be profiled recursively) only if all of the passed
  `--recursive-autoprof` flags are in the no-argument form, so
  ```console
  $ pytest --always-autoprof=foo --recursive-autoprof=bar --recursive-autoprof
  ```
  profiles `bar` recursively but not `foo`.

### Test rewriting

Test are rewritten with `~.importers.ProfileTestsImporter`,
which does the same rewrites on tests as for scripts run with
[`kernprof -l --prof-mod=... [--prof-imports] ...`][kernprof-docs],
using
[`AstTreeProfiler.profile()`][line-profiler-AstTreeProfiler-profile].
This is on top of the [`pytest` assertion rewrites][pytest-assert]
(when appropriate),
so rich comparisons in assertions (or the lack thereof) work the same
as otherwise.

- <a name='autoprof-tests'>`--autoprof-tests`</a>
  ([boolean flag](#boolean-parsing); default: `False`):  
  whether to profile entire test modules;
  equivalent to adding each test file to
  [`--autoprof-mod`](#autoprof-mod) as it is run.
- <a name='autoprof-mod'>`--autoprof-mod`</a>
  ([dotted-path flag](#dotted-path-parsing): default: nil):  
  equivalent to [`kernprof -l`'s `--prof-mod` flag][kernprof-docs];
  if any of those targets is directly imported in the tests,
  it is profiled with the facilities of
  [`line_profiler`][line-profiler-docs].
- <a name='autoprof-imports'>`--autoprof-imports`</a>
  ([boolean flag](#boolean-parsing); default: `False`):  
  equivalent to [`kernprof -l`'s `--prof-imports`][kernprof-docs] flag;
  if an entire test module is already profiled
  (via [`--autoprof-tests`](#autoprof-tests) or explicit inclusion in
  [`--autoprof-mod`](#autoprof-mod)),
  also profile *all* its imports with
  [`line_profiler`][line-profiler-docs].

### Doctest profiling

Doctests are line-profiled as they are executed with the help of
[`~._doctest.get_doctest_handler_class()`](src/pytest_autoprofile/_doctest.py),
which builds the appropriate helper class running and profiling
doctests;
e.g. when using the vanilla doctest facilities of `pytest`,
it creates a [`doctest.DocTestRunner`][python-doctest-DocTestRunner]
subclass,
like what [`_pytest.doctest._init_runner_class()`][pytest-doctest]
does.
Optionally,
it also does the same import and function-/method-definition rewrites
according to [`--autoprof-mod`](#autoprof-mod) and
[`--autoprof-imports`](#autoprof-imports) as with normal tests.

- <a name='autoprof-doctests'>`--autoprof-doctests`</a>
  (extended [boolean flag](#boolean-parsing) with special value `'all'`;
  default: `False`):
  - **`'all'`, `'A'`, etc.**:  
    Profile all the collected doctests that are
    [tractable](#notes-doctest-profiling),
    similar to how [`--autoprof-tests`](#autoprof-tests) works for
    regular tests;
    this is the value defaulted to ([instead of true](#boolean-parsing))
    when using the zero-argument form of the option
  - **True**:  
    Profile collected tractable doctests if they belong to modules,
    classes, functions, etc. covered by
    [`--autoprof-mod`](#autoprof-mod)
  - **False**:  
    Don't profile doctests
- <a name='autoprof-rewrite-doctests'>`--autoprof-rewrite-doctests`</a>
  ([boolean flag](#boolean-parsing);
  default `False`)
  whether to profile imports (resp. function/method definitions) in
  doctests via AST rewriting if resp.:
  - [`--autoprof-mod`](#autoprof-mod) or
    [`--autoprof-doctests`](#autoprof-doctests)
    indicate that the Python files they reside in should have
    function/method definitions rewritten
  - [`--autoprof-mod`](#autoprof-mod) or
    [`--autoprof-imports`](#autoprof-imports) indicate that the specific
    imports in the Python files they reside in should be rewritten

#### <a name='notes-doctest-profiling'></a> Notes

- "Tractable" doctests are those that
  - Reside in bodied Python objects
    (i.e. modules and function/method/class definitions), and
  - Defined literally as the first expressions in said bodies.

  <details>
  <summary> Click to expand </summary>

  ```python
  def some_function():  # This doctest can be profiled...
      """
      >>> something = ...
      >>> some_function(something)
      """


  def other_function():
      ...


  # But this can't since it defies static analysis
  other_function.__doc__ = f'>>> other_function()\n{expected_output!r}'


  def add_doc(doc):
      def wrapper(func):
          func.__doc__ = doc
          return func

      return wrapper


  @add_doc("""
  >>> yet_another_function()
  SOME_EXPECTED_OUTPUT
  """)
  def yet_another_function():  # And neither can this
      ...
  ```

  </details>

  Only tractable doctests are included in the profiling output,
  because [`line_profiler`][line-profiler-docs] expects the profiled
  files to be Python source files,
  [parsing their lines into snippets][line-profiler-output-getblock]
  consisting of blocks of bodied objects to format its output.
  As such,
  profiled doctests must be able to be attributed to specific lines in a
  Python source file with static analysis.
- Compatibility with other doctest plugins is limited:
  - [`pytest-doctestplus >= 0.10`][pytest-doctestplus-source] and
    [`xdoctest >= 0.12`][xdoctest-source] are partially supported:
    `get_doctest_handler_class()` checks at runtime whether their
    doctest facilities or that of vanilla `pytest`'s should be used,
    and sets up the appropriate overrides;
    of course,
    the aforementioned restrictions on tractable tests still apply.
  - As discussed above,
    profiling is not possible for doctests residing in various
    non-Python files (like `.rst` and `.md` files) discovered by the
    various [doctest-related plugins][pytest-plugins],
    including `pytest-doctestplus`.

### Subprocess profiling

Both forked and spawned Python subprocesses can be profiled,
setting up the same profiling targets as outlined in
[Module rewriting](#module-rewriting) and
[Test rewriting](#test-rewriting),
and writing the profiling data on exit which are later collated.
This is achieved by:
- Writing the appropriate (temporary)
  [`.pth` file][python-site] so that spawned subprocesses install the
  [appropriate hooks](src/pytest_autoprofile/startup_hook.py),
- [Monkey-patching](src/pytest_autoprofile/startup_hook.py)
  [`os.fork()`][python-os-fork] to set up profiling for
  forked processes,
  and
- [Monkey-patching](src/pytest_autoprofile/_multiprocessing.py)
  [`multiprocessing`][python-multiprocessing]
  to ensure the writing of profiling data after code is executed in
  subprocesses.

See however especially the [following notes](#notes-subproc-profiling).

- <a name='autoprof-subprocs'>`--autoprof-subprocs`</a>
  ([boolean flag](#boolean-parsing); default: `False`):  
  whether to profile subprocesses.

#### <a name='notes-subproc-profiling'></a> Notes

- Since this writes a `.pth` file,
  write permission is needed for the directory
  [`sysconfig.get_path('purelib')`][python-sysconfig-get_path] points
  to.
- To avoid affecting other Python processes using the same installation
  paths,
  the environment variable `${PYTEST_AUTOPROFILE_TEST_PID}` is
  (temporarily) set so that only subprocesses inheriting it are affected
  by said `.pth` file,
  and the file itself is removed as soon as the test session terminates.
  Still,
  this means extra code is imported and executed for all Python
  interpreters on startup throughout the (short) lifetime of the file,
  and has obvious performance implications.
- <a name='multiproc-caveat'></a>To ensure that profiling data is
  correctly gathered from [`multiprocessing`][python-multiprocessing]
  subprocesses,
  one should take care to properly finalize them,
  e.g. by explicitly [`.close()`][python-multiprocessing-Pool-close]-ing
  and [`.join()`][python-multiprocessing-Pool-join]-ing process pools
  (see also
  [`coverage.py`'s caveat on `multiprocessing`][coverage-multiproc-caveat]).
  Otherwise,
  incomplete profiling data may be written and temporary files may not
  be properly cleaned up.

### Output

The `.lprof` file and terminal output is only written if any actual
function, method, property, code, etc. has been passed to the profiler
(or profilers in subprocesses if `--autoprof-subprocs` is set).

- <a name='autoprof-outfile'>`--autoprof-outfile`</a>
  (default: `<root_dir> / <cache_dir> / 'pytest_autoprof.lprof'`):  
  filename to which the profiling data should be written,
  equivalent to [`kernprof -l`'s `--outfile` flag][kernprof-docs].
- <a name='autoprof-view'>`--autoprof-view`</a>
  (extended [boolean flag](#boolean-parsing) also taking
  [`python -m line_profiler`][line-profiler-docs] options (see below);
  default: `False`):  
  equivalent to [`kernprof -l`'s `--view` flag][kernprof-docs],
  showing the profiling results at the end of the test session.
  Can also be a string to be [`shlex.split()`][python-shlex-split] into
  the CLI options for [`python -m line_profiler`][line-profiler-docs],
  which then causes the results to be displayed as if the `.lprof` file
  has been passed thereto with said options;
  valid options are:
  - `-c CONFIG`/`--config=CONFIG`, `--no-config`:  
    Load configuration from the provided file
    (or the [default config file][line-profiler-default-config] that
    ships with `line_profiler` if `--no-config`);
    if any of the following flags/flag pairs is not passed,
    the value is resolved therefrom
  - `-u UNIT`/`--unit=UNIT`:  
    Set the `output_unit` argument (positive finite real number) for the
    [`LineProfiler.print_stats()`][line-profiler-LineProfiler-print_stats]
    call
  - `-z`/`--skip-zero`, `--no-skip-zero`:  
    Whether to set `stripzeros=True` for said call
  - `-r`/`--rich`, `--no-rich`; `-t`/`--sort`, `--no-sort`;
    `-m`/`--summarize`, `--no-summarize`:  
    Whether to set the synonymous arguments to `True` for said call

#### <a name='notes-output'></a> Notes

- `<root_dir>` refers to the [`pytest` root directory][pytest-root-dir],
  which usually is where your project specs are.
- `<cache_dir>` is `'.pytest_cache'` unless you
  [otherwise configured `pytest`][pytest-cache-dir].
- At neutral verbosity level or above,
  the filename where the profiling data is written to (if any) is always
  shown at the end of the test session *unless* it is explicitly
  specified by the [`--autoprof-outfile`](#autoprof-outfile) flag.
- If [`--autoprof-view`](#autoprof-view) doesn't resolve to false and
  the profiler has been used,
  the terminal output is always written regardless of verbosity level.
- If none of `-c`/`--config`/`--no-config` is specified in
  [`--autoprof-view`](#autoprof-view),
  the configuration is loaded from the default resolved location
  (see [`line_profiler.toml_config`][line-profiler-toml_config]).

### Miscellaneous options

- <a name='postimport-autoprof'>`--postimport-autoprof`</a>
  ([dotted-path flag](#dotted-path-parsing) (optional); default: nil):  
  importable targets to auto-profile throughout the entire test session
  like [`--always-autoprof`](#always-autoprof) and
  [`--recursive-autoprof`](#recursive-autoprof),
  except that instead of rewriting entire modules *at import time*,
  profiling targets are explicitly imported *then* profiled;
  can also be supplied without the argument,
  which indicates that all targets in
  [`--always-autoprof`](#always-autoprof) and
  [`--recursive-autoprof`](#recursive-autoprof) are to be profiled
  post-import.
- <a name='autoprof-global-profiler'>`--autoprof-global-profiler`</a>
  (extended [boolean flag](#boolean-parsing) with special value `'always'`;
  default: `False`):
  - **`'always'`, `'A'`, etc.**:  
    Profile everything passed to
    [`@line_profiler.profile`][line-profiler-profile],
    regardless of whether it is `.enabled` or not;
    this is the value defaulted to ([instead of true](#boolean-parsing))
    when using the zero-argument form of the option
  - **True**:  
    Profile everything passed to
    [`@line_profiler.profile`][line-profiler-profile] when it is
    `.enabled`
  - **False**:  
    Don't profile objects passed to
    [`@line_profiler.profile`][line-profiler-profile]
    (unless it is otherwise already included in profiling by e.g.
    [module](#module-rewriting),
    [test](#test-rewriting),
    or [doctest](#autoprof-rewrite-doctests) rewriting)

#### <a name='notes-misc'></a> Notes

- When supplied with arguments,
  [`--postimport-autoprof`](#postimport-autoprof) infers which
  module/package targets to recurse into and which not to:
  - If the target is also found in
    [`--recursive-autoprof`](#recursive-autoprof)
    (or is implied by the no-argument form thereof),
    the module is recursed into.
  - Else,
    if the target is also found in
    [`--always-autoprof`](#always-autoprof),
    it is taken to be explicitly specified to **not** be recursed into.
  - Otherwise,
    it is recursed into.
- [`--postimport-autoprof`](#postimport-autoprof)
  is in a sense highly overlapping with
  [`--always-autoprof`](#always-autoprof) and
  [`--recursive-autoprof`](#recursive-autoprof) in function,
  but it covers the following corner cases:
  - When modules have already been loaded and for whatever reasons
    cannot be unloaded at the beginning of the test session.
    This can happen e.g. with Cython modules,
    which persists even after a call to
    [`importlib.invalidate_caches()`][python-importlib-invalidate_caches].
  - When profiling [`line_profiler`][line-profiler-docs] itself or its
    components.
- The default behavior prior to v0.12.0 was roughly equivalent to
  [`--autoprof-global-profiler=always`](#autoprof-global-profiler);
  however,
  since it altered the internal state of
  [`@line_profiler.profile`][line-profiler-profile]
  (replacing its inner `LineProfiler` instance)
  using the same hook that [`kernprof`][kernprof-docs] uses,
  the normal outputs
  (e.g. `profile_output.txt`,
  `profile_output.lprof`,
  and `stdout` print-outs)
  written by
  [`@line_profiler.profile`][line-profiler-profile] were suppressed.
  This is no longer the case,
  and [`@line_profiler.profile`][line-profiler-profile] now functions
  identically (up to overhead) between when this plugin is used or not.

### Boolean parsing

If a flag can be supplied without arguments,
doing so is equivalent to setting it to true.
If one does supply an argument,
it should be any of the following (case-insensitive):
```python
truey_strings = {'1', 'T', 'True', 'Y', 'yes'}
falsy_strings = {'0', 'F', 'False', 'N', 'no'}
```

### Dotted-path parsing

Dotted paths consist of a dotted *module* part,
and an optional sub-module-level dotted attribute-access (*object*)
part,
separated from the module part.
As examples,
a path like `foo.bar.baz` should correspond to the module
`importlib.import_module('foo.bar.baz')`,
while a path like `foo.bar::Baz.foobar` represents the object
`operator.attrgetter('Bar.foobar')(importlib.import_module('foo.bar'))`.

Multiple paths can be supplied both:
- Together and joined with commas, and/or
- By passing multiple copies of the corresponding dotted-path flag, like
  ```console
  $ pytest --always-autoprof=foo.bar::baz,foobar --always-autoprof=spam.eggs
  ```

#### <a name='notes-dotted-paths'></a> Notes

These semantics are a bit different and somewhat limited,
compared with those of
[`pytest-line-profiler`][pytest-line-profiler-source]'s
`--line-profile` flag
and [`kernprof`][kernprof-docs]'s `--prof-mod` flag resp.:
- File paths are not accepted.
- The explicit separation of the module and object parts with `'::'` is
  required,
  instead of using `'.'` as the separator
  (thus not distinguishing between the parts)
  and only later inferring which part is the module and which exists
  under it.

### Default hooks

Each of the command-line option added to `pytest` corresponds to a
[hook function][pytest-hooks],
through which users (through `conftest.py`) or other plugins can
provide alternative default values to the options
(see [`~.option_hooks`](src/pytest_autoprofile/option_hooks.py)):
- [`--always-autoprof`](#always-autoprof):
  `pytest_always_autoprof_default()`
- [`--recursive-autoprof`](#recursive-autoprof):
  `pytest_recursive_autoprof_default()`
- [`--postimport-autoprof`](#postimport-autoprof):
  `pytest_postimport_autoprof_default()`
- [`--autoprof-tests`](#autoprof-tests):
  `pytest_autoprof_tests_default()`
- [`--autoprof-mod`](#autoprof-mod):
  `pytest_autoprof_mod_default()`
- [`--autoprof-imports`](#autoprof-imports):
  `pytest_autoprof_imports_default()`
- [`--autoprof-doctests`](#autoprof-doctests):
  `pytest_autoprof_doctests_default()`
- [`--autoprof-rewrite-doctests`](#autoprof-rewrite-doctests):
  `pytest_autoprof_rewrite_doctests_default()`
- [`--autoprof-subprocs`](#autoprof-subprocs):
  `pytest_autoprof_subprocs_default()`
- [`--autoprof-outfile`](#autoprof-outfile):
  `pytest_autoprof_outfile_default()`
- [`--autoprof-view`](#autoprof-view):
  `pytest_autoprof_view_default()`
- [`--autoprof-global-profiler`](#autoprof-global-profiler):
  `pytest_autoprof_global_profiler_default()`

#### <a name='notes-hooks'></a> Notes

Unfortunately,
the defaults supplied by `conftest.py` and plugins are not (reliably)
available at the time that the command-line option parser is created
(see `pytest` issue [#13304][pytest-issue-13304]).
Therefore,
the default values of the options are left out of their `pytest --help`
blurbs.

Tests
-----

(Refer to the latest [Pipelines][repo-pipelines].)

Tests are currently done in the following environments.
Compatibility with other environments should be reasonable,
but is not guaranteed;
[write me an issue][repo-issues] if anything weird comes up.

### Stacks

| Component\Stack name | `py3.8` (*"oldest"*)                                                         | `py3.11` (*"middle"*)                                                         | `py3.13` (*"newest"*) |
| :-:                  | :-:                                                                          | :-:                                                                           | :-:                   |
| `python`             | `3.8.20` <sup>[[Note 1](#test-platforms-note-windows-python-versions)]</sup> | `3.11.10` <sup>[[Note 1](#test-platforms-note-windows-python-versions)]</sup> | `3.13.3`              |
| `pytest`             | `7.0.1`                                                                      | `8.0.2`                                                                       | `8.4.1`               |
| `pluggy`             | `1.2.0`                                                                      | `1.3.0`                                                                       | `1.5.0`               |
| `pytest-doctestplus` | `0.10.0`                                                                     | `1.0` <sup>[[Note 2](#test-platforms-note-mac-doctest)]</sup>                 | `1.4.0`               |
| `xdoctest`           | `0.12.0`                                                                     | `1.1.3` <sup>[[Note 2](#test-platforms-note-mac-doctest)]</sup>               | `1.2.0`               |

### Platforms

| OS      | CI? | Machine                                                     | Notes                                                                      |
| :-:     | :-: | :-:                                                         | :-:                                                                        |
| Linux   | yes | [`saas-linux-small-amd64`][gitlab-hosted-runner-linux]      |                                                                            |
| Windows | yes | [`saas-windows-medium-amd64`][gitlab-hosted-runner-windows] | [1](#test-platforms-note-windows-python-versions)                          |
| macOS   | no  | Yours truly's M3 Mac                                        | [2](#test-platforms-note-mac-doctest), [3](#test-platforms-note-mac-no-ci) |

### <a name='notes-tests'></a> Notes

1. <a name='test-platforms-note-windows-python-versions'></a>
   The Python versions are different on Windows due to the
   unavailability of the target versions on
   [NuGet][nuget-python-versions]:
   - "oldest": `3.8.20` → `3.8.10`
   - "middle": `3.11.10` → `3.11.9`
2. <a name='test-platforms-note-mac-doctest'></a>
   On other platforms,
   the test suite is always run *both* with and without
   [`pytest-doctestplus`][pytest-doctestplus-source] and
   [`xdoctest`][xdoctest-source] installed;
   on macOS,
   the test suite is always run *without* `pytest-doctestplus` and
   `xdoctest` on the "middle" stack and *with* it on the others.
3. <a name='test-platforms-note-mac-no-ci'></a>
   I'd love to run CI pipelines for that too,
   but [GitLab's macOS rate][gitlab-cost-factors] is too high...
   so just trust me bro.
   <sup>[[citation needed][wikipedia-citation-needed]]</sup>

Limitations
-----------

- There are no `.ini`-file-style equivalents for the command-line flags.
- Compatibility with other `pytest` plugins may be limited;
  see the [Notes](#notes-doctest-profiling) on
  [Doctest profiling](#doctest-profiling).
- Care must be taken when profiling code called in subprocesses,
  esp. via [`multiprocessing`][python-multiprocessing];
  see the [caveat](#multiproc-caveat) on
  [Subprocess profiling](#subprocess-profiling).

Acknowledgements
----------------

This plugin makes use of,
refers to,
or is inspired by
(in alphabetical order):

- [`coverage.py`][coverage-py-source]
- [`line_profiler`][line-profiler-source]
- [`pytest`][pytest-source]
- [`pytest-doctestplus`][pytest-doctestplus-source]
- [`pytest-line-profiler`][pytest-line-profiler-source]
- [`xdoctest`][xdoctest-source]

[repo-issues]: https://gitlab.com/TTsangSC/pytest-autoprofile/-/issues
[repo-pipelines]: https://gitlab.com/TTsangSC/pytest-autoprofile/-/pipelines
[repo-mascot]: assets/mascot.svg "Repo mascot"
[gitlab-cost-factors]: https://docs.gitlab.com/ci/pipelines/compute_minutes/#cost-factors-of-hosted-runners-for-gitlabcom
[gitlab-hosted-runner-linux]: https://docs.gitlab.com/ci/runners/hosted_runners/linux/
[gitlab-hosted-runner-windows]: https://docs.gitlab.com/ci/runners/hosted_runners/windows/
[nuget-python-versions]: https://www.nuget.org/packages/python#versions-body-tab
[pypi-line-profiler]: https://pypi.org/project/line-profiler/
[python-import-system]: https://docs.python.org/3/reference/import.html
[python-doctest]: https://docs.python.org/3/library/doctest.html
[python-doctest-DocTestRunner]: https://docs.python.org/3/library/doctest.html#doctest.DocTestRunner
[python-importlib-invalidate_caches]: https://docs.python.org/3/library/importlib.html#importlib.invalidate_caches
[python-multiprocessing]: https://docs.python.org/3/library/multiprocessing.html
[python-multiprocessing-Pool-close]: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.close
[python-multiprocessing-Pool-join]: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.join
[python-os-fork]: https://docs.python.org/3/library/os.html#os.fork
[python-shlex-split]: https://docs.python.org/3/library/shlex.html#shlex.split
[python-site]: https://docs.python.org/3/library/site.html
[python-sysconfig-get_path]: https://docs.python.org/3/library/sysconfig.html#sysconfig.get_path
[coverage-py-source]: https://github.com/nedbat/coveragepy
[coverage-multiproc-caveat]: https://coverage.readthedocs.io/en/latest/subprocess.html#using-multiprocessing
[kernprof-docs]: https://kernprof.readthedocs.io/en/latest/auto/kernprof.html
[pytest-doctest]: https://github.com/pytest-dev/pytest/blob/main/src/_pytest/doctest.py
[pytest-source]: https://github.com/pytest-dev/pytest
[pytest-assert]: https://docs.pytest.org/en/stable/how-to/assert.html#assert-details
[pytest-hooks]: https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html#using-hooks-in-pytest-addoption
[pytest-cache-dir]: https://docs.pytest.org/en/stable/reference/reference.html#confval-cache_dir
[pytest-root-dir]: https://docs.pytest.org/en/stable/reference/customize.html#finding-the-rootdir
[pytest-plugins]: https://docs.pytest.org/en/stable/reference/plugin_list.html
[pytest-issue-13304]: https://github.com/pytest-dev/pytest/issues/13304
[line-profiler-docs]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.html
[line-profiler-source]: https://github.com/pyutils/line_profiler
[line-profiler-autoprofile]: https://kernprof.readthedocs.io/en/latest/line_profiler.autoprofile.html
[line-profiler-profile]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.explicit_profiler.html#line_profiler.explicit_profiler.GlobalProfiler
[line-profiler-AstProfileTransformer]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.autoprofile.ast_profile_transformer.html#line_profiler.autoprofile.ast_profile_transformer.AstProfileTransformer
[line-profiler-AstTreeModuleProfiler]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.autoprofile.run_module.html#line_profiler.autoprofile.run_module.AstTreeModuleProfiler
[line-profiler-AstTreeProfiler-profile]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.autoprofile.ast_tree_profiler.html#line_profiler.autoprofile.ast_tree_profiler.AstTreeProfiler.profile
[line-profiler-LineProfiler-print_stats]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.line_profiler.html#line_profiler.line_profiler.LineProfiler.print_stats
[line-profiler-default-config]: https://github.com/pyutils/line_profiler/blob/main/line_profiler/rc/line_profiler.toml
[line-profiler-toml_config]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.toml_config.html
[line-profiler-utils]: https://github.com/pyutils/line_profiler/blob/main/line_profiler/autoprofile/line_profiler_utils.py
[line-profiler-output-getblock]: https://github.com/pyutils/line_profiler/blob/f03d8b14b71e6dec9dea00db0d9dbb4a530325fd/line_profiler/line_profiler.py#L201
[pytest-line-profiler-source]: https://github.com/mgaitan/pytest-line-profiler
[pytest-doctestplus-source]: https://github.com/scientific-python/pytest-doctestplus
[xdoctest-source]: https://github.com/Erotemic/xdoctest
[wikipedia-citation-needed]: https://en.wikipedia.org/wiki/Wikipedia:Citation_needed
