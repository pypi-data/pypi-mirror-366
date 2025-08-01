"""
Base exposer class for the YAPP exposer system.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any
from ..result import Result, Ok
from ..async_compat import async_compatible, smart_call, smart_call_async


class BaseExposer(ABC):
    """Abstract base class for all exposers."""
    
    @abstractmethod
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Expose the item with the given name and workflow type."""
        pass
    
    @abstractmethod
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run the exposed item with given arguments (sync context)."""
        pass
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run the exposed item with given arguments (async context)."""
        # Default implementation - subclasses can override for optimization
        try:
            if asyncio.iscoroutinefunction(item):
                result = await item(**kwargs)
            else:
                result = item(**kwargs)
            return Ok(result)
        except Exception as e:
            return Result.error(str(e))