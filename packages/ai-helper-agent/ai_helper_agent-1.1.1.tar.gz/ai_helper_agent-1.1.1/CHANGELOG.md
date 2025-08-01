# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial development setup

## [1.1.0] - 2025-01-31

### Added
- **Internet Access Feature**: New `ai-helper-internet-single` CLI with automatic web search
- Smart query analysis that determines when internet search is needed
- Multiple search providers support (DuckDuckGo, Google)
- Permission control system with multiple levels (smart, always, ask, never)
- Real-time web search integration with Groq models
- Enhanced system prompts for internet-aware AI assistance
- New dependencies: requests, beautifulsoup4, duckduckgo-search, googlesearch-python

### Enhanced
- Updated README with internet access examples and documentation
- Improved package description to include internet access capabilities
- Enhanced CLI help system with internet commands

### Changed
- Version bumped from 1.0.3 to 1.1.0 for new major feature
- Package description updated to reflect internet access capabilities

## [1.0.0] - 2025-01-29

### Added
- Initial release of AI Helper Agent
- Interactive AI assistant for code analysis
- Code validation and execution utilities
- File operation capabilities
- Command-line interface
- Comprehensive test suite
- Documentation and examples

### Features
- **InteractiveAgent**: Main class for AI interactions
- **Code Analysis**: Syntax validation and error detection
- **Bug Fixing**: Intelligent code suggestions and fixes
- **File Operations**: Read, write, and modify files
- **CLI Tool**: Command-line interface for easy usage
- **Extensible**: Plugin-ready architecture

### Dependencies
- langchain-groq >= 0.1.0
- langchain >= 0.1.0
- Python >= 3.8

### Documentation
- Complete README with usage examples
- API documentation
- Contributing guidelines
- License (MIT)

[Unreleased]: https://github.com/yourusername/ai-helper-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/ai-helper-agent/releases/tag/v1.0.0
