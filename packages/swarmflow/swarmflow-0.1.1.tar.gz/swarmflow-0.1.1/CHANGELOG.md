# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-01-02

### Added
- **Multiple dependency support**: `depends_on()` now accepts multiple dependencies in a single call

## [0.1.0] - 2024-12-19

### Added
- Initial release of SwarmFlow
- Agent orchestration framework with dependency management
- Built-in retry logic for resilient agent execution
- OpenTelemetry integration for observability
- Real-time monitoring capabilities
- Cycle detection for dependency graphs
- Comprehensive error handling and logging
- `@swarm_task` decorator for easy agent function definition
- `SwarmFlow` class for workflow orchestration
- **Multiple dependency support**: `depends_on()` now accepts multiple dependencies in a single call

### Features
- Multi-agent workflow orchestration
- Automatic task dependency resolution
- Performance monitoring and tracing
- Production-ready error handling
- Scalable architecture for complex workflows 