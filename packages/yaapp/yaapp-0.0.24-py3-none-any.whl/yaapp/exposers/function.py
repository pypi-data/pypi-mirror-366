"""
Function exposer for regular functions with async/sync support.
"""

import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Any
from .base import BaseExposer
from ..result import Result, Ok
from ..async_compat import async_compatible, smart_call
from ..execution_strategy import (
    get_execution_hint, 
    should_use_thread_pool, 
    should_use_process_pool,
    ExecutionStrategy
)


class FunctionExposer(BaseExposer):
    """Exposer for regular functions - supports both sync and async functions with execution strategies."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize function exposer.
        
        Args:
            max_workers: Maximum number of thread pool workers
        """
        super().__init__()
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._process_pool = None  # Created on-demand
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Validate and process a function for exposure (stateless)."""
        if not (callable(item) and not inspect.isclass(item)):
            return Result.error(f"FunctionExposer cannot expose {type(item)}: {item}")
        
        try:
            # Just validate - don't store any state
            # Check if it's a bound method - these are handled as-is
            if hasattr(item, '__self__'):
                # It's a bound method, validate it can be called
                if not callable(item):
                    return Result.error(f"Bound method {item} is not callable")
            else:
                # Regular function - validate it can be made async compatible
                try:
                    # Test if async_compatible can be applied (but don't store result)
                    async_compatible(item)
                except Exception as e:
                    return Result.error(f"Function {item} cannot be made async compatible: {str(e)}")
            
            return Ok(True)
        except Exception as e:
            return Result.error(f"Failed to validate function: {str(e)}")
    
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run the function with given arguments (sync context)."""
        if not callable(item):
            return Result.error(f"Cannot run non-callable item: {item}")
        
        try:
            # Handle different function types dynamically
            if asyncio.iscoroutinefunction(item):
                # Async function (including bound async methods) - run with asyncio.run
                if hasattr(item, 'sync'):
                    result = item.sync(**kwargs)
                else:
                    # Create coroutine and run it
                    coro = item(**kwargs)
                    result = asyncio.run(coro)
            elif hasattr(item, '__self__'):
                # Bound method (sync) - call directly
                result = item(**kwargs)
            else:
                # Regular function - apply async compatibility on-demand and call
                try:
                    compatible_func = async_compatible(item)
                    result = compatible_func(**kwargs)
                except (ImportError, TypeError, AttributeError):
                    # If async_compatible fails due to import or type issues, call function directly
                    result = item(**kwargs)
            
            return Ok(result)
        except Exception as e:
            return Result.error(f"Function execution failed: {str(e)}")
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run the function with given arguments (async context) using execution strategies."""
        if not callable(item):
            return Result.error(f"Cannot run non-callable item: {item}")
        
        try:
            # Handle async functions directly
            if asyncio.iscoroutinefunction(item):
                result = await item(**kwargs)
                return Ok(result)
            
            # For sync functions, check execution strategy
            execution_hint = get_execution_hint(item)
            
            # Bound methods always execute directly to avoid serialization issues
            if hasattr(item, '__self__'):
                result = item(**kwargs)
                return Ok(result)
            
            # Apply execution strategy for sync functions
            if should_use_process_pool(item, execution_hint):
                result = await self._run_in_process_pool(item, **kwargs)
            elif should_use_thread_pool(item, execution_hint):
                result = await self._run_in_thread_pool(item, **kwargs)
            else:
                # Direct execution - blocks event loop but fastest for quick functions
                result = item(**kwargs)
            
            return Ok(result)
        except Exception as e:
            return Result.error(f"Function execution failed: {str(e)}")
    
    async def _run_in_thread_pool(self, func: Any, **kwargs) -> Any:
        """Execute function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._thread_pool, lambda: func(**kwargs))
    
    async def _run_in_process_pool(self, func: Any, **kwargs) -> Any:
        """Execute function in process pool."""
        if self._process_pool is None:
            self._process_pool = ProcessPoolExecutor(max_workers=2)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._process_pool, lambda: func(**kwargs))