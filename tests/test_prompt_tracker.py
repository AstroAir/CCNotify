#!/usr/bin/env python3
"""
Test suite for Claude Prompt Tracker System
"""

import os
import sys
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import ccnotify
sys.path.insert(0, str(Path(__file__).parent.parent))
from ccnotify import ClaudePromptTracker


class TestClaudePromptTracker(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.temp_dir) / "test_prompt_tracker.db"
        
        # Mock the database path
        self.original_db_path = None
        
    def tearDown(self):
        """Clean up test environment"""
        import gc
        import time

        # Force garbage collection to close any open database connections
        gc.collect()

        # Try to delete the database file, with retry for Windows file locking
        max_retries = 3
        for i in range(max_retries):
            try:
                if self.test_db_path.exists():
                    self.test_db_path.unlink()
                break
            except PermissionError:
                if i < max_retries - 1:
                    time.sleep(0.1)
                    gc.collect()
                else:
                    # If we still can't delete, just skip it
                    pass

        # Try to remove the temp directory
        try:
            os.rmdir(self.temp_dir)
        except (OSError, PermissionError):
            # Directory might not be empty or file is locked, skip
            pass
    
    def create_test_tracker(self):
        """Create a tracker instance with test database"""
        tracker = ClaudePromptTracker()
        tracker.db_path = str(self.test_db_path)
        tracker.init_database()
        return tracker
    
    def test_database_initialization(self):
        """Test database and table creation"""
        tracker = self.create_test_tracker()
        
        # Check if database file was created
        self.assertTrue(self.test_db_path.exists())
        
        # Check if tables exist
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='prompt'
            """)
            self.assertIsNotNone(cursor.fetchone())
    
    def test_user_prompt_submit(self):
        """Test UserPromptSubmit event handling"""
        tracker = self.create_test_tracker()
        
        test_data = {
            "session_id": "session_001",
            "prompt": "创建一个Python脚本来处理CSV文件数据",
            "cwd": "/Users/developer/projects/my-app",
            "hook_event_name": "UserPromptSubmit"
        }
        
        tracker.handle_user_prompt_submit(test_data)

        # Verify record was inserted
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id, prompt, cwd, seq
                FROM prompt
                WHERE session_id = ?
            """, (test_data["session_id"],))

            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "session_001")
            self.assertEqual(row[1], test_data["prompt"])
            self.assertEqual(row[2], "/Users/developer/projects/my-app")
            self.assertEqual(row[3], 1)  # First record should have seq=1
    
    def test_seq_auto_increment(self):
        """Test sequence auto-increment for same session"""
        tracker = self.create_test_tracker()
        
        # Insert multiple prompts for same session
        for i in range(3):
            test_data = {
                "session_id": "session_003",
                "prompt": f"第{i+1}个prompt",
                "cwd": "/Users/developer/projects/data-analysis",
                "hook_event_name": "UserPromptSubmit"
            }
            tracker.handle_user_prompt_submit(test_data)
        
        # Verify seq values
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT seq FROM prompt
                WHERE session_id = 'session_003'
                ORDER BY seq
            """)
            
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0][0], 1)
            self.assertEqual(rows[1][0], 2)
            self.assertEqual(rows[2][0], 3)
    
    @patch('ccnotify.ClaudePromptTracker.send_notification')
    def test_stop_event_handling(self, mock_send_notification):
        """Test Stop event handling with notification"""
        tracker = self.create_test_tracker()

        # First insert a prompt
        submit_data = {
            "session_id": "session_001",
            "prompt": "测试任务",
            "cwd": "/Users/developer/projects/test-app",
            "hook_event_name": "UserPromptSubmit"
        }
        tracker.handle_user_prompt_submit(submit_data)

        # Then handle stop event
        stop_data = {
            "session_id": "session_001",
            "hook_event_name": "Stop"
        }
        tracker.handle_stop(stop_data)

        # Verify stoped_at was updated
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT stoped_at FROM prompt
                WHERE session_id = ?
            """, (submit_data["session_id"],))

            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertIsNotNone(row[0])  # stoped_at should be set

        # Verify notification was sent
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args
        # Check that title contains the directory name
        self.assertIn('test-app', call_args[1]['title'])
    
    @patch('ccnotify.ClaudePromptTracker.send_notification')
    def test_notification_event_handling(self, mock_send_notification):
        """Test Notification event handling for waiting input"""
        tracker = self.create_test_tracker()

        # First insert a prompt
        submit_data = {
            "session_id": "session_002",
            "prompt": "测试等待输入",
            "cwd": "/Users/developer/projects/web-app",
            "hook_event_name": "UserPromptSubmit"
        }
        tracker.handle_user_prompt_submit(submit_data)

        # Then handle notification event
        notification_data = {
            "session_id": "session_002",
            "message": "Claude is waiting for your input",
            "cwd": "/Users/developer/projects/web-app",
            "hook_event_name": "Notification"
        }
        tracker.handle_notification(notification_data)

        # Verify lastWaitUserAt was updated
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT lastWaitUserAt FROM prompt
                WHERE session_id = ?
            """, (submit_data["session_id"],))

            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertIsNotNone(row[0])  # lastWaitUserAt should be set

        # Verify notification was sent
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args
        # Check that title contains the directory name
        self.assertIn('web-app', call_args[1]['title'])
    
    def test_duration_calculation(self):
        """Test duration calculation functionality"""
        tracker = self.create_test_tracker()
        
        # Test various duration scenarios
        test_cases = [
            ("2024-01-01T10:00:00", "2024-01-01T10:00:30", "30秒"),
            ("2024-01-01T10:00:00", "2024-01-01T10:02:30", "2分30秒"),
            ("2024-01-01T10:00:00", "2024-01-01T10:05:00", "5分钟"),
            ("2024-01-01T10:00:00", "2024-01-01T11:30:00", "1小时30分钟"),
            ("2024-01-01T10:00:00", "2024-01-01T12:00:00", "2小时"),
        ]
        
        for start, end, expected in test_cases:
            result = tracker.calculate_duration(start, end)
            self.assertEqual(result, expected, f"Failed for {start} to {end}")
    
    def test_multiple_sessions(self):
        """Test handling multiple concurrent sessions"""
        tracker = self.create_test_tracker()
        
        # Create prompts for different sessions
        sessions = ["session_004a", "session_004b", "session_004c"]
        
        for session_id in sessions:
            test_data = {
                "session_id": session_id,
                "prompt": f"任务 for {session_id}",
                "cwd": f"/Users/developer/projects/{session_id}",
                "hook_event_name": "UserPromptSubmit"
            }
            tracker.handle_user_prompt_submit(test_data)
        
        # Verify all sessions have records
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT session_id FROM prompt")
            found_sessions = [row[0] for row in cursor.fetchall()]
            
            for session_id in sessions:
                self.assertIn(session_id, found_sessions)
    
    def test_error_handling(self):
        """Test error handling for malformed data"""
        tracker = self.create_test_tracker()
        
        # Test with missing required fields
        invalid_data = {
            "hook_event_name": "UserPromptSubmit"
            # Missing session_id
        }
        
        # Should not raise exception
        try:
            tracker.handle_user_prompt_submit(invalid_data)
        except Exception as e:
            self.fail(f"handle_user_prompt_submit raised {type(e).__name__} unexpectedly!")


class TestMainFunction(unittest.TestCase):
    """Test the main function and JSON processing"""
    
    @patch('sys.stdin')
    @patch('sys.argv', ['ccnotify.py', 'UserPromptSubmit'])
    @patch('ccnotify.ClaudePromptTracker')
    def test_main_user_prompt_submit(self, mock_tracker_class, mock_stdin):
        """Test main function with UserPromptSubmit event"""
        # Mock stdin input
        test_data = {
            "session_id": "session_001",
            "prompt": "测试prompt",
            "cwd": "/Users/developer/projects/test",
            "hook_event_name": "UserPromptSubmit"
        }
        mock_stdin.read.return_value = json.dumps(test_data)

        # Mock tracker instance
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        # Import and run main
        from ccnotify import main
        main()

        # Verify tracker was called correctly
        mock_tracker.handle_user_prompt_submit.assert_called_once_with(test_data)
    
    @patch('sys.stdin')
    @patch('sys.argv', ['ccnotify.py', 'UserPromptSubmit'])
    def test_main_invalid_json(self, mock_stdin):
        """Test main function with invalid JSON"""
        mock_stdin.read.return_value = "invalid json"

        from ccnotify import main

        # Should exit with error code
        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()