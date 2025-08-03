"""
Standalone expose functionality to avoid circular imports.

This module provides the expose decorator without importing any yaapp internals.
Plugin writers should use: from yaapp import expose
"""

# Global registry for lazy plugin registration
_pending_registrations = []

def expose(obj=None, name=None, custom=False, execution=None):
    """Expose a function, class, or object to yaapp without importing the singleton.
    
    This is the preferred way to expose plugins to avoid circular imports.
    Registrations are queued and applied when yaapp.run() is called.
    
    Args:
        obj: Function, class, or object to expose
        name: Optional name (defaults to function/class name)
        custom: Whether to use custom exposure workflow
        execution: Execution strategy hint
    
    Returns:
        Decorator function or result
    
    Usage:
        @expose(name="my_plugin")
        class MyPlugin:
            pass
            
        # Or
        @expose
        def my_function():
            pass
    """
    def decorator(target_obj):
        # Queue the registration for later
        _pending_registrations.append({
            'obj': target_obj,
            'name': name,
            'custom': custom,
            'execution': execution
        })
        return target_obj
    
    if obj is None:
        # Used as decorator: @expose or @expose(name="foo")
        return decorator
    else:
        # Used directly: expose(func, "name")
        return decorator(obj)

def get_pending_registrations():
    """Get all pending registrations."""
    return _pending_registrations.copy()

def clear_pending_registrations():
    """Clear all pending registrations."""
    global _pending_registrations
    _pending_registrations.clear()

def apply_pending_registrations(yaapp_instance):
    """Apply all pending registrations to the yaapp instance."""
    global _pending_registrations
    applied_count = 0
    for reg in _pending_registrations:
        try:
            yaapp_instance.expose(
                reg['obj'], 
                reg['name'], 
                reg['custom'], 
                reg['execution']
            )
            applied_count += 1
        except Exception as e:
            print(f"⚠️ Failed to register {reg.get('name', 'unnamed')}: {e}")
    
    # Silently apply registrations - no spam
    _pending_registrations.clear()
    return applied_count