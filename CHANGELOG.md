## Unreleased

* Dropped support for Python 2.7.

## v1.0.1 (2017-05-01)

* Fixed oversight where `interpret()` would exit with the interpreted code rather than returning it,
  which wasn't particularly friendly for library use.
* Fixed typo in `interpret()` that prevented convenience type conversion for substitutions.
* Added docstrings for the public functions.

## v1.0.0 (2017-04-30)

* Initial release.
