#!/usr/bin/env python3
"""
Test that migrated test files work correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_migrated_files():
    """Test that key migrated files work."""
    
    print("🧪 Testing Migrated Test Files")
    print("=" * 40)
    
    # Test files to verify
    test_cases = [
        ('tests/unit/test_argument_parsing_fix.py', 'Unit test'),
        ('tests/integration/test_comprehensive.py', 'Integration test'),
        ('tests/integration/test_discovery_optimization.py', 'Discovery test'),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_file, description in test_cases:
        test_path = Path(test_file)
        
        if not test_path.exists():
            print(f"❌ {description}: {test_file} not found")
            continue
        
        try:
            # Change to the test file's directory and run it
            test_dir = test_path.parent
            test_name = test_path.name
            
            # Run the test from its directory
            result = subprocess.run(
                [sys.executable, test_name],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {description}: {test_file}")
                success_count += 1
            else:
                print(f"❌ {description}: {test_file}")
                print(f"   Error: {result.stderr.split(chr(10))[0] if result.stderr else 'Unknown error'}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description}: {test_file} - Timeout")
        except Exception as e:
            print(f"❌ {description}: {test_file} - Exception: {e}")
    
    print(f"\n📊 Migration Test Results:")
    print(f"✅ Passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All migrated tests working correctly!")
        return True
    else:
        print("⚠️  Some tests have issues")
        return False

if __name__ == "__main__":
    test_migrated_files()