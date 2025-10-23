#!/usr/bin/env python3
"""
Claude Code Notify
https://github.com/dazuiba/CCNotify
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
import platform
import shutil
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Try to import plyer for cross-platform notifications
try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


def get_platform():
    """
    Detect the current operating system platform.

    Returns:
        str: 'windows', 'linux', 'darwin' (macOS), or 'unknown'
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return 'unknown'


def get_vscode_command():
    """
    Get the VS Code command for the current platform.

    Returns:
        str: Path to VS Code command, or None if not found
    """
    current_platform = get_platform()

    # Try to find 'code' command in PATH
    code_path = shutil.which('code')
    if code_path:
        return code_path

    # Platform-specific fallback paths
    if current_platform == 'darwin':
        # macOS common paths
        possible_paths = [
            '/usr/local/bin/code',
            '/opt/homebrew/bin/code',
        ]
    elif current_platform == 'windows':
        # Windows common paths
        possible_paths = [
            'code.cmd',
            'code.exe',
        ]
    elif current_platform == 'linux':
        # Linux common paths
        possible_paths = [
            '/usr/bin/code',
            '/usr/local/bin/code',
        ]
    else:
        possible_paths = []

    # Check fallback paths
    for path in possible_paths:
        if shutil.which(path) or os.path.exists(path):
            return path

    return None


