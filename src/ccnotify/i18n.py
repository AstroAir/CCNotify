#!/usr/bin/env python3
"""
Internationalization (i18n) module for CCNotify
Provides language detection and translation support
"""

import os
import locale
import logging


def get_system_language():
    """
    Detect the system language with fallback chain.
    
    Returns:
        str: Language code ('en', 'zh-CN', etc.) or 'en' as default
    """
    try:
        # Try to get locale from locale module
        try:
            # Get current locale setting
            current_locale = locale.getlocale()[0]
            if current_locale:
                # Convert locale to language code
                # Examples: 'en_US' -> 'en', 'zh_CN' -> 'zh-CN'
                if current_locale.startswith('zh_CN') or current_locale.startswith('zh-Hans'):
                    return 'zh-CN'
                elif current_locale.startswith('en'):
                    return 'en'
                # Add more language mappings as needed
                else:
                    # Extract base language code
                    lang_code = current_locale.split('_')[0]
                    return lang_code
        except (ValueError, AttributeError):
            pass
        
        # Fallback to environment variables
        for env_var in ['LANG', 'LC_ALL', 'LANGUAGE']:
            env_value = os.environ.get(env_var)
            if env_value:
                # Parse environment variable (e.g., 'en_US.UTF-8' -> 'en')
                if 'zh_CN' in env_value or 'zh-Hans' in env_value:
                    return 'zh-CN'
                elif env_value.startswith('en'):
                    return 'en'
                else:
                    # Extract base language code
                    lang_code = env_value.split('_')[0].split('.')[0]
                    if lang_code:
                        return lang_code
        
        # Default to English if detection fails
        return 'en'
    
    except Exception as e:
        logging.warning(f"Language detection failed: {e}, defaulting to English")
        return 'en'


