"""
Remote Process plugin for yaapp framework.
Provides PTY-based subprocess execution and management.
"""

from .plugin import RemoteProcess, create_remote_process, SubprocessManager, create_subprocess_manager

__all__ = ["RemoteProcess", "create_remote_process", "SubprocessManager", "create_subprocess_manager"]