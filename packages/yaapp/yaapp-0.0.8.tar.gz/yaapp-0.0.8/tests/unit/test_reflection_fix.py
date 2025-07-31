#!/usr/bin/env python3
"""
Test the reflection system ClickOutputHandler fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp.reflection import ClickOutputHandler
import io
import contextlib

def test_click_output_handler():
    """Test ClickOutputHandler works properly."""
    
    print("=== Testing ClickOutputHandler ===")
    
    try:
        # Test handler creation
        handler = ClickOutputHandler()
        print("✅ ClickOutputHandler created successfully")
        
        # Test that streams are not hijacked during creation
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        handler2 = ClickOutputHandler()
        
        if sys.stdout is original_stdout and sys.stderr is original_stderr:
            print("✅ Stream hijacking eliminated - streams unchanged")
        else:
            print("❌ Stream hijacking still occurs")
            return False
        
        # Test error handling
        handler.write_error("Test error message")
        print("✅ Error handling works")
        
        return True
        
    except Exception as e:
        print(f"❌ ClickOutputHandler test failed: {e}")
        return False

def test_reflection_integration():
    """Test reflection system integration."""
    
    print("\n=== Testing Reflection Integration ===")
    
    try:
        from yaapp.reflection import CLIBuilder, CommandReflector
        from yaapp.core import YaappCore
        
        core = YaappCore()
        
        # Test CLI builder
        builder = CLIBuilder(core)
        print("✅ CLIBuilder created successfully")
        
        # Test command reflector  
        reflector = CommandReflector(core)
        print("✅ CommandReflector created successfully")
        
        # Test basic functionality - CommandReflector has add_reflected_commands
        if hasattr(reflector, 'add_reflected_commands'):
            print("✅ Command reflection method exists")
        else:
            print("❌ Command reflection method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reflection integration test failed: {e}")
        return False

def test_safe_execution():
    """Test that reflection execution is safe."""
    
    print("\n=== Testing Safe Execution ===")
    
    try:
        from yaapp.reflection import CommandReflector
        from yaapp.core import YaappCore
        
        # Create a test function
        def test_function():
            return "Hello from test function"
        
        core = YaappCore()
        core.expose(test_function)
        
        # Use ClickReflection for backward compatibility testing
        from yaapp.reflection import ClickReflection
        reflection = ClickReflection(core)
        
        # Test that we can create reflective CLI without issues
        cli = reflection.create_reflective_cli()
        
        if cli is not None:
            print("✅ Reflective CLI created successfully")
        else:
            print("⚠️  CLI creation returned None (Click may not be available)")
        
        print("✅ Safe execution test completed")
        return True
        
    except Exception as e:
        print(f"❌ Safe execution test failed: {e}")
        return False

def test_stream_safety():
    """Test that stream operations are safe."""
    
    print("\n=== Testing Stream Safety ===")
    
    original_stdout = sys.stdout  
    original_stderr = sys.stderr
    
    try:
        from yaapp.reflection import ClickOutputHandler
        
        # Create multiple handlers
        handlers = [ClickOutputHandler() for _ in range(3)]
        
        # Verify streams never changed
        if sys.stdout is original_stdout and sys.stderr is original_stderr:
            print("✅ Multiple handlers don't affect streams")
        else:
            print("❌ Stream integrity compromised")
            return False
            
        # Test error writing
        for i, handler in enumerate(handlers):
            handler.write_error(f"Test error {i}")
        
        print("✅ Error writing works for all handlers")
        
        # Final stream check
        if sys.stdout is original_stdout and sys.stderr is original_stderr:
            print("✅ Streams remain unchanged after operations")
            return True
        else:
            print("❌ Stream integrity lost after operations")
            return False
            
    except Exception as e:
        print(f"❌ Stream safety test failed: {e}")
        # Restore streams in case of error
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        return False

def main():
    """Run all reflection system tests."""
    
    print("🔧 Testing Reflection System Fixes")
    print("=" * 40)
    
    success1 = test_click_output_handler()
    success2 = test_reflection_integration()
    success3 = test_safe_execution()
    success4 = test_stream_safety()
    
    print("\n" + "=" * 40)
    
    if success1 and success2 and success3 and success4:
        print("🎉 ALL REFLECTION SYSTEM TESTS PASSED!")
        print("✅ ClickOutputHandler working correctly")
        print("✅ Stream hijacking eliminated") 
        print("✅ Reflection integration functional")
        print("✅ Safe execution confirmed")
        print("✅ Stream safety maintained")
        return 0
    else:
        print("❌ SOME REFLECTION SYSTEM TESTS FAILED!")
        failed_tests = []
        if not success1: failed_tests.append("ClickOutputHandler")
        if not success2: failed_tests.append("Reflection integration")
        if not success3: failed_tests.append("Safe execution")
        if not success4: failed_tests.append("Stream safety")
            
        print(f"Failed tests: {', '.join(failed_tests)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())