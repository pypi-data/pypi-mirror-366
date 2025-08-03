"""
Registry Plugin - Service Registry for Microservices

Plugin is auto-discovered via @expose decorator.
No need to import here to avoid circular imports.
"""

# from .plugin import Registry  # Disabled to avoid circular imports

__all__ = []  # Empty - plugin registers itself via @expose