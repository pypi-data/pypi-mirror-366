"""
Smart Timeout MCP Server
Intelligent timeout calculation and progress monitoring for Claude Code
"""

__version__ = "1.0.0"
__author__ = "yscha88"
__email__ = "clmfkilu@gmail.com"

# Core classes and functions
from .smart_timeout import (
    SmartTimeout,
    TaskType,
    get_ollama_timeout,
    get_download_timeout,
    suggest_timeout
)

from .progress_monitor import (
    UniversalProgressMonitor,
    ProgressInfo,
    TaskStatus,
    start_ollama_pull,
    start_download,
    start_command,
    get_all_progress,
    get_task_progress,
    cancel_task
)

# Convenience imports
__all__ = [
    # Core timeout functionality
    "SmartTimeout",
    "TaskType", 
    "get_ollama_timeout",
    "get_download_timeout",
    "suggest_timeout",
    
    # Progress monitoring
    "UniversalProgressMonitor",
    "ProgressInfo",
    "TaskStatus",
    "start_ollama_pull",
    "start_download", 
    "start_command",
    "get_all_progress",
    "get_task_progress",
    "cancel_task",
]