# Translation dictionaries
TRANSLATIONS = {
    'en': {
        # Notification messages
        'notification.task_complete': 'job#{seq} done, duration: {duration}',
        'notification.waiting_input': 'Waiting for input',
        'notification.permission_required': 'Permission Required',
        'notification.action_required': 'Action Required',
        'notification.generic': 'Notification',
        'notification.default_title': 'Claude Task',
        
        # Duration units
        'duration.seconds': '{seconds}s',
        'duration.minutes': '{minutes}m',
        'duration.minutes_seconds': '{minutes}m {seconds}s',
        'duration.hours': '{hours}h',
        'duration.hours_minutes': '{hours}h {minutes}m',
        'duration.unknown': 'Unknown',
        
        # Log messages
        'log.initialized': 'CCNotify initialized on platform: {platform}',
        'log.python_version': 'Python version: {version}',
        'log.plyer_available': 'Plyer available: {available}',
        'log.vscode_found': 'VS Code command found: {command}',
        'log.vscode_not_found': 'VS Code command not found in PATH',
        'log.sending_notification': 'Sending notification on platform: {platform}',
        'log.notification_sent': 'Notification sent for session {session_id}: {subtitle}',
        'log.notification_suppressed': 'Notification suppressed for session {session_id}: {subtitle}',
        'log.task_completed': 'Task completed for session {session_id}, job#{seq}, duration: {duration}',
        'log.recorded_prompt': 'Recorded prompt for session {session_id}',
        'log.updated_wait_time': 'Updated lastWaitUserAt for session {session_id}',
        
        # Error messages
        'error.missing_field': 'Missing required field: {field}',
        'error.db_error': 'Database error in {function}: {error}',
        'error.duration_calc': 'Error calculating duration: {error}',
        'error.notification_failed': 'All notification methods failed. Title: {title}, Message: {message}. Consider installing: macOS: \'brew install terminal-notifier\', Linux: \'sudo apt install libnotify-bin\', All platforms: \'pip install plyer\'',
        'error.plyer_failed': 'Plyer notification failed: {error}',
        'error.macos_failed': 'macOS notification failed: {error}',
        'error.linux_failed': 'Linux notification failed: {error}',
        'error.windows_failed': 'Windows notification failed: {error}',
        'error.terminal_notifier_not_found': 'terminal-notifier not found',
        'error.terminal_notifier_timeout': 'terminal-notifier timed out',
        'error.terminal_notifier_exit_code': 'terminal-notifier returned non-zero exit code: {code}',
        'error.notify_send_not_found': 'notify-send not found (install libnotify-bin on Debian/Ubuntu)',
        'error.notify_send_timeout': 'notify-send timed out',
        'error.notify_send_exit_code': 'notify-send returned non-zero exit code: {code}',
        'error.powershell_not_found': 'PowerShell not found',
        'error.powershell_timeout': 'PowerShell notification timed out',
        'error.powershell_exit_code': 'PowerShell notification returned non-zero exit code: {code}',
        
        # Notification method success messages
        'success.plyer': 'Notification sent via plyer: {title} - {message}',
        'success.terminal_notifier': 'Notification sent via terminal-notifier: {title} - {message}',
        'success.notify_send': 'Notification sent via notify-send: {title} - {message}',
        'success.powershell': 'Notification sent via PowerShell: {title} - {message}',
        
        # Validation errors
        'validation.unknown_event': 'Unknown event type: {event}',
        'validation.event_mismatch': 'Event name mismatch: expected {expected}, got {actual}',
        'validation.missing_fields': 'Missing required fields for {event}: {fields}',
        'validation.invalid_hook': 'Invalid hook type: {hook}',
        'validation.valid_hooks': 'Valid hook types: {hooks}',
        'validation.no_input': 'No input data received',
        'validation.json_error': 'JSON decode error: {error}',
    },
    'zh-CN': {
        # Notification messages
        'notification.task_complete': '任务#{seq}完成，耗时：{duration}',
        'notification.waiting_input': '等待输入',
        'notification.permission_required': '需要权限',
        'notification.action_required': '需要操作',
        'notification.generic': '通知',
        'notification.default_title': 'Claude 任务',
        
        # Duration units
        'duration.seconds': '{seconds}秒',
        'duration.minutes': '{minutes}分钟',
        'duration.minutes_seconds': '{minutes}分{seconds}秒',
        'duration.hours': '{hours}小时',
        'duration.hours_minutes': '{hours}小时{minutes}分钟',
        'duration.unknown': '未知',
        
        # Log messages
        'log.initialized': 'CCNotify 已在平台上初始化：{platform}',
        'log.python_version': 'Python 版本：{version}',
        'log.plyer_available': 'Plyer 可用：{available}',
        'log.vscode_found': '找到 VS Code 命令：{command}',
        'log.vscode_not_found': '在 PATH 中未找到 VS Code 命令',
        'log.sending_notification': '在平台上发送通知：{platform}',
        'log.notification_sent': '已为会话 {session_id} 发送通知：{subtitle}',
        'log.notification_suppressed': '已抑制会话 {session_id} 的通知：{subtitle}',
        'log.task_completed': '会话 {session_id} 的任务已完成，任务#{seq}，耗时：{duration}',
        'log.recorded_prompt': '已记录会话 {session_id} 的提示',
        'log.updated_wait_time': '已更新会话 {session_id} 的 lastWaitUserAt',
        
        # Error messages
        'error.missing_field': '缺少必需字段：{field}',
        'error.db_error': '{function} 中的数据库错误：{error}',
        'error.duration_calc': '计算持续时间时出错：{error}',
        'error.notification_failed': '所有通知方法均失败。标题：{title}，消息：{message}。请考虑安装：macOS：\'brew install terminal-notifier\'，Linux：\'sudo apt install libnotify-bin\'，所有平台：\'pip install plyer\'',
        'error.plyer_failed': 'Plyer 通知失败：{error}',
        'error.macos_failed': 'macOS 通知失败：{error}',
        'error.linux_failed': 'Linux 通知失败：{error}',
        'error.windows_failed': 'Windows 通知失败：{error}',
        'error.terminal_notifier_not_found': '未找到 terminal-notifier',
        'error.terminal_notifier_timeout': 'terminal-notifier 超时',
        'error.terminal_notifier_exit_code': 'terminal-notifier 返回非零退出代码：{code}',
        'error.notify_send_not_found': '未找到 notify-send（在 Debian/Ubuntu 上安装 libnotify-bin）',
        'error.notify_send_timeout': 'notify-send 超时',
        'error.notify_send_exit_code': 'notify-send 返回非零退出代码：{code}',
        'error.powershell_not_found': '未找到 PowerShell',
        'error.powershell_timeout': 'PowerShell 通知超时',
        'error.powershell_exit_code': 'PowerShell 通知返回非零退出代码：{code}',
        
        # Notification method success messages
        'success.plyer': '通过 plyer 发送通知：{title} - {message}',
        'success.terminal_notifier': '通过 terminal-notifier 发送通知：{title} - {message}',
        'success.notify_send': '通过 notify-send 发送通知：{title} - {message}',
        'success.powershell': '通过 PowerShell 发送通知：{title} - {message}',
        
        # Validation errors
        'validation.unknown_event': '未知事件类型：{event}',
        'validation.event_mismatch': '事件名称不匹配：期望 {expected}，得到 {actual}',
        'validation.missing_fields': '{event} 缺少必需字段：{fields}',
        'validation.invalid_hook': '无效的钩子类型：{hook}',
        'validation.valid_hooks': '有效的钩子类型：{hooks}',
        'validation.no_input': '未收到输入数据',
        'validation.json_error': 'JSON 解码错误：{error}',
    }
}


# Detect system language once at module load
CURRENT_LANGUAGE = get_system_language()


def t(key, **kwargs):
    """
    Translate a key to the current language with optional formatting.
    
    Args:
        key: Translation key (e.g., 'notification.task_complete')
        **kwargs: Format arguments for the translation string
    
    Returns:
        str: Translated and formatted string, or the key itself if not found
    """
    # Get translation for current language, fallback to English
    translation = TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(key)
    
    # If not found in current language, try English
    if translation is None:
        translation = TRANSLATIONS.get('en', {}).get(key)
    
    # If still not found, return the key itself
    if translation is None:
        logging.warning(f"Translation key not found: {key}")
        return key
    
    # Format the translation with provided arguments
    try:
        return translation.format(**kwargs)
    except KeyError as e:
        logging.warning(f"Missing format argument for key '{key}': {e}")
        return translation


def get_current_language():
    """
    Get the currently detected language code.
    
    Returns:
        str: Current language code (e.g., 'en', 'zh-CN')
    """
    return CURRENT_LANGUAGE


def set_language(lang_code):
    """
    Manually set the language (useful for testing).
    
    Args:
        lang_code: Language code to set (e.g., 'en', 'zh-CN')
    """
    global CURRENT_LANGUAGE
    if lang_code in TRANSLATIONS:
        CURRENT_LANGUAGE = lang_code
    else:
        logging.warning(f"Unsupported language code: {lang_code}, keeping current: {CURRENT_LANGUAGE}")

