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
        
        # For classes, don't instantiate here - let the framework do it with config
        if inspect.isclass(item):
            # Just validate that the class has the required methods
            if hasattr(item, 'expose_to_registry') or hasattr(item, 'execute_call'):
                return Ok(True)
            else:
                return Result.error(f"Custom class {item} must implement expose_to_registry() or execute_call() method")
        
        # For instances, handle normally
        target_item = item
        
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
        
        # If it's a class, it should have been instantiated by the framework already
        if inspect.isclass(item):
            return Result.error(f"Class {item} should have been instantiated by framework before execution")
        
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
        
        # If it's a class, it should have been instantiated by the framework already
        if inspect.isclass(item):
            return Result.error(f"Class {item} should have been instantiated by framework before execution")
        
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
        # Import yaapp to register the proxy function
        from .. import yaapp
        
        # Register the proxy function with yaapp using the function exposer
        try:
            yaapp.expose(proxy_func, name)
        except Exception as e:
            print(f"   ❌ Failed to register {name}: {e}")