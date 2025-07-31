"""
yaapp plugins - extending functionality through discovery system.

Plugins are now discovered automatically through the configuration system.
Direct imports are available for manual instantiation if needed.
"""

# Import plugin classes for manual use (not for discovery)
from .app_proxy import AppProxy
from .issues.plugin import IssuesPlugin
from .router.plugin import Router
from .storage.plugin import StoragePlugin, StorageManager
from .remote_process.plugin import RemoteProcess

# Import routing components
try:
    from .routing import RouteTarget, RoutingStrategy
except ImportError:
    # Routing module might not exist
    RouteTarget = None
    RoutingStrategy = None

# Import session handler
try:
    from .session_handler import SessionHandler
except ImportError:
    # Session handler might not exist
    SessionHandler = None

__all__ = [
    'AppProxy',
    'IssuesPlugin', 
    'Router',
    'StoragePlugin',
    'StorageManager',
    'RemoteProcess',
    'RouteTarget',
    'RoutingStrategy', 
    'SessionHandler'
]

# Backward compatibility aliases
Storage = StorageManager
SubprocessManager = RemoteProcess