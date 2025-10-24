# Contributing to CCNotify

Thank you for your interest in contributing to CCNotify! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Detailed steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, CCNotify version)
- Relevant log output from `ccnotify.log`

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

### Suggesting Features

Feature suggestions are welcome! Please:

- Check existing feature requests first
- Provide a clear use case
- Explain how it aligns with CCNotify's purpose
- Consider implementation complexity

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** on all supported Python versions
6. **Submit a pull request** using the PR template

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/CCNotify.git
cd CCNotify

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e .
pip install pytest pytest-cov ruff mypy

# Run tests to verify setup
pytest tests/
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Code Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check code style
ruff check src/ tests/

# Auto-format code
ruff format src/ tests/
```

### Type Hints

- Add type hints to function signatures
- Use `mypy` for type checking:

```bash
mypy src/ccnotify/ --ignore-missing-imports
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=ccnotify --cov-report=term

# Run specific test file
pytest tests/test_prompt_tracker.py -v
```

### Writing Tests

- Write tests for all new functionality
- Aim for high code coverage
- Use descriptive test names
- Test edge cases and error conditions

## Project Structure

```
CCNotify/
├── src/ccnotify/          # Source code
│   ├── __init__.py
│   ├── ccnotify.py        # Main module
│   ├── i18n.py            # Internationalization
│   └── install_helper.py  # Installation utilities
├── tests/                 # Test files
├── docs/                  # Documentation
├── scripts/               # Installation scripts
├── .github/               # GitHub workflows and templates
├── pyproject.toml         # Package configuration
├── requirements.txt       # Dependencies
└── README.md              # Main documentation
```

## Internationalization (i18n)

When adding user-facing text:

1. Add translation keys to `src/ccnotify/i18n.py`
2. Provide translations for both English (`en`) and Chinese Simplified (`zh-CN`)
3. Use the `t()` function for all user-facing strings

Example:

```python
from .i18n import t

# Add to TRANSLATIONS dict in i18n.py
'new_feature': {
    'message': 'New feature message'  # English
}

# In Chinese section
'new_feature': {
    'message': '新功能消息'  # Chinese
}

# Use in code
message = t('new_feature.message')
```

## Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for detailed documentation
- Add docstrings to all public functions and classes
- Include code examples where helpful

## Commit Messages

Write clear, concise commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Examples:

```
Add retry logic for failed notifications

Fix notification timeout on Windows (#123)

Update README with new installation instructions
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `src/ccnotify/__init__.py`
2. Update `CHANGELOG.md` with release notes
3. Create a git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release
6. CI/CD will automatically publish to PyPI

## Getting Help

- Check the [documentation](README.md)
- Search [existing issues](https://github.com/dazuiba/CCNotify/issues)
- Ask questions in issue discussions
- Review the [troubleshooting guide](README.md#troubleshooting)

## License

By contributing to CCNotify, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project's README and release notes.

Thank you for contributing to CCNotify! 🎉
