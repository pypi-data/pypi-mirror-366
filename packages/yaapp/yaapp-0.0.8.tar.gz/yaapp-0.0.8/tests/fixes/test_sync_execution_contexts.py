#!/usr/bin/env python3
"""
Demonstrate exactly when and how sync functions are executed in different contexts.
"""

import sys
import asyncio
import time
import threading
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp


def slow_sync_function(duration: float = 0.1) -> str:
    """A slow sync function to demonstrate execution context."""
    thread_name = threading.current_thread().name
    time.sleep(duration)
    return f"Executed on: {thread_name}"


def test_sync_context_execution():
    """Test sync function execution in sync context."""
    print("=== Sync Function in SYNC Context ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")  # Thread strategy
    
    func, exposer = app._registry["slow_sync_function"]
    
    # Call from sync context using exposer.run()
    print("Calling exposer.run() from sync context...")
    result = exposer.run(func, duration=0.05)
    
    if result.is_ok():
        execution_info = result.unwrap()
        print(f"Result: {execution_info}")
        
        # In sync context, even with "thread" strategy, it runs directly!
        main_thread = threading.current_thread().name
        if main_thread in execution_info:
            print("👉 RUNS DIRECTLY on main thread (no threading in sync context)")
        else:
            print("👉 RUNS ON THREAD POOL")
    
    return True


async def test_async_context_execution():
    """Test sync function execution in async context."""
    print("\n=== Sync Function in ASYNC Context ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, execution="thread")  # Thread strategy
    
    func, exposer = app._registry["slow_sync_function"]
    
    # Call from async context using exposer.run_async()
    print("Calling exposer.run_async() from async context...")
    result = await exposer.run_async(func, duration=0.05)
    
    if result.is_ok():
        execution_info = result.unwrap()
        print(f"Result: {execution_info}")
        
        # In async context with "thread" strategy, it should run on thread pool
        main_thread = threading.current_thread().name
        if "ThreadPoolExecutor" in execution_info:
            print("👉 RUNS ON THREAD POOL (non-blocking for event loop)")
        else:
            print(f"👉 RUNS DIRECTLY on {main_thread} (would block event loop!)")
    
    return True


async def test_direct_strategy_in_async():
    """Test direct strategy in async context."""
    print("\n=== Direct Strategy in ASYNC Context ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, name="direct_func", execution="direct")  # Direct strategy
    
    func, exposer = app._registry["direct_func"]
    
    print("Calling direct execution from async context...")
    result = await exposer.run_async(func, duration=0.05)
    
    if result.is_ok():
        execution_info = result.unwrap()
        print(f"Result: {execution_info}")
        
        main_thread = threading.current_thread().name
        if main_thread in execution_info:
            print("👉 RUNS DIRECTLY on main thread (BLOCKS event loop!)")
        else:
            print("👉 RUNS ON THREAD POOL")
    
    return True


def test_plain_function_call():
    """Test calling the function directly (outside YAPP)."""
    print("\n=== Plain Function Call (No YAPP) ===")
    
    # Direct function call - always runs on current thread
    thread_name = threading.current_thread().name
    result = slow_sync_function(0.05)
    
    print(f"Direct call result: {result}")
    print(f"👉 ALWAYS runs directly on current thread: {thread_name}")
    
    return True


async def test_event_loop_blocking():
    """Demonstrate event loop blocking with different strategies."""
    print("\n=== Event Loop Blocking Demonstration ===")
    
    app = Yaapp()
    app.expose(slow_sync_function, name="thread_func", execution="thread")
    app.expose(slow_sync_function, name="direct_func", execution="direct")
    
    thread_func, thread_exposer = app._registry["thread_func"]
    direct_func, direct_exposer = app._registry["direct_func"]
    
    print("Testing event loop responsiveness during execution...")
    
    # Test thread execution (should not block)
    print("\n1. Thread execution (should be non-blocking):")
    start_time = time.time()
    
    # Start slow function
    slow_task = asyncio.create_task(thread_exposer.run_async(thread_func, duration=0.2))
    
    # Test event loop responsiveness
    for i in range(3):
        loop_start = time.time()
        await asyncio.sleep(0.05)  # Should complete quickly if loop is responsive
        loop_time = time.time() - loop_start
        print(f"   Event loop sleep {i+1}: {loop_time:.3f}s (should be ~0.05s)")
    
    # Wait for slow task
    slow_result = await slow_task
    total_time = time.time() - start_time
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Slow task result: {slow_result.unwrap()}")
    
    # Test direct execution (will block)
    print("\n2. Direct execution (will block event loop):")
    start_time = time.time()
    
    # This will block the event loop
    direct_result = await direct_exposer.run_async(direct_func, duration=0.2)
    
    # Event loop was blocked, so this runs after
    loop_start = time.time()
    await asyncio.sleep(0.05)
    loop_time = time.time() - loop_start
    
    total_time = time.time() - start_time
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Post-execution sleep: {loop_time:.3f}s")
    print(f"   Direct result: {direct_result.unwrap()}")
    
    return True


def show_execution_summary():
    """Show summary of execution behavior."""
    print("\n" + "="*80)
    print("📋 YAPP Sync Function Execution Summary:")
    print("="*80)
    print()
    print("🔍 SYNC CONTEXT (exposer.run()):")
    print("   • Thread strategy → Runs DIRECTLY on current thread")
    print("   • Direct strategy → Runs DIRECTLY on current thread")  
    print("   • No threading in sync context (would be wasteful)")
    print()
    print("🔍 ASYNC CONTEXT (exposer.run_async()):")
    print("   • Thread strategy → Runs on THREAD POOL (non-blocking)")
    print("   • Direct strategy → Runs DIRECTLY on main thread (BLOCKS event loop)")
    print("   • Process strategy → Runs on PROCESS POOL (CPU-intensive)")
    print()
    print("🎯 KEY INSIGHT:")
    print("   The execution strategy only matters in ASYNC contexts!")
    print("   In sync contexts, functions always run directly.")
    print()
    print("⚡ ASYNC EVENT LOOP SAFETY:")
    print("   • Default 'thread' strategy prevents event loop blocking")
    print("   • Use 'direct' only for very fast functions (< 1ms)")
    print("   • Thread pool allows true concurrency in async context")
    print()
    print("🔥 BEFORE THIS FIX:")
    print("   • All sync functions blocked the event loop in async context")
    print("   • Used dangerous asyncio.run() creating new event loops")
    print()
    print("✅ AFTER THIS FIX:")
    print("   • Sync functions run safely in thread pool by default")
    print("   • Developer control over execution strategy")
    print("   • No more event loop blocking!")


async def main():
    """Run all execution context demonstrations."""
    print("🔍 YAPP Sync Function Execution Context Analysis")
    print("=" * 80)
    
    # Run tests
    test_plain_function_call()
    test_sync_context_execution()
    await test_async_context_execution()
    await test_direct_strategy_in_async()
    await test_event_loop_blocking()
    
    # Show summary
    show_execution_summary()


if __name__ == "__main__":
    asyncio.run(main())