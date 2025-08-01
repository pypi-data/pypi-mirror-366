"""
Issues plugin for yaapp framework.
Provides comprehensive issue management with review workflows.
"""

from .plugin import Issues

# Backward compatibility
IssuesPlugin = Issues

__all__ = ["Issues", "IssuesPlugin"]