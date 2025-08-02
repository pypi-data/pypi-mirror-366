"""
Git-based storage backend for YAAPP framework.
Provides immutable, auditable storage using Git objects.
"""

from .backend import GitStorage

__all__ = ["GitStorage"]