# Changelog

All notable changes to CCNotify will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project structure reorganization following Python best practices
- GitHub Actions CI/CD workflows (testing, linting, publishing)
- Issue templates for bug reports and feature requests
- Pull request template
- Contributing guidelines (CONTRIBUTING.md)
- Comprehensive .gitignore file
- Type checking with mypy in CI
- Multi-language support (English and Chinese Simplified)
- Rich library integration for beautiful terminal output
- Retry logic with exponential backoff for failed notifications
- Enhanced edge case handling and input validation

### Changed

- Moved source code to `src/ccnotify/` package structure
- Moved tests to `tests/` directory
- Moved documentation to `docs/` directory
- Moved installation scripts to `scripts/` directory
- Updated package configuration in pyproject.toml
- Improved notification system reliability

### Fixed

- Consistent timeout handling across all notification methods
- Better error messages with translations

## [0.1.0] - 2024-XX-XX

### Added

- Initial release of CCNotify
- Desktop notifications for Claude Code
- Support for macOS, Linux, and Windows
- Session tracking with SQLite database
- Task duration calculation
- Click-to-open in VS Code (macOS only)
- Automated installation scripts
- Cross-platform notification support (plyer, terminal-notifier, notify-send, PowerShell)
- Comprehensive logging system
- Hook integration with Claude Code

### Features

- UserPromptSubmit hook: Records session start
- Stop hook: Sends completion notification with duration
- Notification hook: Alerts for input requests and permissions

### Documentation

- Comprehensive README with installation instructions
- Platform-specific installation guides
- Troubleshooting section
- Manual and automated installation options

[Unreleased]: https://github.com/dazuiba/CCNotify/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dazuiba/CCNotify/releases/tag/v0.1.0
