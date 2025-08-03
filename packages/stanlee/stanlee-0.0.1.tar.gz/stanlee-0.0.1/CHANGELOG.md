# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-08-02

### Added
- Initial release of Stanlee AI agent framework
- Core Agent class with tool execution capabilities
- Tool base class for creating custom tools
- SendMessage tool for basic agent communication
- History tracking for conversations
- Support for streaming and non-streaming responses
- Integration with litellm for multiple LLM providers
- Examples directory with simple agent demonstration
- Comprehensive error handling with custom exceptions
- Type hints throughout the codebase
- Support for Python 3.11+

### Dependencies
- litellm>=1.74.15 for LLM provider integration
- pydantic>=2.11.7 for data validation
- debugpy>=1.8.15 for debugging capabilities

[0.0.1]: https://github.com/amaarora/stanlee/releases/tag/v0.0.1