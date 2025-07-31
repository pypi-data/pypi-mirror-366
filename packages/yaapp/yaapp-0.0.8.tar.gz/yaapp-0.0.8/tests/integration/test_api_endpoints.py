#!/usr/bin/env python3
"""
Test script to validate the new API endpoint structure.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp

# Create test app
app = Yaapp()

@app.expose
def greet(name: str, formal: bool = False) -> str:
    """Greet a person."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"

@app.expose
class Calculator:
    """A calculator with basic operations."""
    
    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        return x + y
    
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

app.expose({
    "math": {
        "subtract": lambda x, y: x - y,
        "advanced": {
            "power": lambda x, y: x ** y
        }
    },
    "utils": {
        "reverse": lambda s: s[::-1]
    }
})

def test_function_exposure():
    """Test that functions are properly exposed."""
    print("=== Testing Function Exposure ===")
    
    # Test function exposure
    greet_func, _ = app._registry['greet']
    result = greet_func("Alice", formal=True)
    if result == "Good day, Alice!":
        print("✅ Function exposure working")
    else:
        print(f"❌ Function exposure failed: {result}")
        return False
    
    return True

def test_class_exposure():
    """Test that classes are properly exposed."""
    print("\n=== Testing Class Exposure ===")
    
    # Test class exposure
    calc_class, _ = app._registry['Calculator']
    calc_instance = calc_class()
    result = calc_instance.add(5, 3)
    if result == 8:
        print("✅ Class exposure working")
    else:
        print(f"❌ Class exposure failed: {result}")
        return False
    
    return True

def test_nested_exposure():
    """Test that nested functions are properly exposed."""
    print("\n=== Testing Nested Function Exposure ===")
    
    # Test nested function exposure
    if 'math.subtract' in app._registry:
        subtract_func, _ = app._registry['math.subtract']
        result = subtract_func(10, 3)
        if result == 7:
            print("✅ Nested function exposure working")
        else:
            print(f"❌ Nested function failed: {result}")
            return False
    else:
        print("❌ Nested function not found in registry")
        return False
    
    return True

def test_registry_structure():
    """Test that the registry has the expected structure."""
    print("\n=== Testing Registry Structure ===")
    
    expected_functions = ['greet', 'Calculator', 'math.subtract', 'math.advanced.power', 'utils.reverse']
    registry_keys = list(app._registry.keys())
    
    missing = []
    for func in expected_functions:
        if func not in registry_keys:
            missing.append(func)
    
    if not missing:
        print("✅ Registry structure correct")
        print(f"✅ Found all expected functions: {registry_keys}")
        return True
    else:
        print(f"❌ Missing functions: {missing}")
        print(f"❌ Registry contains: {registry_keys}")
        return False

if __name__ == "__main__":
    print("🧪 Testing API Endpoints Structure")
    print("="*50)
    
    tests = [
        test_registry_structure,
        test_function_exposure,
        test_class_exposure,
        test_nested_exposure
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
        print("🎉 ALL API ENDPOINT TESTS PASSED!")
        exit(0)
    else:
        print("❌ SOME API ENDPOINT TESTS FAILED!")
        exit(1)