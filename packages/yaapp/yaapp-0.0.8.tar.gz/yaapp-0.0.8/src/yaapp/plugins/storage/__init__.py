"""
Storage plugin for YAAPP framework.
Provides unified data persistence capabilities configured through yaapp config.
"""

from .plugin import (
    Storage,
    StorageManager,
    StoragePlugin,  # For discovery system
    MemoryStorage,
    FileStorage,
    SQLiteStorage,
)

# Try to import Git storage
try:
    from .git import GitStorage
    __all__ = [
        "Storage", "StorageManager", "StoragePlugin", "GitStorage",
        "MemoryStorage", "FileStorage", "SQLiteStorage",
    ]
except ImportError:
    # Git storage not available
    GitStorage = None
    __all__ = [
        "Storage", "StorageManager", "StoragePlugin",
        "MemoryStorage", "FileStorage", "SQLiteStorage",
    ]