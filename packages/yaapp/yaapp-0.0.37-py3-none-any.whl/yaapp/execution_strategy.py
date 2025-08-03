"""
Execution strategy definitions for YAAPP framework.
Defines how sync functions should be executed in async contexts.
"""

from enum import Enum
from typing import Any, Callable, Optional


class ExecutionStrategy(Enum):
    """
    Execution strategies for sync functions in async contexts.
    """
    # Direct execution - blocks event loop but fastest for quick functions
    DIRECT = "direct"
    
    # Thread pool execution - non-blocking, good for I/O and moderate CPU work
    THREAD = "thread"
    
    # Process pool execution - for CPU-intensive work (requires pickleable functions)
    PROCESS = "process"
    
    # Automatic detection based on heuristics
    AUTO = "auto"


class ExecutionHint:
    """
    Container for execution hints attached to functions.
    """
    
    def __init__(self, 
                 strategy: ExecutionStrategy = ExecutionStrategy.THREAD,
                 max_workers: Optional[int] = None,
                 timeout: Optional[float] = None):
        """
        Initialize execution hint.
        
        Args:
            strategy: How to execute the function in async context
            max_workers: Max workers for thread/process pools (None = use default)
            timeout: Timeout for execution (None = no timeout)
        """
        self.strategy = strategy
        self.max_workers = max_workers
        self.timeout = timeout
    
    def __repr__(self):
        return f"ExecutionHint(strategy={self.strategy.value}, max_workers={self.max_workers}, timeout={self.timeout})"


def execution_hint(strategy: str = "thread", 
                   max_workers: Optional[int] = None,
                   timeout: Optional[float] = None) -> Callable:
    """
    Decorator to add execution hints to functions.
    
    Args:
        strategy: Execution strategy ("direct", "thread", "process", "auto")
        max_workers: Maximum workers for pools
        timeout: Execution timeout in seconds
    
    Returns:
        Decorated function with execution hint attached
    
    Example:
        @execution_hint("thread")
        def slow_function():
            time.sleep(1)
            return "done"
        
        @execution_hint("direct")  
        def fast_function():
            return 42
    """
    try:
        strategy_enum = ExecutionStrategy(strategy)
    except ValueError:
        print(f"Warning: Invalid execution strategy: {strategy}. "
                        f"Valid options: {[s.value for s in ExecutionStrategy]}")
        strategy_enum = ExecutionStrategy.THREAD  # Default fallback
    
    def decorator(func: Callable) -> Callable:
        hint = ExecutionHint(
            strategy=strategy_enum,
            max_workers=max_workers,
            timeout=timeout
        )
        
        # Attach hint to function
        func.__execution_hint__ = hint
        return func
    
    return decorator


def get_execution_hint(func: Callable) -> ExecutionHint:
    """
    Get execution hint from function, or return default.
    
    Args:
        func: Function to check
        
    Returns:
        ExecutionHint (default is THREAD strategy)
    """
    return getattr(func, '__execution_hint__', ExecutionHint())


def should_use_thread_pool(func: Callable, hint: ExecutionHint) -> bool:
    """
    Determine if function should use thread pool based on hint and heuristics.
    
    Args:
        func: Function to analyze
        hint: Execution hint
        
    Returns:
        True if should use thread pool
    """
    if hint.strategy == ExecutionStrategy.DIRECT:
        return False
    elif hint.strategy == ExecutionStrategy.THREAD:
        return True
    elif hint.strategy == ExecutionStrategy.PROCESS:
        return False  # Process pool handled separately
    elif hint.strategy == ExecutionStrategy.AUTO:
        return _detect_blocking_function(func)
    
    return True  # Default to thread pool for safety


def should_use_process_pool(func: Callable, hint: ExecutionHint) -> bool:
    """
    Determine if function should use process pool.
    
    Args:
        func: Function to analyze
        hint: Execution hint
        
    Returns:
        True if should use process pool
    """
    return hint.strategy == ExecutionStrategy.PROCESS


def _detect_blocking_function(func: Callable) -> bool:
    """
    Heuristics to detect if a function might be blocking.
    
    Args:
        func: Function to analyze
        
    Returns:
        True if function is likely to block
    """
    # Get function metadata
    name = getattr(func, '__name__', '').lower()
    module = getattr(func, '__module__', '')
    doc = getattr(func, '__doc__', '') or ''
    
    # Common blocking patterns
    blocking_keywords = [
        'sleep', 'wait', 'request', 'download', 'upload', 'fetch',
        'read', 'write', 'save', 'load', 'connect', 'query', 'sql',
        'http', 'api', 'network', 'socket', 'file', 'database', 'db'
    ]
    
    # Check function name
    if any(keyword in name for keyword in blocking_keywords):
        return True
    
    # Check module name for common blocking libraries
    blocking_modules = [
        'requests', 'urllib', 'http', 'socket', 'sqlite3', 'mysql',
        'psycopg2', 'sqlalchemy', 'pymongo', 'redis', 'time'
    ]
    
    if any(mod in module for mod in blocking_modules):
        return True
    
    # Check docstring for hints
    doc_lower = doc.lower()
    if any(keyword in doc_lower for keyword in blocking_keywords):
        return True
    
    # Default to threading for safety - better safe than sorry
    # Most functions that developers expose are likely to do some work
    return True


# Convenience functions for common patterns
def direct_execution():
    """Decorator for functions that should always execute directly."""
    return execution_hint("direct")


def thread_execution(max_workers: Optional[int] = None, timeout: Optional[float] = None):
    """Decorator for functions that should execute in thread pool."""
    return execution_hint("thread", max_workers=max_workers, timeout=timeout)


def process_execution(max_workers: Optional[int] = None, timeout: Optional[float] = None):
    """Decorator for functions that should execute in process pool."""
    return execution_hint("process", max_workers=max_workers, timeout=timeout)


def auto_execution():
    """Decorator for functions with automatic execution strategy detection."""
    return execution_hint("auto")