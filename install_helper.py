#!/usr/bin/env python3
"""
CCNotify Installation Helper
Handles configuration file management for CCNotify installation
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path


def get_settings_path():
    """Get the path to Claude settings.json based on platform"""
    if sys.platform == 'win32':
        base_path = Path(os.environ.get('USERPROFILE', ''))
    else:
        base_path = Path.home()
    
    return base_path / '.claude' / 'settings.json'


def get_install_path():
    """Get the CCNotify installation path based on platform"""
    if sys.platform == 'win32':
        base_path = Path(os.environ.get('USERPROFILE', ''))
        script_name = 'python %USERPROFILE%\\.claude\\ccnotify\\ccnotify.py'
    else:
        base_path = Path.home()
        script_name = '~/.claude/ccnotify/ccnotify.py'
    
    install_dir = base_path / '.claude' / 'ccnotify'
    return install_dir, script_name


def backup_settings(settings_path):
    """
    Create a backup of settings.json with timestamp
    
    Args:
        settings_path: Path to settings.json
        
    Returns:
        Path to backup file, or None if no backup was needed
    """
    if not settings_path.exists():
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = settings_path.parent / f'settings.json.backup.{timestamp}'
    
    try:
        shutil.copy2(settings_path, backup_path)
        print(f"✓ Backed up settings.json to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Failed to backup settings.json: {e}", file=sys.stderr)
        return None


def load_settings(settings_path):
    """
    Load settings.json, return empty dict if file doesn't exist or is invalid
    
    Args:
        settings_path: Path to settings.json
        
    Returns:
        Dictionary containing settings, or empty dict
    """
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"✗ Warning: settings.json contains invalid JSON: {e}", file=sys.stderr)
        print(f"  Please fix the JSON syntax errors before proceeding.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"✗ Error reading settings.json: {e}", file=sys.stderr)
        return None


def create_hook_config(script_path, hook_type):
    """
    Create a hook configuration object
    
    Args:
        script_path: Path to the ccnotify.py script
        hook_type: Type of hook (UserPromptSubmit, Stop, Notification)
        
    Returns:
        Hook configuration dictionary
    """
    return {
        "hooks": [
            {
                "type": "command",
                "command": f"{script_path} {hook_type}"
            }
        ]
    }


def is_hook_installed(hooks_array, script_path, hook_type):
    """
    Check if CCNotify hook is already installed
    
    Args:
        hooks_array: Array of hook configurations
        script_path: Path to the ccnotify.py script
        hook_type: Type of hook to check
        
    Returns:
        True if hook is already installed
    """
    if not hooks_array:
        return False
    
    target_command = f"{script_path} {hook_type}"
    
    for hook_group in hooks_array:
        if 'hooks' in hook_group:
            for hook in hook_group['hooks']:
                if hook.get('type') == 'command':
                    command = hook.get('command', '')
                    # Normalize paths for comparison
                    if 'ccnotify.py' in command and hook_type in command:
                        return True
    
    return False


def merge_hooks(settings, script_path):
    """
    Merge CCNotify hooks into settings
    
    Args:
        settings: Current settings dictionary
        script_path: Path to the ccnotify.py script
        
    Returns:
        Updated settings dictionary, and count of hooks added
    """
    if 'hooks' not in settings:
        settings['hooks'] = {}
    
    hooks_added = 0
    hook_types = ['UserPromptSubmit', 'Stop', 'Notification']
    
    for hook_type in hook_types:
        if hook_type not in settings['hooks']:
            settings['hooks'][hook_type] = []
        
        # Check if hook is already installed
        if is_hook_installed(settings['hooks'][hook_type], script_path, hook_type):
            print(f"  • {hook_type}: Already installed, skipping")
            continue
        
        # Add the hook
        hook_config = create_hook_config(script_path, hook_type)
        settings['hooks'][hook_type].append(hook_config)
        hooks_added += 1
        print(f"  • {hook_type}: Added")
    
    return settings, hooks_added


def save_settings(settings_path, settings):
    """
    Save settings to settings.json with proper formatting
    
    Args:
        settings_path: Path to settings.json
        settings: Settings dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with nice formatting
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline
        
        return True
    except Exception as e:
        print(f"✗ Error writing settings.json: {e}", file=sys.stderr)
        return False


def restore_backup(settings_path, backup_path):
    """
    Restore settings.json from backup
    
    Args:
        settings_path: Path to settings.json
        backup_path: Path to backup file
        
    Returns:
        True if successful, False otherwise
    """
    if not backup_path or not backup_path.exists():
        return False
    
    try:
        shutil.copy2(backup_path, settings_path)
        print(f"✓ Restored settings.json from backup")
        return True
    except Exception as e:
        print(f"✗ Failed to restore backup: {e}", file=sys.stderr)
        return False


