"""
Routing plugin for YAAPP framework.
Provides context-aware routing, agent switching, session isolation, and load balancing.
"""

from .plugin import Router, RouteTarget, RoutingStrategy

__all__ = ["Router", "RouteTarget", "RoutingStrategy"]