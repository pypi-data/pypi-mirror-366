"""
Async compatibility utilities for YAAPP framework.
Provides dual interface pattern for sync/async function execution.
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Coroutine, Union
from .result import Result, Ok


def async_compatible(func: Callable) -> Callable:
    """
    Decorator that makes any function callable from both sync and async contexts.
    
    For async functions:
    - Adds a .sync attribute that runs the function with asyncio.run()
    - Original function remains async
    
    For sync functions:
    - Adds an .async attribute that returns the result directly
    - Original function remains sync
    
    Raises:
        ValueError: If function type doesn't support async compatibility
    """
    # Handle bound methods - they need wrapper approach
    if hasattr(func, '__self__'):
        raise ValueError(f"Bound method {func} cannot be made async compatible. Use wrapper approach.")
    
    # Handle built-in functions and other non-modifiable types
    if hasattr(func, '__module__') and func.__module__ == 'builtins':
        raise ValueError(f"Built-in function {func} cannot be made async compatible. Use wrapper approach.")
    
    if asyncio.iscoroutinefunction(func):
        # It's already async
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        
        # Attach sync wrapper to async function
        try:
            func.sync = sync_wrapper
            func.is_async = True
        except AttributeError as e:
            print(f"Warning: Cannot add sync compatibility to {type(func).__name__}: {e}")
            return func
        
        return func
    else:
        # It's sync - create async wrapper that uses thread pool for non-blocking execution
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Use thread pool to prevent event loop blocking
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))
        
        # Attach async wrapper to sync function  
        try:
            func.async_version = async_wrapper
            func.is_async = False
        except AttributeError as e:
            print(f"Warning: Cannot add async compatibility to {type(func).__name__}: {e}")
            return func
        
        return func


def smart_call(func: Callable, *args, **kwargs) -> Any:
    """
    Smart function caller that detects execution context and calls appropriately.
    
    Args:
        func: Function to call (should have been processed by async_compatible)
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result
    """
    if asyncio.iscoroutinefunction(func):
        # It's an async function
        try:
            # Check if we're in an async context
            asyncio.current_task()
            # We're in async context but this is not awaitable
            print("Warning: Cannot call async function directly from smart_call in async context. Use await.")
            return None
        except RuntimeError:
            # Not in async context, use sync wrapper
            if hasattr(func, 'sync'):
                return func.sync(*args, **kwargs)
            else:
                return asyncio.run(func(*args, **kwargs))
    else:
        # It's a sync function, call directly
        return func(*args, **kwargs)


async def smart_call_async(func: Callable, *args, **kwargs) -> Any:
    """
    Smart async function caller that handles both sync and async functions.
    Uses thread pool for sync functions to prevent event loop blocking.
    
    Args:
        func: Function to call
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result
    """
    if asyncio.iscoroutinefunction(func):
        # It's async, await it
        return await func(*args, **kwargs)
    else:
        # It's sync, run in thread pool to prevent event loop blocking
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))


def detect_execution_context() -> str:
    """
    Detect current execution context.
    
    Returns:
        'async' if in async context, 'sync' otherwise
    """
    try:
        asyncio.current_task()
        return 'async'
    except RuntimeError:
        return 'sync'


async def result_from_async(coro: Coroutine) -> Result:
    """
    Create Result object from async coroutine execution.
    
    Args:
        coro: Coroutine to execute
        
    Returns:
        Result object with success or error
    """
    try:
        value = await coro
        return Ok(value)
    except Exception as e:
        return Result.error(str(e))


def result_from_sync(func: Callable, *args, **kwargs) -> Result:
    """
    Create Result object from sync function execution.
    
    Args:
        func: Function to execute
        *args, **kwargs: Arguments to pass
        
    Returns:
        Result object with success or error
    """
    try:
        value = func(*args, **kwargs)
        return Ok(value)
    except Exception as e:
        return Result.error(str(e))