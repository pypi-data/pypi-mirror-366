#!/usr/bin/env python3
"""
Generate a test coverage report for yaapp plugins.
"""

import os
from pathlib import Path

def analyze_test_coverage():
    """Analyze test coverage for yaapp plugins."""
    
    print("📊 YAAPP PLUGIN TEST COVERAGE REPORT")
    print("=" * 60)
    
    # Plugin directories in src
    src_plugins_dir = Path(__file__).parent.parent / "src" / "yaapp" / "plugins"
    test_plugins_dir = Path(__file__).parent / "plugins"
    
    if not src_plugins_dir.exists():
        print("❌ Source plugins directory not found")
        return
    
    # Get all plugin directories
    plugin_dirs = [d for d in src_plugins_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    
    print(f"\n🔍 Found {len(plugin_dirs)} plugins in source:")
    
    coverage_stats = {
        'total_plugins': 0,
        'tested_plugins': 0,
        'untested_plugins': 0
    }
    
    tested_plugins = []
    untested_plugins = []
    
    for plugin_dir in sorted(plugin_dirs):
        plugin_name = plugin_dir.name
        coverage_stats['total_plugins'] += 1
        
        # Check if plugin has tests
        test_dir = test_plugins_dir / plugin_name
        has_tests = test_dir.exists() and any(test_dir.glob("test_*.py"))
        
        if has_tests:
            test_files = list(test_dir.glob("test_*.py"))
            print(f"✅ {plugin_name:<15} - {len(test_files)} test files")
            coverage_stats['tested_plugins'] += 1
            tested_plugins.append(plugin_name)
        else:
            print(f"❌ {plugin_name:<15} - No tests")
            coverage_stats['untested_plugins'] += 1
            untested_plugins.append(plugin_name)
    
    # Calculate coverage percentage
    coverage_percentage = (coverage_stats['tested_plugins'] / coverage_stats['total_plugins']) * 100
    
    print("\n" + "=" * 60)
    print("📈 COVERAGE SUMMARY:")
    print(f"Total Plugins:    {coverage_stats['total_plugins']}")
    print(f"Tested Plugins:   {coverage_stats['tested_plugins']}")
    print(f"Untested Plugins: {coverage_stats['untested_plugins']}")
    print(f"Coverage:         {coverage_percentage:.1f}%")
    
    if coverage_percentage >= 80:
        print("🎉 EXCELLENT COVERAGE!")
    elif coverage_percentage >= 60:
        print("👍 GOOD COVERAGE")
    elif coverage_percentage >= 40:
        print("⚠️  MODERATE COVERAGE")
    else:
        print("🚨 LOW COVERAGE - NEEDS IMPROVEMENT")
    
    if untested_plugins:
        print(f"\n❌ UNTESTED PLUGINS:")
        for plugin in untested_plugins:
            print(f"   - {plugin}")
        print("\n💡 Consider adding tests for these plugins!")
    
    if tested_plugins:
        print(f"\n✅ TESTED PLUGINS:")
        for plugin in tested_plugins:
            print(f"   - {plugin}")
    
    print("\n" + "=" * 60)
    
    # Specific analysis for async-first plugins we just fixed
    async_plugins = ['registry', 'mesh', 'portalloc', 'docker']
    print("🔄 ASYNC-FIRST PLUGINS STATUS:")
    
    for plugin in async_plugins:
        test_dir = test_plugins_dir / plugin
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            async_test_files = list(test_dir.glob("*async*.py"))
            print(f"✅ {plugin:<12} - {len(test_files)} tests ({len(async_test_files)} async-specific)")
        else:
            print(f"❌ {plugin:<12} - No tests")
    
    return coverage_stats

if __name__ == "__main__":
    analyze_test_coverage()