# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.3] - 2025-08-01

### Fixed
- Complete type annotations for all functions and methods
- Fixed mypy type checking errors
- Corrected CLI parameter type annotations for optional values
- Fixed documentation warnings and duplicate entries
- Updated documentation references to match actual code
- Removed deprecated theme options from Sphinx configuration
- Fixed CLI command references in documentation (list-categories vs list-shelves)
- Corrected API method names in documentation examples

### Improved
- Enhanced code quality with comprehensive type hints
- Better documentation structure and consistency
- Cleaner documentation build with fewer warnings
- Updated version consistency across all configuration files

### Technical
- Fixed Path type assignment issues in report generation
- Added proper Optional type hints for CLI parameters
- Updated autosummary configuration to reduce duplicate warnings
- Enhanced developer experience with better type support

## [1.0.2] - 2025-07-19

### Added
- Updated documentation for project rename to discogs-record-shelf
- Improved project metadata and descriptions

## [1.0.1] - 2025-07-19

### Changed
- Renamed project to discogs-record-shelf for better clarity
- Updated all references and documentation

## [1.0.0] - 2025-07-19

### Added
- Initial stable release of record-shelf
- Support for generating collection reports from Discogs API
- Export formats: Excel, CSV, HTML
- Command-line interface with configurable options
- Comprehensive documentation with Sphinx
- Full test coverage
- CI/CD pipeline with GitHub Actions
- PyPI package publishing
- Read the Docs integration

### Features
- Fetch collection data from Discogs API
- Generate detailed reports with multiple data fields
- Rate limiting and error handling
- Configurable logging
- Cross-platform support (Windows, macOS, Linux)
- Python 3.8+ compatibility

