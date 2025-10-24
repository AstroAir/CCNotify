"""
CCNotify - Desktop notifications for Claude Code

Provides desktop notifications when Claude needs input or completes tasks.
"""

__version__ = "0.1.0"
__author__ = "CCNotify Contributors"
__license__ = "MIT"

from .ccnotify import ClaudePromptTracker, get_platform, get_vscode_command

__all__ = [
    "ClaudePromptTracker",
    "get_platform",
    "get_vscode_command",
    "__version__",
]

