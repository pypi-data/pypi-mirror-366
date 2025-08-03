"""
FIXED Class exposer with uniform interface support.
"""

import inspect
from typing import Any, Optional
from .base import BaseExposer
from ..result import Result, Ok, Err


class ClassExposer(BaseExposer):
    """Exposer for classes with uniform interface support."""
    
    def __init__(self):
        """Initialize class exposer with instance cache."""
        self._instance_cache = {}  # Cache instances by class
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Validate a class can be exposed (stateless)."""
        if not inspect.isclass(item):
            return Err(f"ClassExposer cannot expose {type(item)}: {item}")
        
        try:
            # Validate the class has callable methods without instantiation
            has_methods = any(
                callable(getattr(item, attr_name)) and not isinstance(getattr(item, attr_name), type)
                for attr_name in dir(item)
                if not attr_name.startswith('_')
            )
            
            if not has_methods:
                return Err(f"Class {item} has no public methods to expose")
            
            return Ok(True)
        except Exception as e:
            return Err(f"Failed to validate class {item}: {str(e)}")
    
    def run(self, item: Any, function_name: Optional[str] = None, **kwargs) -> Result[Any]:
        """Run method using cached instance with uniform interface."""
        # If it's a class, get or create cached instance
        if inspect.isclass(item):
            try:
                # Check cache first
                if item not in self._instance_cache:
                    self._instance_cache[item] = item()  # Create and cache instance
                
                instance = self._instance_cache[item]
                
                # If function_name provided, call the method
                if function_name:
                    if hasattr(instance, function_name):
                        method = getattr(instance, function_name)
                        if callable(method):
                            result = method(**kwargs)
                            return Ok(result)
                        else:
                            return Err(f"Attribute '{function_name}' is not callable")
                    else:
                        return Err(f"Method '{function_name}' not found on {type(instance).__name__}")
                else:
                    # No function_name, return the instance
                    return Ok(instance)
                    
            except Exception as e:
                return Err(f"Failed to instantiate or call method on class {item}: {str(e)}")
        
        # If it's already an instance, handle method call
        elif function_name:
            if hasattr(item, function_name):
                method = getattr(item, function_name)
                if callable(method):
                    try:
                        result = method(**kwargs)
                        return Ok(result)
                    except Exception as e:
                        return Err(f"Method call failed: {str(e)}")
                else:
                    return Err(f"Attribute '{function_name}' is not callable")
            else:
                return Err(f"Method '{function_name}' not found on {type(item).__name__}")
        else:
            # No function_name, try to call the object directly
            try:
                result = item(**kwargs)
                return Ok(result)
            except Exception as e:
                return Err(f"Direct call failed: {str(e)}")
    
    async def run_async(self, item: Any, function_name: Optional[str] = None, **kwargs) -> Result[Any]:
        """Run async method using cached instance with uniform interface."""
        # Use the base class implementation which handles async properly
        # But first ensure we have an instance if item is a class
        if inspect.isclass(item):
            try:
                # Check cache first
                if item not in self._instance_cache:
                    self._instance_cache[item] = item()  # Create and cache instance
                
                instance = self._instance_cache[item]
                
                # Now use base class async handling with the instance
                return await super().run_async(instance, function_name, **kwargs)
                
            except Exception as e:
                return Err(f"Failed to instantiate class {item}: {str(e)}")
        else:
            # Use base class async handling for instances
            return await super().run_async(item, function_name, **kwargs)