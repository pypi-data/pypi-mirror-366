"""
Class exposer for class introspection and method exposure.
"""

import inspect
from typing import Any
from .base import BaseExposer
from ..result import Result, Ok


class ClassExposer(BaseExposer):
    """Exposer for classes - validates class can be instantiated and caches instances."""
    
    def __init__(self):
        """Initialize class exposer with instance cache."""
        self._instance_cache = {}  # Cache instances by class
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Validate a class can be exposed (stateless)."""
        if not inspect.isclass(item):
            return Result.error(f"ClassExposer cannot expose {type(item)}: {item}")
        
        try:
            # Validate the class has callable methods without instantiation
            has_methods = any(
                callable(getattr(item, attr_name)) and not isinstance(getattr(item, attr_name), type)
                for attr_name in dir(item)
                if not attr_name.startswith('_')
            )
            
            if not has_methods:
                return Result.error(f"Class {item} has no public methods to expose")
            
            return Ok(True)
        except Exception as e:
            return Result.error(f"Failed to validate class {item}: {str(e)}")
    
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run method using cached instance."""
        # If it's a class, get or create cached instance
        if inspect.isclass(item):
            try:
                # Check cache first
                if item not in self._instance_cache:
                    self._instance_cache[item] = item()  # Create and cache instance
                
                instance = self._instance_cache[item]
                return Ok(instance)
            except Exception as e:
                return Result.error(f"Failed to instantiate class {item}: {str(e)}")
        
        # If it's an object method, delegate to ObjectExposer
        from .object import ObjectExposer
        object_exposer = ObjectExposer()
        return object_exposer.run(item, **kwargs)
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run async method using cached instance."""
        # If it's a class, get or create cached instance
        if inspect.isclass(item):
            try:
                # Check cache first
                if item not in self._instance_cache:
                    self._instance_cache[item] = item()  # Create and cache instance
                
                instance = self._instance_cache[item]
                return Ok(instance)
            except Exception as e:
                return Result.error(f"Failed to instantiate class {item}: {str(e)}")
        
        # If it's an object method, delegate to ObjectExposer
        from .object import ObjectExposer
        object_exposer = ObjectExposer()
        return await object_exposer.run_async(item, **kwargs)