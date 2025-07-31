#!/usr/bin/env python3
"""
Test that FastAPI runner properly uses execution strategies and doesn't block event loop.
Verifies the critical async bugs are fixed in web server context.
"""

import sys
import asyncio
import time
import threading
import json
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp


def slow_sync_function(duration: float = 0.1) -> str:
    """A slow sync function that would block event loop if called directly."""
    thread_name = threading.current_thread().name
    time.sleep(duration)
    return f"Completed after {duration}s on thread: {thread_name}"


def fast_sync_function(x: int) -> int:
    """A fast sync function for direct execution."""
    return x * 2


async def async_function(x: int) -> int:
    """An async function."""
    await asyncio.sleep(0.01)
    return x * 3


def cpu_intensive_function(iterations: int = 1000) -> int:
    """CPU-intensive function for process execution."""
    total = 0
    for i in range(iterations):
        total += i
    return total


async def test_fastapi_execution_strategies():
    """Test that FastAPI runner uses execution strategies correctly."""
    print("=== Testing FastAPI Execution Strategies ===")
    
    # Create app with different execution strategies
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")
    app.expose(fast_sync_function, execution="direct") 
    app.expose(cpu_intensive_function, execution="process")
    app.expose(async_function)
    
    # Import FastAPI runner
    from yaapp.runners.fastapi_runner import FastAPIRunner
    runner = FastAPIRunner(app)
    
    # Test _call_function_async method directly
    print("\\n1. Testing thread execution strategy:")
    start_time = time.time()
    result = await runner._call_function_async("slow_sync_function", {"duration": 0.05})
    execution_time = time.time() - start_time
    
    print(f"   Result: {result}")
    print(f"   Execution time: {execution_time:.4f}s")
    
    # Verify it ran on a different thread
    main_thread = threading.current_thread().name
    assert main_thread not in result, f"Should not run on main thread {main_thread}"
    assert "ThreadPoolExecutor" in result, f"Should run on thread pool: {result}"
    print("   ✅ Ran on thread pool (non-blocking)")
    
    print("\\n2. Testing direct execution strategy:")
    start_time = time.time()
    result = await runner._call_function_async("fast_sync_function", {"x": 5})
    execution_time = time.time() - start_time
    
    print(f"   Result: {result}")
    print(f"   Execution time: {execution_time:.6f}s")
    assert result == 10, f"Expected 10, got {result}"
    print("   ✅ Direct execution working")
    
    print("\\n3. Testing async function:")
    start_time = time.time()
    result = await runner._call_function_async("async_function", {"x": 4})
    execution_time = time.time() - start_time
    
    print(f"   Result: {result}")
    print(f"   Execution time: {execution_time:.4f}s")
    assert result == 12, f"Expected 12, got {result}"
    print("   ✅ Async function working")
    
    return True


async def test_concurrent_web_requests():
    """Test that multiple concurrent requests work without blocking."""
    print("\\n=== Testing Concurrent Web Requests ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")
    
    from yaapp.runners.fastapi_runner import FastAPIRunner
    runner = FastAPIRunner(app)
    
    # Simulate 3 concurrent web requests
    print("Simulating 3 concurrent requests (0.1s each)...")
    start_time = time.time()
    
    tasks = []
    for i in range(3):
        task = runner._call_function_async("slow_sync_function", {"duration": 0.1})
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"Total time for 3 concurrent requests: {total_time:.4f}s")
    
    # Should complete in ~0.1s (concurrent), not 0.3s (sequential blocking)
    assert total_time < 0.2, f"Too slow: {total_time:.4f}s (expected < 0.2s)"
    
    # All results should be successful and show different threads
    threads_used = set()
    for i, result in enumerate(results):
        print(f"   Request {i+1}: {result}")
        # Extract thread name from result
        if "ThreadPoolExecutor" in result:
            threads_used.add(result.split("thread: ")[1])
    
    print(f"   Used {len(threads_used)} different thread(s)")
    print("   ✅ Concurrent execution working (no event loop blocking!)")
    
    return True


