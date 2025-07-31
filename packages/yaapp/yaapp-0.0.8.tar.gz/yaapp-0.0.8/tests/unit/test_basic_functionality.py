#!/usr/bin/env python3
"""
Test basic YAPP functionality to ensure execution parameter changes didn't break core features.
"""

import sys
import asyncio
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp


def test_basic_function_exposure():
    """Test that basic function exposure still works."""
    print("=== Testing Basic Function Exposure ===")
    
    app = Yaapp()
    
    def test_func(x: int) -> int:
        return x * 2
    
    # Test basic exposure (should use default thread execution)
    app.expose(test_func)
    
    registry = app.get_registry_items()
    assert "test_func" in registry, "Function not in registry"
    
    # Test that function can be retrieved and has execution hint
    func, exposer = app._registry["test_func"]
    assert hasattr(func, '__execution_hint__'), "Function should have execution hint"
    
    print("✅ Basic function exposure working")
    return True


def test_class_exposure():
    """Test that class exposure still works."""
    print("\n=== Testing Class Exposure ===")
    
    app = Yaapp()
    
    class TestClass:
        def method(self, x: int) -> int:
            return x + 1
    
    app.expose(TestClass)
    
    registry = app.get_registry_items()
    assert "TestClass" in registry, "Class not in registry"
    
    print("✅ Class exposure working")
    return True


async def test_async_function_execution():
    """Test that async functions still work correctly."""
    print("\n=== Testing Async Function Execution ===")
    
    app = Yaapp()
    
    async def async_func(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 3
    
    app.expose(async_func)
    
    # Get function from registry
    func, exposer = app._registry["async_func"]
    
    # Test async execution
    result = await exposer.run_async(func, x=5)
    
    assert result.is_ok(), f"Async execution failed: {result.as_error}"
    assert result.unwrap() == 15, f"Expected 15, got {result.unwrap()}"
    
    print("✅ Async function execution working")
    return True


def test_sync_function_execution():
    """Test that sync functions work with new execution system."""
    print("\n=== Testing Sync Function Execution ===")
    
    app = Yaapp()
    
    def sync_func(x: int) -> int:
        return x + 10
    
    app.expose(sync_func)
    
    # Get function from registry
    func, exposer = app._registry["sync_func"]
    
    # Test sync execution
    result = exposer.run(func, x=5)
    
    assert result.is_ok(), f"Sync execution failed: {result.as_error}"
    assert result.unwrap() == 15, f"Expected 15, got {result.unwrap()}"
    
    print("✅ Sync function execution working")
    return True


async def test_sync_function_in_async_context():
    """Test that sync functions work properly in async context with thread execution."""
    print("\n=== Testing Sync Function in Async Context ===")
    
    app = Yaapp()
    
    def sync_func(x: int) -> int:
        return x * 4
    
    # This should use thread execution by default
    app.expose(sync_func)
    
    # Get function from registry
    func, exposer = app._registry["sync_func"]
    
    # Test async execution of sync function
    result = await exposer.run_async(func, x=5)
    
    assert result.is_ok(), f"Async execution of sync function failed: {result.as_error}"
    assert result.unwrap() == 20, f"Expected 20, got {result.unwrap()}"
    
    print("✅ Sync function in async context working")
    return True


def test_direct_execution_strategy():
    """Test direct execution strategy."""
    print("\n=== Testing Direct Execution Strategy ===")
    
    app = Yaapp()
    
    def fast_func(x: int) -> int:
        return x + 1
    
    app.expose(fast_func, execution="direct")
    
    # Check execution hint
    func, _ = app._registry["fast_func"]
    hint = getattr(func, '__execution_hint__', None)
    
    assert hint is not None, "Function should have execution hint"
    assert hint.strategy.value == "direct", f"Expected direct strategy, got {hint.strategy.value}"
    
    print("✅ Direct execution strategy working")
    return True


def test_custom_object_exposure():
    """Test that custom object exposure still works."""
    print("\n=== Testing Custom Object Exposure ===")
    
    app = Yaapp()
    
    class CustomObject:
        def execute_call(self, **kwargs):
            return f"Custom result: {kwargs.get('message', 'default')}"
    
    custom_obj = CustomObject()
    app.expose(custom_obj, name="custom", custom=True)
    
    registry = app.get_registry_items()
    assert "custom" in registry, "Custom object not in registry"
    
    print("✅ Custom object exposure working")
    return True


def test_backward_compatibility():
    """Test that existing code patterns still work."""
    print("\n=== Testing Backward Compatibility ===")
    
    app = Yaapp()
    
    # Old style - should still work
    @app.expose
    def old_style_function(x: int) -> int:
        return x * 2
    
    # New style - should also work  
    @app.expose(execution="thread")
    def new_style_function(x: int) -> int:
        return x * 3
    
    registry = app.get_registry_items()
    assert "old_style_function" in registry, "Old style function not registered"
    assert "new_style_function" in registry, "New style function not registered"
    
    print("✅ Backward compatibility maintained")
    return True


async def main():
    """Run all basic functionality tests."""
    print("🧪 Testing Basic YAPP Functionality After Execution Parameter Changes")
    print("=" * 80)
    
    # Run sync tests
    sync_tests = [
        test_basic_function_exposure,
        test_class_exposure,
        test_sync_function_execution,
        test_direct_execution_strategy,
        test_custom_object_exposure,
        test_backward_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in sync_tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    # Run async tests
    async_tests = [
        test_async_function_execution,
        test_sync_function_in_async_context,
    ]
    
    for test in async_tests:
        try:
            if await test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL BASIC FUNCTIONALITY TESTS PASSED!")
        print("✅ Core YAPP features still working after execution parameter changes")
        print("✅ No regressions detected in basic functionality")
        return 0
    else:
        print("❌ SOME BASIC FUNCTIONALITY TESTS FAILED!")
        print("⚠️  Potential regressions detected")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))