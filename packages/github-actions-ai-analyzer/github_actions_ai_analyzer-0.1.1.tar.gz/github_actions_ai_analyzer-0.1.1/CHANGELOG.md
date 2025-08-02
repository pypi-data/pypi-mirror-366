# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-08-02

### Fixed
- Fixed LogLevel and PatternCategory enum handling in CLI and analyzer
- Fixed log processor to properly handle GitHub Actions timestamp format
- Fixed pattern matcher language filtering to work with logs without language metadata
- Improved error pattern matching for dependency and network errors

### Improved
- Enhanced log message cleaning to remove timestamps before pattern matching
- Added more comprehensive error patterns for dependency issues
- Better test coverage and manual testing validation

### Technical
- Fixed AttributeError: 'str' object has no attribute 'value' issues
- Improved pattern matching accuracy for real GitHub Actions logs
- Enhanced CLI error handling and user experience

## [0.1.0] - 2024-08-02

### Added
- Initial implementation of GitHub Actions AI Analyzer
- Core analyzer components (LogProcessor, PatternMatcher, ContextCollector, AIPromptOptimizer)
- Type definitions for log entries, patterns, and analysis results
- CLI interface with analyze, validate, and watch commands
- Support for Python, JavaScript, and Java error patterns
- AI prompt optimization for error analysis and solution generation
- Basic test structure and examples

### Features
- Log processing and noise removal
- Error pattern matching with confidence scoring
- Context collection from repository, workflow, and environment
- Structured error analysis and solution proposals
- Multiple output formats (text, JSON, YAML)
- Rich CLI interface with progress indicators
- Pattern matching for common GitHub Actions errors (dependency, permission, environment, network, and syntax errors)

### Technical
- Comprehensive test coverage (70% overall)
- Pydantic-based type validation
- Modular architecture for easy extension
- MIT license 