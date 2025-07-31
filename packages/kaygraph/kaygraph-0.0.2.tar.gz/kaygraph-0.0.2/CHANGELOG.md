# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-07-31

### Changed
- **BREAKING**: Updated minimum Python version requirement from 3.8 to 3.11
- Modernized type hints to use Python 3.10+ syntax:
  - `Dict[str, Any]` → `dict[str, Any]`
  - `List[Any]` → `list[Any]`
  - `Optional[str]` → `str | None`
- Updated development tooling to target Python 3.11

### Added
- Added support for Python 3.12 and 3.13 in classifiers

### Removed
- Removed support for Python versions 3.8, 3.9, and 3.10

## [0.0.1] - 2025-07-29

### Added
- Initial release of KayGraph
- Core abstractions: BaseNode, Node, Graph
- Async support with AsyncNode and AsyncGraph
- Batch processing with BatchNode and ParallelBatchNode
- Built-in resilience with retries and fallbacks
- Thread-safe execution with node copying
- Zero dependencies - pure Python implementation