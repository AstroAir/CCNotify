# CCNotify Testing Guide

This guide provides instructions for testing CCNotify on different platforms.

## Quick Platform Test

Run the platform detection test script to verify your system is compatible:

```bash
python test_platform.py
```

This will:
- Detect your operating system
- Check Python version
- Verify plyer library availability
- Check for VS Code installation
- Optionally send a test notification

## Platform-Specific Testing

### macOS Testing

#### Prerequisites
```bash
# Install Python dependencies
pip3 install plyer

# Install terminal-notifier (recommended)
brew install terminal-notifier
```

#### Test Steps
1. Run the platform test:
   ```bash
   python3 test_platform.py
   ```

2. Test with actual script:
   ```bash
   # Test without arguments (should print "ok")
   python3 ccnotify.py
   
   # Test with event data
   echo '{"session_id":"test-001","hook_event_name":"UserPromptSubmit","prompt":"test","cwd":"/tmp"}' | python3 ccnotify.py UserPromptSubmit
   ```

3. Check logs:
   ```bash
   tail -f ccnotify.log
   ```

#### Expected Results
- Platform detected as: `darwin`
- terminal-notifier should be found
- Notifications should appear in macOS Notification Center
- Click-to-open VS Code should work (if cwd provided)

### Linux Testing

#### Prerequisites

**Debian/Ubuntu:**
```bash
# Install Python dependencies
pip3 install plyer

# Install libnotify (recommended)
sudo apt install libnotify-bin
```

**Fedora/RHEL:**
```bash
pip3 install plyer
sudo dnf install libnotify
```

**Arch Linux:**
```bash
pip install plyer
sudo pacman -S libnotify
```

#### Test Steps
1. Run the platform test:
   ```bash
   python3 test_platform.py
   ```

2. Test with actual script:
   ```bash
   # Test without arguments (should print "ok")
   python3 ccnotify.py
   
   # Test with event data
   echo '{"session_id":"test-001","hook_event_name":"UserPromptSubmit","prompt":"test","cwd":"/tmp"}' | python3 ccnotify.py UserPromptSubmit
   ```

3. Check logs:
   ```bash
   tail -f ccnotify.log
   ```

#### Expected Results
- Platform detected as: `linux`
- notify-send should be found
- Notifications should appear in your desktop environment's notification area
- Check logs for any errors

### Windows Testing

#### Prerequisites
```powershell
# Install Python dependencies
pip install plyer
```

#### Test Steps
1. Run the platform test:
   ```powershell
   python test_platform.py
   ```

2. Test with actual script:
   ```powershell
   # Test without arguments (should print "ok")
   python ccnotify.py
   
   # Test with event data (PowerShell)
   '{"session_id":"test-001","hook_event_name":"UserPromptSubmit","prompt":"test","cwd":"C:\\temp"}' | python ccnotify.py UserPromptSubmit
   ```

3. Check logs:
   ```powershell
   Get-Content ccnotify.log -Tail 20
   ```

#### Expected Results
- Platform detected as: `windows`
- Plyer should be available
- Notifications should appear in Windows Action Center
- Check logs for any errors

## Testing Notification Methods

### Test All Notification Methods

You can test each notification method individually by modifying the test script or using Python interactively:

```python
from ccnotify import ClaudePromptTracker

tracker = ClaudePromptTracker()

# Test notification
tracker.send_notification(
    title="Test Notification",
    subtitle="Testing CCNotify",
    cwd="/path/to/project"  # Optional
)
```

### Verify Fallback Chain

To test the fallback chain, you can temporarily rename notification commands:

**macOS:**
```bash
# Temporarily disable terminal-notifier to test plyer fallback
sudo mv /usr/local/bin/terminal-notifier /usr/local/bin/terminal-notifier.bak
python3 test_platform.py
# Restore
sudo mv /usr/local/bin/terminal-notifier.bak /usr/local/bin/terminal-notifier
```

**Linux:**
```bash
# Temporarily disable notify-send to test plyer fallback
sudo mv /usr/bin/notify-send /usr/bin/notify-send.bak
python3 test_platform.py
# Restore
sudo mv /usr/bin/notify-send.bak /usr/bin/notify-send
```

## Integration Testing with Claude Code

### Setup Test Environment

1. Install CCNotify following the platform-specific instructions in README.md
2. Configure hooks in `~/.claude/settings.json` (or `%USERPROFILE%\.claude\settings.json` on Windows)
3. Verify hooks are active:
   ```bash
   claude -p --model haiku -d hooks --verbose "hi"
   ```

### Test Scenarios

#### Scenario 1: Basic Prompt Completion
```
# In Claude Code session
after 1 second, echo 'hello'
```
**Expected**: Notification appears when task completes

#### Scenario 2: Waiting for Input
```
# In Claude Code session
Create a file and ask me what content to put in it
```
**Expected**: Notification appears when Claude waits for input

#### Scenario 3: Multiple Tasks
```
# In Claude Code session
Run three commands with 1 second delay between each
```
**Expected**: Notification for each task completion with correct job numbers

### Verify Database

Check that events are being recorded:

**macOS/Linux:**
```bash
sqlite3 ~/.claude/ccnotify/ccnotify.db "SELECT * FROM prompt ORDER BY created_at DESC LIMIT 5;"
```

**Windows:**
```powershell
# Install sqlite3 or use DB Browser for SQLite
# Check: %USERPROFILE%\.claude\ccnotify\ccnotify.db
```

## Troubleshooting Tests

### No Notifications Appearing

1. Check platform detection:
   ```bash
   python test_platform.py
   ```

2. Check logs for errors:
   ```bash
   cat ccnotify.log
   ```

3. Verify notification system is working:
   - **macOS**: Check System Preferences → Notifications
   - **Linux**: Test with `notify-send "Test" "Message"`
   - **Windows**: Check Settings → System → Notifications

### Permission Errors

**macOS:**
- Grant terminal-notifier permissions in System Preferences → Security & Privacy

**Linux:**
- Ensure script is executable: `chmod +x ccnotify.py`
- Check D-Bus is running: `echo $DBUS_SESSION_BUS_ADDRESS`

**Windows:**
- Run PowerShell as Administrator if needed
- Check Windows Defender isn't blocking Python

### Import Errors

If you see `ModuleNotFoundError: No module named 'plyer'`:
```bash
pip install plyer
# or
pip3 install plyer
```

## Continuous Testing

For ongoing development, consider:

1. Running the test suite after any changes:
   ```bash
   python test_platform.py
   ```

2. Monitoring logs during Claude Code sessions:
   ```bash
   tail -f ~/.claude/ccnotify/ccnotify.log
   ```

3. Testing on multiple platforms if possible (VM, Docker, etc.)

## Reporting Issues

When reporting issues, please include:
- Output from `python test_platform.py`
- Relevant log entries from `ccnotify.log`
- Operating system and version
- Python version
- Whether plyer is installed
- Whether platform-specific notification tools are installed

