"""
Main entry point for the yaapp CLI command.
Separated to avoid circular imports.
"""

def main():
    """Main entry point for the yaapp CLI command."""
    import sys
    
    # Get the singleton instance - this is safe since main.py doesn't import app.py
    from yaapp import yaapp as app
    
    # Trigger plugin discovery on the singleton
    if not app._plugins_discovered:
        app._auto_discover_plugins()
    
    # Simple CLI - just show what's available
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']):
        print("yaapp - Yet Another App Framework")
        print("\nAvailable functions:")
        registry_items = app.get_registry_items()
        if registry_items:
            for name, obj in sorted(registry_items.items()):
                print(f"  {name}")
        else:
            print("  No functions exposed. Add some with @app.expose")
        print("\nUsage: yaapp <function_name> [args...]")
        return
    
    # Execute function
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        args = sys.argv[2:]
        
        registry_items = app.get_registry_items()
        if func_name in registry_items:
            try:
                result = app._call_function_with_args(registry_items[func_name], args)
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Function '{func_name}' not found.")
            print(f"Available: {list(registry_items.keys())}")
    else:
        print("Usage: yaapp <function_name> [args...]")
        print("Use 'yaapp --help' to see available functions")