class ClaudePromptTracker:
    def __init__(self):
        """Initialize the prompt tracker with database setup"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, "ccnotify.db")
        self.setup_logging()

        # Log platform information
        current_platform = get_platform()
        logging.info(f"CCNotify initialized on platform: {current_platform}")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"Plyer available: {PLYER_AVAILABLE}")

        vscode_cmd = get_vscode_command()
        if vscode_cmd:
            logging.info(f"VS Code command found: {vscode_cmd}")
        else:
            logging.warning("VS Code command not found in PATH")

        self.init_database()

    def setup_logging(self):
        """Setup logging to file with daily rotation"""

        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, "ccnotify.log")

        # Create a timed rotating file handler
        handler = TimedRotatingFileHandler(
            log_path,
            when="midnight",  # Rotate at midnight
            interval=1,  # Every 1 day
            backupCount=1,  # Keep 1 days of logs
            encoding="utf-8",
        )

        # Set the log format
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Configure the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def init_database(self):
        """Create tables and triggers if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Create main table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    prompt TEXT,
                    cwd TEXT,
                    seq INTEGER,
                    stoped_at DATETIME,
                    lastWaitUserAt DATETIME
                )
            """)

            # Create trigger for auto-incrementing seq
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS auto_increment_seq
                AFTER INSERT ON prompt
                FOR EACH ROW
                BEGIN
                    UPDATE prompt
                    SET seq = (
                        SELECT COALESCE(MAX(seq), 0) + 1
                        FROM prompt
                        WHERE session_id = NEW.session_id
                    )
                    WHERE id = NEW.id;
                END
            """)

            conn.commit()
        finally:
            conn.close()

    def handle_user_prompt_submit(self, data):
        """Handle UserPromptSubmit event - insert new prompt record"""
        session_id = data.get("session_id")
        prompt = data.get("prompt", "")
        cwd = data.get("cwd", "")

        # Validate required fields
        if not session_id:
            logging.warning("Missing required field: session_id")
            return

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """
                INSERT INTO prompt (session_id, prompt, cwd)
                VALUES (?, ?, ?)
            """,
                (session_id, prompt, cwd),
            )
            conn.commit()
            logging.info(f"Recorded prompt for session {session_id}")
        except sqlite3.Error as e:
            logging.error(f"Database error in handle_user_prompt_submit: {e}")
        finally:
            if conn:
                conn.close()

    def handle_stop(self, data):
        """Handle Stop event - update completion time and send notification"""
        session_id = data.get("session_id")

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Find the latest unfinished record for this session
            cursor = conn.execute(
                """
                SELECT id, created_at, cwd
                FROM prompt
                WHERE session_id = ? AND stoped_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if row:
                record_id, created_at, cwd = row

                # Update completion time
                conn.execute(
                    """
                    UPDATE prompt
                    SET stoped_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (record_id,),
                )
                conn.commit()

                # Get seq number and calculate duration
                cursor = conn.execute(
                    "SELECT seq FROM prompt WHERE id = ?", (record_id,)
                )
                seq_row = cursor.fetchone()
                seq = seq_row[0] if seq_row else 1

                duration = self.calculate_duration_from_db(record_id)
                self.send_notification(
                    title=os.path.basename(cwd) if cwd else "Claude Task",
                    subtitle=f"job#{seq} done, duration: {duration}",
                    cwd=cwd,
                )

                logging.info(
                    f"Task completed for session {session_id}, job#{seq}, duration: {duration}"
                )
        finally:
            if conn:
                conn.close()

    def handle_notification(self, data):
        """Handle Notification event - check for various notification types and send notifications"""
        session_id = data.get("session_id")
        message = data.get("message", "")
        cwd = data.get("cwd", "")

        # Log all notifications for debugging
        logging.info(f"[NOTIFICATION] session={session_id}, message='{message}'")

        # Determine notification type and subtitle
        message_lower = message.lower()
        subtitle = None
        should_update_db = False
        should_notify = True

        if (
            "waiting for your input" in message_lower
            or "waiting for input" in message_lower
        ):
            subtitle = "Waiting for input"
            should_update_db = True
            should_notify = True  # Send notification to alert user
        elif "permission" in message_lower:
            subtitle = "Permission Required"
        elif "approval" in message_lower or "choose an option" in message_lower:
            subtitle = "Action Required"
        else:
            # For other notifications, use a generic subtitle
            subtitle = "Notification"

        # Update database for waiting notifications
        if should_update_db:
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                # Fix: Use subquery instead of ORDER BY/LIMIT in UPDATE
                conn.execute(
                    """
                    UPDATE prompt
                    SET lastWaitUserAt = CURRENT_TIMESTAMP
                    WHERE id = (
                        SELECT id FROM prompt
                        WHERE session_id = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                    )
                """,
                    (session_id,),
                )
                conn.commit()
                logging.info(f"Updated lastWaitUserAt for session {session_id}")
            finally:
                if conn:
                    conn.close()

        # Send notification only if should_notify is True
        if should_notify:
            self.send_notification(
                title=os.path.basename(cwd) if cwd else "Claude Task",
                subtitle=subtitle,
                cwd=cwd,
            )
            logging.info(f"Notification sent for session {session_id}: {subtitle}")
        else:
            logging.info(
                f"Notification suppressed for session {session_id}: {subtitle}"
            )

    def calculate_duration_from_db(self, record_id):
        """Calculate duration for a completed record"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                """
                SELECT created_at, stoped_at
                FROM prompt
                WHERE id = ?
            """,
                (record_id,),
            )

            row = cursor.fetchone()
            if row and row[1]:
                return self.calculate_duration(row[0], row[1])

            return "Unknown"
        finally:
            if conn:
                conn.close()

    def calculate_duration(self, start_time, end_time):
        """Calculate human-readable duration between two timestamps"""
        try:
            if isinstance(start_time, str):
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            else:
                start_dt = datetime.fromisoformat(start_time)

            if isinstance(end_time, str):
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            else:
                end_dt = datetime.fromisoformat(end_time)

            duration = end_dt - start_dt
            total_seconds = int(duration.total_seconds())

            if total_seconds < 60:
                return f"{total_seconds}秒"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                if seconds > 0:
                    return f"{minutes}分{seconds}秒"
                else:
                    return f"{minutes}分钟"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                if minutes > 0:
                    return f"{hours}小时{minutes}分钟"
                else:
                    return f"{hours}小时"
        except Exception as e:
            logging.error(f"Error calculating duration: {e}")
            return "Unknown"

    def _send_notification_plyer(self, title, message, cwd=None):
        """
        Send notification using plyer (cross-platform).

        Returns:
            bool: True if successful, False otherwise
        """
        if not PLYER_AVAILABLE:
            return False

        try:
            # Plyer doesn't support click actions, so we just send the notification
            plyer_notification.notify(
                title=title,
                message=message,
                app_name='CCNotify',
                timeout=10  # seconds
            )
            logging.info(f"Notification sent via plyer: {title} - {message}")
            return True
        except Exception as e:
            logging.warning(f"Plyer notification failed: {e}")
            return False

    def _send_notification_macos(self, title, message, cwd=None):
        """
        Send notification on macOS using terminal-notifier.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = [
                "terminal-notifier",
                "-sound",
                "default",
                "-title",
                title,
                "-message",
                message,
            ]

            # Add click action to open VS Code if cwd is provided
            if cwd:
                vscode_cmd = get_vscode_command()
                if vscode_cmd:
                    cmd.extend(["-execute", f'{vscode_cmd} "{cwd}"'])

            result = subprocess.run(cmd, check=False, capture_output=True, timeout=5)
            if result.returncode == 0:
                logging.info(f"Notification sent via terminal-notifier: {title} - {message}")
                return True
            else:
                logging.warning(f"terminal-notifier returned non-zero exit code: {result.returncode}")
                return False
        except FileNotFoundError:
            logging.warning("terminal-notifier not found")
            return False
        except subprocess.TimeoutExpired:
            logging.warning("terminal-notifier timed out")
            return False
        except Exception as e:
            logging.warning(f"macOS notification failed: {e}")
            return False

    def _send_notification_linux(self, title, message, cwd=None):
        """
        Send notification on Linux using notify-send.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = ["notify-send", title, message, "-u", "normal", "-t", "10000"]

            result = subprocess.run(cmd, check=False, capture_output=True, timeout=5)
            if result.returncode == 0:
                logging.info(f"Notification sent via notify-send: {title} - {message}")
                return True
            else:
                logging.warning(f"notify-send returned non-zero exit code: {result.returncode}")
                return False
        except FileNotFoundError:
            logging.warning("notify-send not found (install libnotify-bin on Debian/Ubuntu)")
            return False
        except subprocess.TimeoutExpired:
            logging.warning("notify-send timed out")
            return False
        except Exception as e:
            logging.warning(f"Linux notification failed: {e}")
            return False

    def _send_notification_windows(self, title, message, cwd=None):
        """
        Send notification on Windows using PowerShell.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use PowerShell to show a Windows toast notification
            ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{title}</text>
            <text id="2">{message}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("CCNotify").Show($toast)
