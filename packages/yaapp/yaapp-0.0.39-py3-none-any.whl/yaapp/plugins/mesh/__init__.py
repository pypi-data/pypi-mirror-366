"""
Mesh Plugin - Service/Plugin Orchestrator

Plugin is auto-discovered via @expose decorator.
No need to import here to avoid circular imports.
"""

# from .plugin import Mesh  # Disabled to avoid circular imports

__all__ = []  # Empty - plugin registers itself via @expose