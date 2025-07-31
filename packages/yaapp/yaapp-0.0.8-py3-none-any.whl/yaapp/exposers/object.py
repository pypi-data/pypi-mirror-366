"""
Object exposer for object instances.
"""

import inspect
from typing import Any
from .base import BaseExposer
from .function import FunctionExposer
from ..result import Result, Ok


class ObjectExposer(BaseExposer):
    """Exposer for object instances - validates objects have callable methods."""
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Validate object can be exposed (stateless)."""
        if not (hasattr(item, '__class__') and not callable(item) and not inspect.isclass(item)):
            return Result.error(f"ObjectExposer cannot expose {type(item)}: {item}")
        
        try:
            # Validate object has at least one public callable method
            has_methods = False
            function_exposer = FunctionExposer()
            
            for method_name in dir(item):
                if not method_name.startswith('_'):
                    method = getattr(item, method_name)
                    if callable(method):
                        # Test that method can be exposed (but don't store it)
                        result = function_exposer.expose(method, f"{name}.{method_name}", custom)
                        if result.is_ok():
                            has_methods = True
            
            if not has_methods:
                return Result.error(f"Object {item} has no exposable public methods")
            
            return Ok(True)
        except Exception as e:
            return Result.error(f"Failed to validate object methods: {str(e)}")
    
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run object method using FunctionExposer logic."""
        if not callable(item):
            return Result.error(f"Cannot run non-callable item: {item}")
        
        # Delegate to FunctionExposer for consistent behavior
        function_exposer = FunctionExposer()
        return function_exposer.run(item, **kwargs)
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run object method async using FunctionExposer logic."""
        if not callable(item):
            return Result.error(f"Cannot run non-callable item: {item}")
        
        # Delegate to FunctionExposer for consistent behavior
        function_exposer = FunctionExposer()
        return await function_exposer.run_async(item, **kwargs)