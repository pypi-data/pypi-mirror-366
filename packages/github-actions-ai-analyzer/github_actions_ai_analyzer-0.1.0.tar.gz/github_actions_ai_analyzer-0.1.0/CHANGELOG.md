# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic log analysis functionality
- Pattern matching for common GitHub Actions errors
- CLI tool for log file analysis
- Support for dependency, permission, environment, network, and syntax errors 