"""

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                check=False,
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                logging.info(f"Notification sent via PowerShell: {title} - {message}")
                return True
            else:
                logging.warning(f"PowerShell notification returned non-zero exit code: {result.returncode}")
                return False
        except FileNotFoundError:
            logging.warning("PowerShell not found")
            return False
        except subprocess.TimeoutExpired:
            logging.warning("PowerShell notification timed out")
            return False
        except Exception as e:
            logging.warning(f"Windows notification failed: {e}")
            return False

    def send_notification(self, title, subtitle, cwd=None):
        """
        Send cross-platform desktop notification.

        Tries multiple notification methods in order of preference:
        1. Platform-specific native method (terminal-notifier, notify-send, PowerShell)
        2. Plyer (cross-platform library)
        3. Logs warning if all methods fail

        Args:
            title: Notification title
            subtitle: Notification subtitle/message
            cwd: Optional working directory (for click-to-open in VS Code)
        """
        current_time = datetime.now().strftime("%B %d, %Y at %H:%M")
        message = f"{subtitle}\n{current_time}"

        current_platform = get_platform()
        logging.info(f"Sending notification on platform: {current_platform}")

        success = False

        # Try platform-specific method first
        if current_platform == 'darwin':
            success = self._send_notification_macos(title, message, cwd)
            if not success:
                # Fallback to plyer on macOS
                success = self._send_notification_plyer(title, message, cwd)
        elif current_platform == 'linux':
            success = self._send_notification_linux(title, message, cwd)
            if not success:
                # Fallback to plyer on Linux
                success = self._send_notification_plyer(title, message, cwd)
        elif current_platform == 'windows':
            # Try plyer first on Windows (more reliable)
            success = self._send_notification_plyer(title, message, cwd)
            if not success:
                # Fallback to PowerShell
                success = self._send_notification_windows(title, message, cwd)
        else:
            # Unknown platform, try plyer
            success = self._send_notification_plyer(title, message, cwd)

        if not success:
            logging.warning(
                f"All notification methods failed. "
                f"Title: {title}, Message: {subtitle}. "
                f"Consider installing: "
                f"macOS: 'brew install terminal-notifier', "
                f"Linux: 'sudo apt install libnotify-bin', "
                f"All platforms: 'pip install plyer'"
            )


def validate_input_data(data, expected_event_name):
    """Validate input data matches design specification"""
    required_fields = {
        "UserPromptSubmit": ["session_id", "prompt", "cwd", "hook_event_name"],
        "Stop": ["session_id", "hook_event_name"],
        "Notification": ["session_id", "message", "hook_event_name"],
    }

    if expected_event_name not in required_fields:
        raise ValueError(f"Unknown event type: {expected_event_name}")

    # Check hook_event_name matches expected
    if data.get("hook_event_name") != expected_event_name:
        raise ValueError(
            f"Event name mismatch: expected {expected_event_name}, got {data.get('hook_event_name')}"
        )

    # Check required fields
    missing_fields = []
    for field in required_fields[expected_event_name]:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(
            f"Missing required fields for {expected_event_name}: {missing_fields}"
        )

    return True


def main():
    """Main entry point - read JSON from stdin and process event"""
    try:
        # Check if hook type is provided as command line argument
        if len(sys.argv) < 2:
            print("ok")
            return

        expected_event_name = sys.argv[1]
        valid_events = ["UserPromptSubmit", "Stop", "Notification"]

        if expected_event_name not in valid_events:
            logging.error(f"Invalid hook type: {expected_event_name}")
            logging.error(f"Valid hook types: {', '.join(valid_events)}")
            sys.exit(1)

        # Read JSON data from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            logging.warning("No input data received")
            return

        data = json.loads(input_data)

        # Validate input data
        validate_input_data(data, expected_event_name)

        tracker = ClaudePromptTracker()

        if expected_event_name == "UserPromptSubmit":
            tracker.handle_user_prompt_submit(data)
        elif expected_event_name == "Stop":
            tracker.handle_stop(data)
        elif expected_event_name == "Notification":
            tracker.handle_notification(data)

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
