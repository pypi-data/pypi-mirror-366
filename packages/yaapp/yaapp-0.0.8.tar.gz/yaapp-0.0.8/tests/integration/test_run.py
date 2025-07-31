#!/usr/bin/env python3
"""
Test the run method of YApp
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp

# Create instance
yapp = Yaapp()


# Add some test functions
@yapp.expose
def greet(name: str, formal: bool = False) -> str:
    """Greet a person."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"


@yapp.expose
class Calculator:
    """A simple calculator."""

    def add(self, x: int, y: int) -> int:
        return x + y


# Add via method call
yapp.expose({"math": {"subtract": lambda x, y: x - y, "power": lambda x, y: x**y}})

def test_registry_contents():
    """Test that the registry contains expected functions."""
    print("=== Testing Registry Contents ===")
    
    expected = ['greet', 'Calculator', 'math.subtract', 'math.power']
    registry_keys = list(yapp._registry.keys())
    
    missing = []
    for func in expected:
        if func not in registry_keys:
            missing.append(func)
    
    if not missing:
        print(f"✅ Registry contains all expected functions: {registry_keys}")
        return True
    else:
        print(f"❌ Missing functions: {missing}")
        print(f"❌ Registry contains: {registry_keys}")
        return False

def test_function_execution():
    """Test that functions can be executed directly."""
    print("\n=== Testing Function Execution ===")
    
    # Test direct function call
    try:
        greet_func, _ = yapp._registry['greet']
        result = greet_func("Alice")
        if result == "Hello, Alice!":
            print("✅ Function execution working")
        else:
            print(f"❌ Function execution failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Function execution failed with exception: {e}")
        return False
    
    return True

def test_class_instantiation():
    """Test that classes can be instantiated and used."""
    print("\n=== Testing Class Instantiation ===")
    
    try:
        calc_class, _ = yapp._registry['Calculator']
        calc_instance = calc_class()
        result = calc_instance.add(5, 3)
        if result == 8:
            print("✅ Class instantiation and method execution working")
        else:
            print(f"❌ Class method execution failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Class instantiation failed with exception: {e}")
        return False
    
    return True

def test_nested_function_execution():
    """Test that nested functions can be executed."""
    print("\n=== Testing Nested Function Execution ===")
    
    try:
        subtract_func, _ = yapp._registry['math.subtract']
        result = subtract_func(10, 3)
        if result == 7:
            print("✅ Nested function execution working")
        else:
            print(f"❌ Nested function execution failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Nested function execution failed with exception: {e}")
        return False
    
    return True

def test_run_method_availability():
    """Test that the run method exists and is callable."""
    print("\n=== Testing Run Method Availability ===")
    
    if hasattr(yapp, 'run') and callable(getattr(yapp, 'run')):
        print("✅ Run method is available and callable")
        return True
    else:
        print("❌ Run method is not available or not callable")
        return False

if __name__ == "__main__":
    print("🧪 Testing YApp Run Method and Registry")
    print("="*50)
    
    tests = [
        test_registry_contents,
        test_function_execution,
        test_class_instantiation,
        test_nested_function_execution,
        test_run_method_availability
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL RUN METHOD TESTS PASSED!")
        exit(0)
    else:
        print("❌ SOME RUN METHOD TESTS FAILED!")
        exit(1)
