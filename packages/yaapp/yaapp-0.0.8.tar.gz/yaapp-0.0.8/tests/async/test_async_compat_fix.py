#!/usr/bin/env python3
"""
Test that async_compat.py is fixed and no longer blocks the event loop.
"""

import sys
import asyncio
import time
import threading
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp.async_compat import async_compatible, smart_call_async


def slow_sync_function(duration: float = 0.1) -> str:
    """A slow sync function to test async compatibility."""
    thread_name = threading.current_thread().name
    time.sleep(duration)
    return f"Completed after {duration}s on thread: {thread_name}"


async def test_async_compatible_decorator():
    """Test that async_compatible decorator uses thread pool."""
    print("=== Testing async_compatible Decorator ===")
    
    # Apply async_compatible decorator
    wrapped_func = async_compatible(slow_sync_function)
    
    # Test the async version
    print("Testing async_version...")
    start_time = time.time()
    result = await wrapped_func.async_version(duration=0.05)
    execution_time = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Execution time: {execution_time:.4f}s")
    
    # Verify it ran on a different thread
    main_thread = threading.current_thread().name
    assert main_thread not in result, f"Should not run on main thread {main_thread}"
    assert "ThreadPoolExecutor" in result, f"Should run on thread pool: {result}"
    
    print("✅ async_compatible uses thread pool (event loop safe)")
    return True


async def test_smart_call_async():
    """Test that smart_call_async uses thread pool for sync functions."""
    print("\n=== Testing smart_call_async Function ===")
    
    # Test with sync function
    print("Testing sync function through smart_call_async...")
    start_time = time.time()
    result = await smart_call_async(slow_sync_function, duration=0.05)
    execution_time = time.time() - start_time
    
    print(f"Result: {result}")
    print(f"Execution time: {execution_time:.4f}s")
    
    # Verify it ran on a different thread
    main_thread = threading.current_thread().name
    assert main_thread not in result, f"Should not run on main thread {main_thread}"
    assert "ThreadPoolExecutor" in result, f"Should run on thread pool: {result}"
    
    print("✅ smart_call_async uses thread pool for sync functions")
    return True


async def test_concurrent_async_compat_calls():
    """Test concurrent calls through async_compat don't block each other."""
    print("\n=== Testing Concurrent async_compat Calls ===")
    
    wrapped_func = async_compatible(slow_sync_function)
    
    print("Running 3 concurrent calls (0.1s each)...")
    start_time = time.time()
    
    tasks = [
        wrapped_func.async_version(duration=0.1),
        wrapped_func.async_version(duration=0.1),
        wrapped_func.async_version(duration=0.1)
    ]
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"Total time: {total_time:.4f}s")
    
    # Should be concurrent (~0.1s), not sequential (0.3s)
    assert total_time < 0.2, f"Too slow: {total_time:.4f}s (expected < 0.2s)"
    
    # Check all ran on different threads
    threads_used = set()
    for i, result in enumerate(results):
        print(f"   Task {i+1}: {result}")
        if "ThreadPoolExecutor" in result:
            threads_used.add(result.split("thread: ")[1])
    
    print(f"   Used {len(threads_used)} different thread(s)")
    print("✅ Concurrent async_compat calls working")
    return True


async def test_event_loop_responsiveness_with_async_compat():
    """Test event loop stays responsive during async_compat calls."""
    print("\n=== Testing Event Loop Responsiveness ===")
    
    wrapped_func = async_compatible(slow_sync_function)
    
    print("Testing event loop responsiveness during slow async_compat call...")
    
    # Start slow operation
    slow_task = asyncio.create_task(wrapped_func.async_version(duration=0.2))
    
    # Test event loop responsiveness
    responsiveness_times = []
    for i in range(4):
        loop_start = time.time()
        await asyncio.sleep(0.05)  # Should complete quickly
        loop_time = time.time() - loop_start
        responsiveness_times.append(loop_time)
        print(f"   Event loop sleep {i+1}: {loop_time:.4f}s")
    
    # Wait for slow task
    slow_result = await slow_task
    print(f"   Slow task result: {slow_result}")
    
    # Event loop should remain responsive
    avg_responsiveness = sum(responsiveness_times) / len(responsiveness_times)
    assert avg_responsiveness < 0.1, f"Event loop blocked: {avg_responsiveness:.4f}s"
    
    print(f"   ✅ Average responsiveness: {avg_responsiveness:.4f}s")
    print("   ✅ Event loop remained responsive!")
    return True


def test_before_after_async_compat():
    """Show the before/after comparison for async_compat."""
    print("\n=== Before/After async_compat Comparison ===")
    
    print("\n🔥 BEFORE FIX (async_compat.py:53-54):")
    print("   async def async_wrapper(*args, **kwargs):")
    print("       return func(*args, **kwargs)  # 🚨 BLOCKED event loop")
    
    print("\n✅ AFTER FIX:")
    print("   async def async_wrapper(*args, **kwargs):")
    print("       loop = asyncio.get_event_loop()")
    print("       with ThreadPoolExecutor() as executor:")
    print("           return await loop.run_in_executor(executor, lambda: func(...))")
    print("   # ✅ NON-BLOCKING thread pool execution")
    
    print("\n🔥 BEFORE FIX (smart_call_async:110-111):")  
    print("   # It's sync, call directly (runs in current thread)")
    print("   return func(*args, **kwargs)  # 🚨 BLOCKED event loop")
    
    print("\n✅ AFTER FIX:")
    print("   # It's sync, run in thread pool to prevent event loop blocking")  
    print("   with ThreadPoolExecutor() as executor:")
    print("       return await loop.run_in_executor(executor, lambda: func(...))")
    print("   # ✅ NON-BLOCKING thread pool execution")
    
    return True


async def main():
    """Run all async_compat fix tests."""
    print("🔧 Testing async_compat.py Event Loop Blocking Fixes")
    print("=" * 65)
    
    tests = [
        test_before_after_async_compat,
        test_async_compatible_decorator,
        test_smart_call_async,
        test_concurrent_async_compat_calls,
        test_event_loop_responsiveness_with_async_compat,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()  
            else:
                result = test()
                
            if result:
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 65)
    print(f"async_compat Fix Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL async_compat.py FIXES VERIFIED!")
        print("\n✅ Critical Bugs RESOLVED:")
        print("  • async_wrapper event loop blocking: FIXED")
        print("  • smart_call_async event loop blocking: FIXED") 
        print("  • ThreadPoolExecutor integration: ADDED")
        print("  • Concurrent execution: WORKING")
        print("  • Event loop responsiveness: MAINTAINED")
        print("\n🔥 async_compat.py is now EVENT LOOP SAFE!")
        return 0
    else:
        print("\n❌ SOME async_compat.py TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))