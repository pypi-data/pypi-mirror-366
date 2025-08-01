#!/usr/bin/env python3
"""
Test different methods to detect if a function is async or sync.
"""

import asyncio
import inspect
import functools
from typing import Callable, Any


def sync_function():
    """A regular sync function."""
    return "sync result"


async def async_function():
    """An async function."""
    await asyncio.sleep(0.01)
    return "async result"


class TestClass:
    """Test class with both sync and async methods."""
    
    def sync_method(self):
        return "sync method result"
    
    async def async_method(self):
        await asyncio.sleep(0.01)
        return "async method result"


def test_detection_methods():
    """Test various methods to detect async vs sync functions."""
    
    print("=== Function Type Detection Methods ===\n")
    
    # Test subjects
    test_items = [
        ("sync_function", sync_function),
        ("async_function", async_function),
        ("sync_method", TestClass().sync_method),
        ("async_method", TestClass().async_method),
        ("lambda sync", lambda: "lambda result"),
        ("lambda async", lambda: asyncio.sleep(0)),  # This is NOT async!
    ]
    
    for name, func in test_items:
        print(f"Testing: {name}")
        print(f"  Type: {type(func)}")
        
        # Method 1: asyncio.iscoroutinefunction() - Most reliable
        is_async_asyncio = asyncio.iscoroutinefunction(func)
        print(f"  asyncio.iscoroutinefunction(): {is_async_asyncio}")
        
        # Method 2: inspect.iscoroutinefunction() - Same as asyncio version
        is_async_inspect = inspect.iscoroutinefunction(func)
        print(f"  inspect.iscoroutinefunction(): {is_async_inspect}")
        
        # Method 3: Check if calling it returns a coroutine (DANGEROUS - actually calls!)
        try:
            result = func()
            is_coroutine = inspect.iscoroutine(result)
            print(f"  Result is coroutine: {is_coroutine}")
            
            # Clean up coroutine to avoid warnings
            if is_coroutine:
                result.close()
        except Exception as e:
            print(f"  Result check failed: {e}")
        
        # Method 4: Check __code__.co_flags for CO_ITERABLE_COROUTINE
        if hasattr(func, '__code__'):
            co_flags = func.__code__.co_flags
            is_async_flags = bool(co_flags & inspect.CO_ITERABLE_COROUTINE)
            print(f"  CO_ITERABLE_COROUTINE flag: {is_async_flags}")
        else:
            print(f"  No __code__ attribute")
        
        # Method 5: Check if it's a coroutine type
        is_async_type = hasattr(func, '__await__')
        print(f"  Has __await__ method: {is_async_type}")
        
        print()


def test_advanced_detection():
    """Test more advanced async detection scenarios."""
    
    print("=== Advanced Detection Scenarios ===\n")
    
    # Wrapped functions
    import functools
    
    @functools.wraps(async_function)
    def wrapped_async():
        return async_function()
    
    @functools.wraps(sync_function) 
    async def async_wrapped_sync():
        return sync_function()
    
    # Partial functions
    import functools
    partial_sync = functools.partial(sync_function)
    partial_async = functools.partial(async_function)
    
    # Test cases
    advanced_cases = [
        ("wrapped_async", wrapped_async),
        ("async_wrapped_sync", async_wrapped_sync), 
        ("partial_sync", partial_sync),
        ("partial_async", partial_async),
        ("builtin_len", len),
        ("builtin_print", print),
    ]
    
    for name, func in advanced_cases:
        print(f"Testing: {name}")
        print(f"  Type: {type(func)}")
        print(f"  asyncio.iscoroutinefunction(): {asyncio.iscoroutinefunction(func)}")
        print(f"  inspect.iscoroutinefunction(): {inspect.iscoroutinefunction(func)}")
        print(f"  Callable: {callable(func)}")
        print()


def test_context_detection():
    """Test detection of async execution context."""
    
    print("=== Async Context Detection ===\n")
    
    def detect_async_context():
        """Detect if we're currently in an async context."""
        try:
            # Try to get current task - only works in async context
            task = asyncio.current_task()
            return True, f"In async context, task: {task.get_name() if task else 'unknown'}"
        except RuntimeError as e:
            return False, f"Not in async context: {e}"
    
    # Test from sync context
    is_async, message = detect_async_context()
    print(f"From sync context: {is_async} - {message}")
    
    # Test from async context
    async def test_from_async():
        is_async, message = detect_async_context()
        print(f"From async context: {is_async} - {message}")
    
    asyncio.run(test_from_async())
    
    print()


