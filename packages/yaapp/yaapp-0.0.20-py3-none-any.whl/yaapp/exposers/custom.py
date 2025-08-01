"""
Custom exposer for objects that implement their own exposure logic.
"""

import inspect
from typing import Any
from .base import BaseExposer
from ..result import Result, Ok


class CustomExposer(BaseExposer):
    """Exposer for custom objects that handle their own exposure and execution."""
    
    def __init__(self):
        """Initialize custom exposer with instance cache."""
        self._instance_cache = {}  # Cache instances by class
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Expose custom object by delegating to its expose_to_registry method or checking execute_call."""
        # Handle class vs instance like other exposers
        target_item = item
        
        # If it's a class, instantiate it
        if inspect.isclass(item):
            try:
                # Check cache first
                if item not in self._instance_cache:
                    self._instance_cache[item] = item()  # Create and cache instance
                target_item = self._instance_cache[item]
            except Exception as e:
                return Result.error(f"Failed to instantiate class {item}: {str(e)}")
        
        # Check if object implements custom exposure workflow
        if hasattr(target_item, 'expose_to_registry'):
            try:
                # Delegate exposure to the custom object
                target_item.expose_to_registry(name, self)
                return Ok(True)
            except Exception as e:
                return Result.error(f"Custom exposure failed: {str(e)}")
        
        # Check if object at least implements execute_call (minimum requirement)
        elif hasattr(target_item, 'execute_call'):
            # Object can be executed but doesn't have custom exposure logic
            return Ok(True)
        
        else:
            return Result.error(f"Custom object {target_item} must implement execute_call() method")
    
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run custom object by delegating to its execute_call method."""
        # Handle class vs instance like other exposers
        target_item = item
        
        # If it's a class, get cached instance
        if inspect.isclass(item):
            if item in self._instance_cache:
                target_item = self._instance_cache[item]
            else:
                return Result.error(f"Class {item} not instantiated - call expose() first")
        
        if not hasattr(target_item, 'execute_call'):
            return Result.error(f"Custom object {target_item} must implement execute_call() method")
        
        try:
            # Check if execute_call is async and handle appropriately
            import asyncio
            if asyncio.iscoroutinefunction(target_item.execute_call):
                # It's async, run it with asyncio.run
                result = asyncio.run(target_item.execute_call(**kwargs))
            else:
                # It's sync, call directly
                result = target_item.execute_call(**kwargs)
            return Ok(result)
        except Exception as e:
            return Result.error(f"Custom execution failed: {str(e)}")
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run custom object async by delegating to its execute_call method."""
        # Handle class vs instance like other exposers
        target_item = item
        
        # If it's a class, get cached instance
        if inspect.isclass(item):
            if item in self._instance_cache:
                target_item = self._instance_cache[item]
            else:
                return Result.error(f"Class {item} not instantiated - call expose() first")
        
        if not hasattr(target_item, 'execute_call'):
            return Result.error(f"Custom object {target_item} must implement execute_call() method")
        
        try:
            # Check if execute_call is async
            import asyncio
            if asyncio.iscoroutinefunction(target_item.execute_call):
                result = await target_item.execute_call(**kwargs)
            else:
                result = target_item.execute_call(**kwargs)
            return Ok(result)
        except Exception as e:
            return Result.error(f"Custom execution failed: {str(e)}")
    
    def register_proxy_function(self, name: str, proxy_func):
        """Register a proxy function for custom objects to use."""
        # Custom objects can call this to register their proxy functions
        # This is used by AppProxy to register discovered remote functions
        pass