def validate_settings(settings):
    """
    Validate that settings have the correct structure
    
    Args:
        settings: Settings dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(settings, dict):
        return False
    
    if 'hooks' in settings:
        if not isinstance(settings['hooks'], dict):
            return False
        
        for hook_type, hooks_array in settings['hooks'].items():
            if not isinstance(hooks_array, list):
                return False
    
    return True


def install_hooks(dry_run=False):
    """
    Install CCNotify hooks into settings.json
    
    Args:
        dry_run: If True, show what would be done without making changes
        
    Returns:
        0 on success, non-zero on failure
    """
    settings_path = get_settings_path()
    install_dir, script_path = get_install_path()
    
    print(f"CCNotify Configuration Helper")
    print(f"Settings file: {settings_path}")
    print(f"Script path: {script_path}")
    
    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]")
    
    print()
    
    # Load current settings
    settings = load_settings(settings_path)
    if settings is None:
        print("\n✗ Cannot proceed with invalid settings.json")
        print("  Please fix the JSON syntax errors and try again.")
        return 1
    
    # Backup existing settings
    backup_path = None
    if not dry_run and settings_path.exists():
        backup_path = backup_settings(settings_path)
        if backup_path is None and settings:
            print("✗ Failed to create backup, aborting for safety")
            return 1
    
    # Merge hooks
    print("Configuring hooks:")
    original_settings = json.dumps(settings, sort_keys=True)
    updated_settings, hooks_added = merge_hooks(settings, script_path)
    
    if hooks_added == 0:
        print("\n✓ All hooks are already installed")
        return 0
    
    # Validate merged settings
    if not validate_settings(updated_settings):
        print("\n✗ Validation failed: Invalid settings structure")
        if backup_path:
            restore_backup(settings_path, backup_path)
        return 1
    
    # Save updated settings
    if not dry_run:
        if save_settings(settings_path, updated_settings):
            print(f"\n✓ Successfully configured {hooks_added} hook(s)")
            print(f"✓ Settings saved to: {settings_path}")
            return 0
        else:
            print("\n✗ Failed to save settings")
            if backup_path:
                restore_backup(settings_path, backup_path)
            return 1
    else:
        print(f"\n[DRY RUN] Would configure {hooks_added} hook(s)")
        return 0


def remove_hooks(dry_run=False):
    """
    Remove CCNotify hooks from settings.json
    
    Args:
        dry_run: If True, show what would be done without making changes
        
    Returns:
        0 on success, non-zero on failure
    """
    settings_path = get_settings_path()
    
    print(f"CCNotify Configuration Helper - Uninstall")
    print(f"Settings file: {settings_path}")
    
    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]")
    
    print()
    
    if not settings_path.exists():
        print("✓ No settings.json found, nothing to remove")
        return 0
    
    # Load current settings
    settings = load_settings(settings_path)
    if settings is None:
        print("\n✗ Cannot proceed with invalid settings.json")
        return 1
    
    if 'hooks' not in settings:
        print("✓ No hooks configured, nothing to remove")
        return 0
    
    # Backup existing settings
    backup_path = None
    if not dry_run:
        backup_path = backup_settings(settings_path)
        if backup_path is None:
            print("✗ Failed to create backup, aborting for safety")
            return 1
    
    # Remove CCNotify hooks
    hooks_removed = 0
    hook_types = ['UserPromptSubmit', 'Stop', 'Notification']
    
    print("Removing hooks:")
    for hook_type in hook_types:
        if hook_type not in settings['hooks']:
            continue
        
        original_count = len(settings['hooks'][hook_type])
        
        # Filter out CCNotify hooks
        settings['hooks'][hook_type] = [
            hook_group for hook_group in settings['hooks'][hook_type]
            if not any(
                'ccnotify.py' in hook.get('command', '')
                for hook in hook_group.get('hooks', [])
                if hook.get('type') == 'command'
            )
        ]
        
        removed = original_count - len(settings['hooks'][hook_type])
        if removed > 0:
            hooks_removed += removed
            print(f"  • {hook_type}: Removed {removed} hook(s)")
    
    if hooks_removed == 0:
        print("✓ No CCNotify hooks found")
        return 0
    
    # Save updated settings
    if not dry_run:
        if save_settings(settings_path, settings):
            print(f"\n✓ Successfully removed {hooks_removed} hook(s)")
            return 0
        else:
            print("\n✗ Failed to save settings")
            if backup_path:
                restore_backup(settings_path, backup_path)
            return 1
    else:
        print(f"\n[DRY RUN] Would remove {hooks_removed} hook(s)")
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CCNotify Installation Helper - Manage Claude Code hooks'
    )
    parser.add_argument(
        'action',
        choices=['install', 'uninstall'],
        help='Action to perform'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == 'install':
            return install_hooks(dry_run=args.dry_run)
        elif args.action == 'uninstall':
            return remove_hooks(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