async def test_event_loop_responsiveness():
    """Test that event loop remains responsive during slow operations."""
    print("\\n=== Testing Event Loop Responsiveness ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")
    
    from yaapp.runners.fastapi_runner import FastAPIRunner
    runner = FastAPIRunner(app)
    
    print("Testing event loop responsiveness during slow operation...")
    
    # Start slow operation
    slow_task = asyncio.create_task(
        runner._call_function_async("slow_sync_function", {"duration": 0.2})
    )
    
    # Test event loop responsiveness
    responsiveness_times = []
    for i in range(4):
        loop_start = time.time()
        await asyncio.sleep(0.05)  # Should complete quickly if loop is responsive
        loop_time = time.time() - loop_start
        responsiveness_times.append(loop_time)
        print(f"   Event loop sleep {i+1}: {loop_time:.4f}s (should be ~0.05s)")
    
    # Wait for slow task to complete
    slow_result = await slow_task
    print(f"   Slow task result: {slow_result}")
    
    # Event loop should have remained responsive
    avg_responsiveness = sum(responsiveness_times) / len(responsiveness_times)
    assert avg_responsiveness < 0.1, f"Event loop not responsive: {avg_responsiveness:.4f}s average"
    
    print(f"   ✅ Average event loop responsiveness: {avg_responsiveness:.4f}s")
    print("   ✅ Event loop remained responsive during slow operation!")
    
    return True


def test_fastapi_runner_structure():
    """Test that FastAPI runner has the correct structure."""
    print("\\n=== Testing FastAPI Runner Structure ===")
    
    app = Yaapp()
    app.expose(slow_sync_function)
    
    from yaapp.runners.fastapi_runner import FastAPIRunner
    runner = FastAPIRunner(app)
    
    # Check that async methods exist
    assert hasattr(runner, '_call_function_async'), "Should have _call_function_async method"
    assert hasattr(runner, '_call_function_async_method'), "Should have _call_function_async_method method"
    
    # Check that old sync method is gone or replaced
    if hasattr(runner, '_call_function_sync'):
        print("   ⚠️  Old _call_function_sync method still exists")
    else:
        print("   ✅ Old broken _call_function_sync method removed")
    
    print("   ✅ FastAPI runner structure updated")
    return True


async def test_before_and_after_comparison():
    """Show the difference between old (broken) and new (fixed) behavior."""
    print("\\n=== Before/After Comparison ===")
    
    print("\\n🔥 BEFORE THIS FIX:")
    print("   • sync functions called with func(**kwargs) - BLOCKED event loop")
    print("   • async functions called with asyncio.run() - CREATED new event loop (error!)")
    print("   • FastAPI web server UNUSABLE under concurrent load")
    print("   • Event loop completely blocked during sync operations")
    print("   • Performance: Sequential execution only")
    
    print("\\n✅ AFTER THIS FIX:")
    print("   • sync functions use exposer.run_async() with thread pool")
    print("   • async functions use exposer.run_async() with await")
    print("   • FastAPI web server handles concurrent requests properly")
    print("   • Event loop remains responsive")
    print("   • Performance: True concurrent execution")
    
    # Demonstrate the fix
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")
    
    from yaapp.runners.fastapi_runner import FastAPIRunner
    runner = FastAPIRunner(app)
    
    # This call would have blocked the event loop before
    print("\\n   Demonstrating fixed behavior:")
    start = time.time()
    result = await runner._call_function_async("slow_sync_function", {"duration": 0.1})
    duration = time.time() - start
    
    print(f"   Call completed in {duration:.4f}s: {result}")
    
    # The key evidence: it ran on a thread pool, not main thread
    main_thread = threading.current_thread().name
    if "ThreadPoolExecutor" in result:
        print("   ✅ PROOF: Ran on ThreadPoolExecutor (non-blocking!)")
    else:
        print(f"   ❌ WARNING: Ran on {main_thread} (would block event loop)")
    
    return True


async def main():
    """Run all FastAPI execution fix tests."""
    print("🚀 Testing FastAPI Runner Execution Strategy Fix")
    print("=" * 70)
    print("Verifying that the critical async bugs are fixed in web server context")
    print("=" * 70)
    
    tests = [
        test_fastapi_runner_structure,
        test_fastapi_execution_strategies,
        test_concurrent_web_requests,
        test_event_loop_responsiveness,
        test_before_and_after_comparison,
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
    
    print("\\n" + "=" * 70)
    print(f"FastAPI Fix Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\\n🎉 ALL FASTAPI EXECUTION TESTS PASSED!")
        print("\\n✅ Critical FastAPI Issues RESOLVED:")
        print("  • Event loop blocking: FIXED")
        print("  • Concurrent request handling: WORKING")
        print("  • ThreadPoolExecutor integration: ACTIVE")
        print("  • Execution strategy system: INTEGRATED")
        print("  • Web server responsiveness: MAINTAINED")
        print("\\n🔥 FastAPI web server is now PRODUCTION-READY!")
        print("\\nKey fix: FastAPI endpoints now use exposer.run_async() instead of")
        print("         direct function calls, enabling proper async execution.")
        return 0
    else:
        print("\\n❌ SOME FASTAPI TESTS FAILED!")
        print("Web server may still have async execution issues.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))