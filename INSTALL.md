# CCNotify Installation Guide

This document provides detailed installation instructions for CCNotify.

## Quick Start

### Automated Installation (Recommended)

The easiest way to install CCNotify is using our automated installation scripts.

#### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (to clone the repository)

#### Installation Steps

**macOS/Linux:**

```bash
# 1. Clone the repository
git clone https://github.com/dazuiba/CCNotify.git
cd CCNotify

# 2. Make the installation script executable
chmod +x install.sh

# 3. Run the installer
./install.sh
```

**Windows:**

```powershell
# 1. Clone the repository
git clone https://github.com/dazuiba/CCNotify.git
cd CCNotify

# 2. Run the installer
.\install.ps1
```

#### What the Installer Does

The automated installer will:

1. ✓ Verify Python 3.7+ is installed
2. ✓ Check that pip is available
3. ✓ Install required Python dependencies (plyer)
4. ✓ Create the installation directory (`~/.claude/ccnotify`)
5. ✓ Copy necessary files to the installation directory
6. ✓ Configure Claude Code hooks automatically in `settings.json`
7. ✓ Offer to install optional platform-specific notification tools
8. ✓ Validate the installation

#### Installation Options

**Silent Mode** (non-interactive):
- Unix: `./install.sh --silent`
- Windows: `.\install.ps1 -Silent`

**Dry Run** (preview without making changes):
- Unix: `./install.sh --dry-run`
- Windows: `.\install.ps1 -DryRun`

**Help**:
- Unix: `./install.sh --help`
- Windows: `.\install.ps1 -Help`

## Platform-Specific Notes

### macOS

The installer will offer to install `terminal-notifier` via Homebrew for enhanced notifications:

```bash
brew install terminal-notifier
```

This is optional but recommended for the best notification experience on macOS.

### Linux

The installer will offer to install `libnotify` for native Linux notifications:

**Debian/Ubuntu:**
```bash
sudo apt install libnotify-bin
```

**Fedora/RHEL:**
```bash
sudo dnf install libnotify
```

**Arch Linux:**
```bash
sudo pacman -S libnotify
```

### Windows

Windows uses the `plyer` library exclusively for notifications. No additional tools are required.

## Verification

After installation, test CCNotify by running:

```bash
claude 'after 1 second, echo hello'
```

You should see a desktop notification appear.

## Troubleshooting

### Python Not Found

**Error:** `Python is not installed` or `command not found: python`

**Solution:**
- Ensure Python 3.7+ is installed
- Verify with: `python --version` or `python3 --version`
- Add Python to your PATH if necessary

**Installation:**
- macOS: `brew install python3`
- Linux: `sudo apt install python3` (Debian/Ubuntu)
- Windows: Download from [python.org](https://www.python.org/downloads/)

### pip Not Available

**Error:** `pip is not available`

**Solution:**
- Try: `python -m ensurepip --upgrade`
- Linux: `sudo apt install python3-pip`
- Verify with: `python -m pip --version`

### Permission Denied (Unix)

**Error:** `Permission denied` when running install.sh

**Solution:**
```bash
chmod +x install.sh
./install.sh
```

### Settings.json Invalid JSON

**Error:** `settings.json contains invalid JSON`

**Solution:**
- The installer will refuse to proceed if settings.json has syntax errors
- Fix the JSON syntax errors before running the installer
- Use a JSON validator or editor with JSON support
- Common issues: missing commas, trailing commas, unquoted keys

### Installation Directory Already Exists

The installer will detect existing installations and handle them appropriately. If you want to reinstall:

1. Run the uninstaller first: `./uninstall.sh` or `.\uninstall.ps1`
2. Then run the installer again

### Hooks Not Working

After installation, if hooks don't work:

1. Verify hooks are in settings.json:
   - Unix: `cat ~/.claude/settings.json`
   - Windows: `type %USERPROFILE%\.claude\settings.json`

2. Check for JSON syntax errors in settings.json

3. Restart Claude Code or your terminal

4. Test with verbose mode:
   ```bash
   claude -p --model haiku -d hooks --verbose "hi"
   ```

   You should see:
   ```
   [DEBUG] Found 1 hook commands to execute
   [DEBUG] Executing hook command: ~/.claude/ccnotify/ccnotify.py UserPromptSubmit
   ```

## Manual Installation

If you prefer to install manually, see the [Manual Installation](README.md#manual-installation) section in the README.

## Uninstallation

To uninstall CCNotify:

**macOS/Linux:**
```bash
cd CCNotify
./uninstall.sh
```

**Windows:**
```powershell
cd CCNotify
.\uninstall.ps1
```

**Options:**
- `--keep-data` / `-KeepData`: Keep log files and database
- `--silent` / `-Silent`: Non-interactive mode
- `--dry-run` / `-DryRun`: Preview without making changes

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](README.md#troubleshooting) section in the README
2. Review the installation logs
3. Run the installer with `--dry-run` to see what would be done
4. Open an issue on [GitHub](https://github.com/dazuiba/CCNotify/issues)

## Advanced Options

### Custom Installation Directory

The default installation directory is `~/.claude/ccnotify`. If you need to use a different location, you'll need to:

1. Manually copy the files to your desired location
2. Update the hook commands in `settings.json` to point to the new location
3. Ensure the script is executable (Unix)

### Using UV Package Manager

If you prefer using UV for dependency management, see the [Alternative Installation with UV](README.md#alternative-installation-with-uv) section in the README.

## Next Steps

After successful installation:

1. Restart Claude Code or reload your terminal
2. Test the notification system
3. Review the [How It Works](README.md#how-it-works) section to understand CCNotify's behavior
4. Check the logs at `~/.claude/ccnotify/ccnotify.log` if you encounter issues

Enjoy using CCNotify!

