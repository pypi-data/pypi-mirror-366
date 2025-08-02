"""
Router plugin - simple pattern matching and routing.
"""

import re
from typing import Dict, Any, Callable, Optional
from yaapp.result import Result, Ok
from yaapp import yaapp


@yaapp.expose("router")
class Router:
    """Simple router with pattern matching."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        self.routes: Dict[str, Callable] = {}
        
        # Load routes from config if provided
        self._load_routes_from_config()
    
    def _load_routes_from_config(self):
        """Load routes from configuration."""
        if not self.config:
            return
        
        # Load predefined routes from config
        config_routes = self.config.get('routes', {})
        for pattern, handler_name in config_routes.items():
            # For now, just store the handler name - in a real implementation
            # you'd resolve the handler from a registry or import it
            print(f"Router: Found route in config: {pattern} -> {handler_name}")
    
    def add(self, pattern: str, handler: Callable) -> Result[bool]:
        """Add a route."""
        self.routes[pattern] = handler
        return Ok(True)
    
    def delete(self, pattern: str) -> Result[bool]:
        """Delete a route."""
        if pattern in self.routes:
            del self.routes[pattern]
            return Ok(True)
        else:
            return Result.error(f"Route pattern '{pattern}' not found")
    
    def update(self, pattern: str, handler: Callable) -> Result[bool]:
        """Update a route handler."""
        if pattern in self.routes:
            self.routes[pattern] = handler
            return Ok(True)
        else:
            return Result.error(f"Route pattern '{pattern}' not found")
    
    def route(self, path: str, request: Dict[str, Any]) -> Result[Any]:
        """Route a request to matching handler."""
        for pattern, handler in self.routes.items():
            if re.match(pattern, path):
                try:
                    result = handler(request)
                    return Ok(result)
                except Exception as e:
                    return Result.error(f"Handler error: {str(e)}")
        
        return Result.error(f"No route found for path: {path}")
    
    def list_routes(self) -> Result[Dict[str, str]]:
        """List all routes."""
        route_info = {pattern: str(handler) for pattern, handler in self.routes.items()}
        return Ok(route_info)
    
    def get_config(self) -> Result[Dict[str, Any]]:
        """Get current router configuration."""
        return Ok(self.config)
    
    def reload_config(self, new_config: Dict[str, Any]) -> Result[bool]:
        """Reload configuration."""
        self.config = new_config
        self._load_routes_from_config()
        return Ok(True)