def safe_async_detector(func: Callable) -> dict:
    """
    Safe function to detect if a function is async without calling it.
    
    Returns:
        dict with detection results and metadata
    """
    result = {
        'function': func,
        'name': getattr(func, '__name__', str(func)),
        'type': type(func).__name__,
        'is_async': False,
        'is_callable': callable(func),
        'detection_method': 'unknown',
        'confidence': 'low'
    }
    
    # Primary detection using asyncio
    if asyncio.iscoroutinefunction(func):
        result.update({
            'is_async': True,
            'detection_method': 'asyncio.iscoroutinefunction',
            'confidence': 'high'
        })
        return result
    
    # Secondary detection using inspect  
    if inspect.iscoroutinefunction(func):
        result.update({
            'is_async': True,
            'detection_method': 'inspect.iscoroutinefunction', 
            'confidence': 'high'
        })
        return result
    
    # Check for partial functions
    if hasattr(func, 'func'):
        # It's a functools.partial, check the wrapped function
        wrapped_result = safe_async_detector(func.func)
        result.update({
            'is_async': wrapped_result['is_async'],
            'detection_method': f"partial({wrapped_result['detection_method']})",
            'confidence': wrapped_result['confidence']
        })
        return result
    
    # For callable objects, check if they have async __call__ (avoid recursion)
    if hasattr(func, '__call__') and func != func.__call__ and not isinstance(func, type):
        try:
            if asyncio.iscoroutinefunction(func.__call__):
                result.update({
                    'is_async': True,
                    'detection_method': 'callable.__call__.iscoroutinefunction',
                    'confidence': 'high'
                })
                return result
        except:
            pass
    
    # Default to sync
    result.update({
        'is_async': False,
        'detection_method': 'default_sync',
        'confidence': 'medium'
    })
    
    return result


def test_safe_detector():
    """Test the safe async detector."""
    
    print("=== Safe Async Detector Test ===\n")
    
    # Create test cases
    test_cases = [
        sync_function,
        async_function,
        TestClass().sync_method,
        TestClass().async_method,
        lambda: "sync lambda",
        len,
        print,
        functools.partial(sync_function),
        functools.partial(async_function),
    ]
    
    for func in test_cases:
        result = safe_async_detector(func)
        print(f"Function: {result['name']}")
        print(f"  Type: {result['type']}")
        print(f"  Is Async: {result['is_async']}")
        print(f"  Detection Method: {result['detection_method']}")
        print(f"  Confidence: {result['confidence']}")
        print()


async def test_proper_calling():
    """Test proper ways to call sync/async functions."""
    
    print("=== Proper Function Calling ===\n")
    
    async def smart_call(func, *args, **kwargs):
        """Smart caller that handles both sync and async functions properly."""
        detection = safe_async_detector(func)
        
        if detection['is_async']:
            print(f"Calling async function: {detection['name']}")
            result = await func(*args, **kwargs)
        else:
            print(f"Calling sync function: {detection['name']}")
            result = func(*args, **kwargs)
        
        return result
    
    # Test with both sync and async functions
    sync_result = await smart_call(sync_function)
    print(f"  Sync result: {sync_result}")
    
    async_result = await smart_call(async_function)
    print(f"  Async result: {async_result}")
    
    method_result = await smart_call(TestClass().sync_method)
    print(f"  Method result: {method_result}")
    
    async_method_result = await smart_call(TestClass().async_method)
    print(f"  Async method result: {async_method_result}")


def main():
    """Run all detection tests."""
    
    print("🔍 Python Async/Sync Function Detection Tests")
    print("=" * 60)
    
    test_detection_methods()
    test_advanced_detection()
    test_context_detection()
    test_safe_detector()
    
    # Run async test
    asyncio.run(test_proper_calling())
    
    print("=" * 60)
    print("🎉 Detection tests completed!")
    
    print("\n📋 Summary:")
    print("✅ asyncio.iscoroutinefunction() - Most reliable for detection")
    print("✅ inspect.iscoroutinefunction() - Same as asyncio version")
    print("✅ asyncio.current_task() - Detects if in async context")
    print("⚠️  Never call functions just to test if they return coroutines")
    print("⚠️  Handle partial functions and callable objects specially")
    print("⚠️  Always use proper await/call patterns based on detection")


if __name__ == "__main__":
    main()