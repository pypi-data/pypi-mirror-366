"""
FIXED Base exposer class with uniform interface.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional
from ..result import Result, Ok, Err


class BaseExposer(ABC):
    """Abstract base class for all exposers with uniform interface."""
    
    @abstractmethod
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Expose the item with the given name and workflow type."""
        pass
    
    @abstractmethod
    def run(self, item: Any, function_name: Optional[str] = None, **kwargs) -> Result[Any]:
        """Run the exposed item with given arguments (sync context).
        
        Args:
            item: The object to execute
            function_name: Optional method name for class instances
            **kwargs: Arguments to pass to the function/method
        """
        pass
    
    async def run_async(self, item: Any, function_name: Optional[str] = None, **kwargs) -> Result[Any]:
        """Run the exposed item with given arguments (async context).
        
        Args:
            item: The object to execute
            function_name: Optional method name for class instances
            **kwargs: Arguments to pass to the function/method
        """
        # Default implementation - subclasses can override for optimization
        try:
            # If function_name is provided, this is a method call
            if function_name:
                # Handle different object types
                if hasattr(item, 'execute_call'):
                    # CustomExposer object
                    if asyncio.iscoroutinefunction(item.execute_call):
                        result = await item.execute_call(function_name, **kwargs)
                    else:
                        result = item.execute_call(function_name, **kwargs)
                elif hasattr(item, function_name):
                    # Object with the method
                    method = getattr(item, function_name)
                    if callable(method):
                        if asyncio.iscoroutinefunction(method):
                            result = await method(**kwargs)
                        else:
                            result = method(**kwargs)
                    else:
                        return Err(f"Attribute '{function_name}' is not callable")
                else:
                    return Err(f"Method '{function_name}' not found on {type(item).__name__}")
            else:
                # Direct object call
                if asyncio.iscoroutinefunction(item):
                    result = await item(**kwargs)
                else:
                    result = item(**kwargs)
            
            return Ok(result)
        except Exception as e:
            return Err(str(e))