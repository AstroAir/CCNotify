# CCNotify Development Guide

This guide is for contributors and developers who want to work on CCNotify.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Using UV for Development](#using-uv-for-development)
- [Using Traditional Tools](#using-traditional-tools)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Making Changes](#making-changes)
- [Submitting Contributions](#submitting-contributions)

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Either UV (recommended) or pip/virtualenv

### Option 1: Setup with UV (Recommended)

UV is a fast, modern Python package and project manager that simplifies dependency management.

1. **Install UV:**

   **macOS/Linux:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Windows:**

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository:**

   ```bash
   git clone https://github.com/dazuiba/CCNotify.git
   cd CCNotify
   ```

3. **Install dependencies:**

   ```bash
   # UV automatically creates a virtual environment and installs dependencies
   uv sync
   ```

4. **Activate the virtual environment:**

   **macOS/Linux:**

   ```bash
   source .venv/bin/activate
   ```

   **Windows:**

   ```powershell
   .venv\Scripts\activate
   ```

### Option 2: Setup with Traditional Tools

1. **Clone the repository:**

   ```bash
   git clone https://github.com/dazuiba/CCNotify.git
   cd CCNotify
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**

   **macOS/Linux:**

   ```bash
   source .venv/bin/activate
   ```

   **Windows:**

   ```powershell
   .venv\Scripts\activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
CCNotify/
├── ccnotify.py           # Main script - handles Claude Code hooks
├── test_platform.py      # Platform detection and testing utility
├── tests/                # Test suite
│   ├── test_prompt_tracker.py
│   ├── test_data.py
│   └── run_tests.py
├── pyproject.toml        # Project metadata and dependencies (PEP 621)
├── requirements.txt      # Traditional dependency file (for compatibility)
├── README.md             # User documentation
├── TESTING.md            # Testing guide
├── DEVELOPMENT.md        # This file
└── LICENSE               # MIT License
```

## Using UV for Development

### Managing Dependencies

**Add a new dependency:**

```bash
uv add package-name
```

**Add a development dependency:**

```bash
uv add --dev package-name
```

**Remove a dependency:**

```bash
uv remove package-name
```

**Update dependencies:**

```bash
uv lock --upgrade
```

**Sync environment with lockfile:**

```bash
uv sync
```

### Running the Script

**Run with UV:**

```bash
uv run python ccnotify.py
```

**Run tests:**

```bash
uv run python test_platform.py
uv run python tests/run_tests.py
```

## Using Traditional Tools

### Managing Dependencies

When using pip, manually edit `requirements.txt` and then:

```bash
pip install -r requirements.txt
```

### Running the Script

```bash
python ccnotify.py
python test_platform.py
python tests/run_tests.py
```

## Running Tests

### Platform Detection Test

Test that CCNotify works on your platform:

```bash
python test_platform.py
```

This will:

- Detect your operating system
- Check Python version
- Verify plyer library availability
- Check for VS Code installation
- Optionally send a test notification

### Unit Tests

Run the full test suite:

```bash
cd tests
python -m unittest test_prompt_tracker.py -v
```

### Manual Integration Tests

Run manual tests with different scenarios:

```bash
cd tests
python run_tests.py              # Interactive mode
python run_tests.py all          # Run all scenarios
python run_tests.py scenario_1   # Run specific scenario
python run_tests.py verify       # Verify database
```

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Code Style

### Python Style Guidelines

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Use type hints where appropriate (Python 3.7+)

### Example

```python
def calculate_duration(self, start_time: str, end_time: str) -> str:
    """
    Calculate human-readable duration between two timestamps.
    
    Args:
        start_time: ISO format timestamp string
        end_time: ISO format timestamp string
        
    Returns:
        Human-readable duration string (e.g., "5m30s", "2h15m")
    """
    # Implementation...
```

## Making Changes

### Before Making Changes

1. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make sure tests pass:

   ```bash
   python test_platform.py
   python -m unittest tests/test_prompt_tracker.py
   ```

### After Making Changes

1. Test your changes thoroughly:
   - Run platform detection test
   - Run unit tests
   - Test manually with Claude Code if possible

2. Update documentation if needed:
   - Update README.md for user-facing changes
   - Update TESTING.md for test-related changes
   - Update this file for development workflow changes

3. Commit your changes:

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

## Submitting Contributions

1. **Push your branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request:**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes clearly
   - Reference any related issues

3. **Code Review:**
   - Address any feedback from reviewers
   - Make requested changes
   - Push updates to your branch

## Dependency Management Notes

### pyproject.toml vs requirements.txt

- **pyproject.toml**: Source of truth for project metadata and dependencies (PEP 621 standard)
- **requirements.txt**: Maintained for backward compatibility with existing documentation

When adding dependencies:

- If using UV: Use `uv add package-name` (automatically updates pyproject.toml)
- If using pip: Update both `requirements.txt` AND `pyproject.toml` manually

### Keeping Dependencies in Sync

To ensure both files stay in sync:

1. **Primary method (UV):**

   ```bash
   uv add package-name
   # Then manually update requirements.txt to match
   ```

2. **Manual method:**
   - Edit `pyproject.toml` dependencies array
   - Edit `requirements.txt` to match
   - Run `uv sync` or `pip install -r requirements.txt`

## Questions or Issues?

- Check existing [GitHub Issues](https://github.com/dazuiba/CCNotify/issues)
- Create a new issue if you find a bug or have a feature request
- Review [README.md](README.md) for user documentation
- Review [TESTING.md](TESTING.md) for testing procedures

## License

CCNotify is released under the MIT License. See [LICENSE](LICENSE) for details.
