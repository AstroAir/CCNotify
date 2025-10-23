#!/usr/bin/env python3
"""
Simple test script to verify platform detection and notification system.
Run this to test CCNotify on your platform without needing Claude Code.
"""

import sys
import os

# Add current directory to path to import ccnotify
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import platform detection functions
from ccnotify import get_platform, get_vscode_command, PLYER_AVAILABLE

def test_platform_detection():
    """Test platform detection"""
    print("=" * 60)
    print("CCNotify Platform Detection Test")
    print("=" * 60)
    
    platform = get_platform()
    print(f"\n✓ Detected platform: {platform}")
    
    if platform == 'windows':
        print("  → Running on Windows")
    elif platform == 'linux':
        print("  → Running on Linux")
    elif platform == 'darwin':
        print("  → Running on macOS")
    else:
        print("  → Unknown platform")
    
    print(f"\n✓ Python version: {sys.version}")
    
    # Check plyer availability
    print(f"\n✓ Plyer library available: {PLYER_AVAILABLE}")
    if not PLYER_AVAILABLE:
        print("  → Install with: pip install plyer")
    
    # Check VS Code command
    vscode_cmd = get_vscode_command()
    if vscode_cmd:
        print(f"\n✓ VS Code command found: {vscode_cmd}")
    else:
        print("\n✗ VS Code command not found in PATH")
        print("  → Make sure VS Code is installed and 'code' is in your PATH")
    
    print("\n" + "=" * 60)
    print("Platform detection test completed!")
    print("=" * 60)

def test_notification():
    """Test sending a notification"""
    print("\n" + "=" * 60)
    print("Testing Notification System")
    print("=" * 60)
    
    try:
        from ccnotify import ClaudePromptTracker
        
        print("\n→ Creating tracker instance...")
        tracker = ClaudePromptTracker()
        
        print("→ Sending test notification...")
        tracker.send_notification(
            title="CCNotify Test",
            subtitle="This is a test notification",
            cwd=None
        )
        
        print("\n✓ Notification sent successfully!")
        print("  Check if you received a desktop notification.")
        print("\n  If you didn't see a notification, check:")
        print("  - macOS: Install terminal-notifier (brew install terminal-notifier)")
        print("  - Linux: Install libnotify (sudo apt install libnotify-bin)")
        print("  - Windows: Install plyer (pip install plyer)")
        print("  - All: Check system notification settings")
        
    except Exception as e:
        print(f"\n✗ Error sending notification: {e}")
        print("  Check the log file for details: ccnotify.log")
    
    print("\n" + "=" * 60)

def main():
    """Main test function"""
    print("\nCCNotify Cross-Platform Test Suite\n")
    
    # Test platform detection
    test_platform_detection()
    
    # Ask user if they want to test notifications
    print("\n")
    response = input("Do you want to test sending a notification? (y/n): ").strip().lower()
    
    if response == 'y':
        test_notification()
    else:
        print("\nSkipping notification test.")
    
    print("\n✓ All tests completed!\n")

if __name__ == "__main__":
    main()

