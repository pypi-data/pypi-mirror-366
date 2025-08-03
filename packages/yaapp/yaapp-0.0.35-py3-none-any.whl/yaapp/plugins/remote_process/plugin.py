"""
Remote Process Plugin for yaapp - alias for remote plugin
"""

# Import from the actual remote plugin
from ..remote.plugin import RemoteProcess, PtyReader

def create_remote_process(config=None):
    """Factory function to create RemoteProcess instance."""
    return RemoteProcess(config)

__all__ = ['RemoteProcess', 'PtyReader', 'create_remote_process']