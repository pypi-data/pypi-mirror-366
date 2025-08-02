# Changelog

All notable changes to this project will be documented in this file.


## [Unreleased]

### Added
-

### Changed
-

### Deprecated
-

### Removed
-
### Fixed
-

### Security
-

## [1.0.3]
### Fixed
- Views of `statkit.types.Estimate` gracefully handle `numpy.nan` values.

## [1.0.1-2]
### Changed
- Made package sci-kit learn 1.7 compatible.
- Improved str formatting of `statkit.types.Estimate`.

## [1.0.0]

### Added
- `statkit.dataset.split_multinomial_dataset`: renamed from `statkit.model_selection.holdout_split`.
- `statkit.dataset.balanced_downsample`: renamed from `statkit.dataset.stratified_downsample`.

### Changed
- All `statkit.non_parametric` functions: `**kwargs` parameter now replaces `metric_kwargs`:


### Removed
- `statkit.model_selection.holdout_split`: see Added.
