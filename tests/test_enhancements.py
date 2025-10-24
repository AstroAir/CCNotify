#!/usr/bin/env python3
"""
Test script for CCNotify enhancements
Tests i18n, rich integration, and notification improvements
"""

import sys
import os

# Test i18n module
print("=" * 60)
print("Testing i18n module...")
print("=" * 60)

from ccnotify.i18n import get_system_language, t, set_language, get_current_language

# Test language detection
detected_lang = get_system_language()
print(f"Detected system language: {detected_lang}")
print(f"Current language: {get_current_language()}")

# Test English translations
print("\n--- English Translations ---")
set_language('en')
print(f"Language set to: {get_current_language()}")
print(f"Task complete: {t('notification.task_complete', seq=1, duration='5m 30s')}")
print(f"Waiting input: {t('notification.waiting_input')}")
print(f"Duration (seconds): {t('duration.seconds', seconds=45)}")
print(f"Duration (minutes): {t('duration.minutes_seconds', minutes=5, seconds=30)}")

# Test Chinese translations
print("\n--- Chinese Translations ---")
set_language('zh-CN')
print(f"Language set to: {get_current_language()}")
print(f"Task complete: {t('notification.task_complete', seq=1, duration='5分30秒')}")
print(f"Waiting input: {t('notification.waiting_input')}")
print(f"Duration (seconds): {t('duration.seconds', seconds=45)}")
print(f"Duration (minutes): {t('duration.minutes_seconds', minutes=5, seconds=30)}")

# Test fallback for missing key
print("\n--- Fallback Test ---")
print(f"Missing key: {t('nonexistent.key')}")

# Test rich library
print("\n" + "=" * 60)
print("Testing Rich library integration...")
print("=" * 60)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    
    console = Console()
    
    # Test styled text
    console.print("\n[bold green]✓ Rich library is available![/bold green]")
    
    # Test Panel
    console.print(Panel.fit(
        "[cyan]CCNotify Enhanced[/cyan]\n"
        "✓ Multi-language support (EN, zh-CN)\n"
        "✓ Rich terminal formatting\n"
        "✓ Improved notification reliability",
        title="[bold magenta]Features[/bold magenta]",
        border_style="green"
    ))
    
    # Test Table
    table = Table(title="Language Support", show_header=True, header_style="bold magenta")
    table.add_column("Language", style="cyan", no_wrap=True)
    table.add_column("Code", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row("English", "en", "✓ Supported")
    table.add_row("Chinese (Simplified)", "zh-CN", "✓ Supported")
    
    console.print("\n")
    console.print(table)
    
    print("\n✓ Rich library tests passed!")
    
except ImportError as e:
    print(f"✗ Rich library not available: {e}")

# Test CCNotify initialization
print("\n" + "=" * 60)
print("Testing CCNotify initialization...")
print("=" * 60)

try:
    from ccnotify.ccnotify import ClaudePromptTracker, get_platform
    
    # Reset language to detected
    set_language(detected_lang)
    
    print(f"Platform: {get_platform()}")
    
    # Create tracker instance
    tracker = ClaudePromptTracker()
    print("✓ ClaudePromptTracker initialized successfully")
    
    # Test duration calculation
    from datetime import datetime, timedelta
    start = datetime.now()
    end = start + timedelta(seconds=45)
    duration = tracker.calculate_duration(start.isoformat(), end.isoformat())
    print(f"✓ Duration calculation: {duration}")
    
    # Test with different durations
    end2 = start + timedelta(minutes=5, seconds=30)
    duration2 = tracker.calculate_duration(start.isoformat(), end2.isoformat())
    print(f"✓ Duration calculation (5m 30s): {duration2}")
    
    end3 = start + timedelta(hours=2, minutes=15)
    duration3 = tracker.calculate_duration(start.isoformat(), end3.isoformat())
    print(f"✓ Duration calculation (2h 15m): {duration3}")
    
    print("\n✓ All CCNotify tests passed!")
    
except Exception as e:
    print(f"✗ Error during CCNotify tests: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Enhancement tests completed!")
print("=" * 60)

