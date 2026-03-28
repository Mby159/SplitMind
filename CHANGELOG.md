# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-28

### Added
- **Core Privacy Protection**: Automatic detection and redaction of sensitive information (phone numbers, emails, ID cards, bank cards, etc.)
- **Task Splitting Engine**: Intelligent task decomposition with multiple strategies (auto, single, section, semantic, parallel)
- **Multi-Provider Support**: Integration with OpenAI, Anthropic Claude, Kimi, and local models (Ollama)
- **Result Aggregation**: Multiple aggregation strategies (sequential, parallel_merge, hierarchical, voting, best_of)
- **Execution Modes**: Three modes to balance privacy and capability
  - `local_only`: All processing done locally (maximum privacy)
  - `hybrid`: Privacy protection local, execution can use online providers (balanced)
  - `online`: Can use online services for splitting and execution (maximum capability)
- **CLI Tool**: Complete command-line interface with configuration management
- **Web Interface**: FastAPI-based web UI for interactive use
- **Configuration Management**: Persistent user preferences and settings
- **Docker Support**: Dockerfile and docker-compose.yml for easy deployment
- **Comprehensive Testing**: 20+ unit tests covering core functionality
- **Documentation**: README, API docs, and usage examples

### Security
- All sensitive information processing happens locally
- No sensitive data sent to external AI providers
- Configurable privacy protection levels

[0.1.0]: https://github.com/yourusername/splitmind/releases/tag/v0.1.0
