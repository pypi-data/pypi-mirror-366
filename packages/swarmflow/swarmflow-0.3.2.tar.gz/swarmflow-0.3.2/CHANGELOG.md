# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2025-01-02

### Fixed
- **Task initialization bug**: Fixed crash when accessing `task.current_retry` for skipped tasks or tasks with no retries
  - Added safe fallback: `getattr(task, "current_retry", 0)` in `_log()` method
  - Added `self.current_retry = 0` initialization in `Task.__init__()` constructor
  - Ensures all tasks have consistent retry tracking regardless of execution path

## [0.3.1] - 2025-01-02

### Fixed
- **Retry count tracking**: Fixed retry count logic to accurately report attempts taken vs retries used
  - For successful tasks: reports attempts taken to succeed
  - For failed tasks: reports total retries used
  - Previously always showed 0 due to logging only after retry loop completion

## [0.3.0] - 2025-01-02

### Added
- **Run status persistence**: Added `_finalize_run_status()` method to compute and persist overall DAG run status
- **Retry count tracking**: Each task trace now includes `retry_count` for better debugging and monitoring
- **Enhanced run-level status**: Automatic computation of run status:
  - `"completed"` if all tasks are successful
  - `"failed"` if any task fails
  - `"partial"` if some succeed and some fail/skipped
- **Run status API integration**: PATCH requests to `/api/runs/update-status` to persist run-level status
- **Resumption preparation**: Foundation for future workflow resumption capabilities

### Changed
- **Enhanced task execution**: Added `current_retry` tracking during retry loops
- **Improved trace payload**: Trace payloads now include retry count for each task execution

## [0.2.0] - 2025-01-02

### Added
- **API key authentication**: Added support for API key authentication in trace reporting
- **Environment variable support**: Can use `SWARMFLOW_API_KEY` environment variable as fallback
- **Secure trace reporting**: All POST requests to backend now include `x-api-key` header when API key is provided

## [0.1.9] - 2025-01-02

### Added
- **DAG run tracking**: Added unique `run_id` that's consistent across all tasks in a single DAG run
- **Enhanced trace structure**: Trace payloads now include `run_id` for better grouping and analytics

## [0.1.8] - 2025-01-02

### Fixed
- **Metadata serialization**: Added `_clean_metadata()` method to remove None values from metadata before JSON serialization
- **Trace payload**: Fixed metadata preservation in trace payloads sent to backend

## [0.1.7] - 2025-01-02

### Fixed
- **JSON serialization**: Fixed trace payload serialization to handle Groq ChatCompletion objects properly
- **Output extraction**: Added proper extraction of message content from LLM response objects

## [0.1.6] - 2025-01-02

### Fixed
- **Groq attribute access**: Fixed usage object attribute access to use `getattr()` instead of dict-style access
- **Model name normalization**: Added proper model name normalization to handle provider prefixes (e.g., "meta-llama/llama-3-70b" → "llama-3-70b")

## [0.1.5] - 2025-01-02

### Changed
- **Groq-focused metadata extraction**: Replaced OpenAI/Anthropic support with comprehensive Groq metadata extraction including timing metrics and precise cost calculation
- **Enhanced cost calculation**: Added support for all Groq models with accurate pricing per million tokens

## [0.1.4] - 2025-01-02

### Added
- **Auto-extracted Groq metadata**: Automatically detects and extracts model, provider, token usage, precise cost calculation, and timing metrics from Groq responses
- **Enhanced observability**: Groq metadata is automatically added to task traces and monitoring dashboard

## [0.1.3] - 2025-01-02

### Changed
- **Cleaner imports**: Users can now import directly with `from swarmflow import SwarmFlow, swarm_task`

## [0.1.2] - 2025-01-02

### Changed
- **Simplified backend configuration**: Hardcoded to localhost:8000 for development

## [0.1.1] - 2025-01-02

### Added
- **Multiple dependency support**: `depends_on()` now accepts multiple dependencies in a single call
- **Backend integration**: Traces are sent to SwarmFlow backend service at localhost:8000

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

### Features
- Multi-agent workflow orchestration
- Automatic task dependency resolution
- Performance monitoring and tracing
- Production-ready error handling
- Scalable architecture for complex workflows 