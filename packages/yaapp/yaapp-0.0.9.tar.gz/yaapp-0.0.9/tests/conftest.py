"""
Pytest configuration for proper import handling.
This eliminates the need for import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src')) in every test file.
"""

import sys
from pathlib import Path
import os
import pytest

# Add src directory to Python path for tests
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestResults:
    """Generic test results tracker for integration tests."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message}"
            print(error)
            self.errors.append(error)
    
    def assert_false(self, condition, message):
        self.assert_true(not condition, message)
    
    def assert_in(self, item, container, message):
        self.assert_true(item in container, message)
    
    def assert_not_in(self, item, container, message):
        self.assert_true(item not in container, message)
    
    def assert_not_none(self, obj, message):
        self.assert_true(obj is not None, message)
    
    def assert_equal(self, actual, expected, message):
        self.assert_true(actual == expected, f"{message} - Expected: {expected}, Got: {actual}")
    
    def assert_contains(self, text, container, message):
        self.assert_true(text in container, message)
    
    def assert_less_than(self, actual, threshold, message):
        self.assert_true(actual < threshold, f"{message} - Expected: < {threshold}, Got: {actual}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


@pytest.fixture
def results():
    """Provide a TestResults instance for integration tests."""
    return TestResults()


# Simple timeout handling without external plugins
import signal
import functools

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out")

def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator