<!-- Badges -->

<a href='https://gitlab.com/TTsangSC/pytest-autoprofile/-/releases'
   alt='Badge: release version: "Latest Release" | <VERSION>'>
<img src='https://gitlab.com/TTsangSC/pytest-autoprofile/-/badges/release.svg'>
</a>
<a href='https://gitlab.com/TTsangSC/pytest-autoprofile/-/pipelines'
   alt='Badge: pipeline status: "pipeline" | <STATUS>'>
<img src='https://gitlab.com/TTsangSC/pytest-autoprofile/badges/master/pipeline.svg?ignore_skipped=true'>
</a>

<!-- Logo -->

![Repo mascot: a snake wearing a watch, looking at test results][gitlab-repo-mascot]

<!-- Blurb -->

Overview
--------

This plugin package brings the full power of
[`line_profiler.autoprofile`][line-profiler-autoprofile-docs] to your
[`pytest`][pytest-docs] test suite –
and then more.

Features
--------

- Automatic line profiling of normal tests and
  [doctests][gitlab-docs-doctest-profiling]
- [Import-time rewriting][gitlab-docs-rewriting] of arbitrary
  (test, codebase, external, standard-lib)
  Python modules
- Aggregation of in-process and
  [subprocess line-profiling][gitlab-docs-subprocess-profiling] results

<!-- Link -->

Full documentation
------------------

See the project repository: [GitLab:TTsangSC/pytest-autoprofile][gitlab-repo]

[gitlab-repo]: https://gitlab.com/TTsangSC/pytest-autoprofile
[gitlab-repo-mascot]: https://gitlab.com/TTsangSC/pytest-autoprofile/-/raw/master/assets/mascot.svg
[gitlab-docs-doctest-profiling]: https://gitlab.com/TTsangSC/pytest-autoprofile#doctest-profiling
[gitlab-docs-rewriting]: https://gitlab.com/TTsangSC/pytest-autoprofile#module-rewriting
[gitlab-docs-subprocess-profiling]: https://gitlab.com/TTsangSC/pytest-autoprofile#subprocess-profiling
[line-profiler-autoprofile-docs]: https://kernprof.readthedocs.io/en/latest/auto/line_profiler.autoprofile.html
[pytest-docs]: https://docs.pytest.org/en/stable/index.html
