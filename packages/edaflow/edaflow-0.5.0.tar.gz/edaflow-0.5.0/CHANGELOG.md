# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be documented here

### Changed
- Future changes will be documented here

### Deprecated
- Future deprecations will be documented here

### Removed
- Future removals will be documented here

## [0.5.0] - 2025-08-04

### Added
- `handle_outliers_median()` function for automated outlier detection and replacement
- Multiple outlier detection methods: IQR, Z-score, and Modified Z-score
- Complete outlier analysis workflow integration with boxplot visualization
- Median-based outlier replacement for robust statistical handling
- Flexible column selection with automatic numerical column detection
- Detailed reporting showing exactly which outliers were replaced and statistical bounds
- Safe operation mode (inplace=False by default) to preserve original data
- Statistical method comparison with customizable IQR multipliers
- Complete 9-function EDA package with comprehensive outlier management

### Fixed
- Dtype compatibility improvements to eliminate pandas FutureWarnings
- Enhanced error handling and validation for numerical column processing

## [0.4.2] - 2025-08-04

### Fixed
- Updated README.md changelog to properly reflect v0.4.1 boxplot features on PyPI page
- Corrected version history display for proper PyPI documentation

## [0.4.1] - 2025-08-04

### Added
- `visualize_numerical_boxplots()` function for comprehensive outlier detection and statistical analysis
- Advanced boxplot visualization with customizable layouts (rows/cols), orientations, and color palettes
- Automatic numerical column detection for boxplot analysis
- Detailed statistical summaries including skewness analysis and interpretation
- IQR-based outlier detection with threshold reporting
- Comprehensive outlier identification with actual outlier values displayed
- Support for horizontal and vertical boxplot orientations
- Seaborn integration for enhanced styling and color palettes

### Fixed
- `impute_categorical_mode()` function now properly returns DataFrame instead of None
- Corrected inplace parameter handling for categorical imputation function

### Fixed
- Future fixes will be documented here

### Security
- Future security updates will be documented here

## [0.1.0] - 2025-08-04

### Added
- Initial package structure
- Basic `hello()` function in `edaflow.__init__`
- Setup configuration with `setup.py` and `pyproject.toml`
- Core dependencies: pandas, numpy, matplotlib, seaborn, scipy, missingno
- Comprehensive README with installation and usage instructions
- MIT License
- Development dependencies and tooling configuration
- Git ignore file
- Basic project documentation structure

### Infrastructure
- Package structure with `edaflow/` module directory
- Development tooling setup (black, flake8, isort, pytest, mypy)
- Continuous integration ready configuration
- PyPI publishing ready setup

[Unreleased]: https://github.com/yourusername/edaflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/edaflow/releases/tag/v0.1.0
