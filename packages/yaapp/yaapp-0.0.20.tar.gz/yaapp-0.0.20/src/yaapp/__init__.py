# yaapp
# A library bridging FastAPI and CLI interfaces

from .app import Yaapp
from .execution_strategy import (
    ExecutionStrategy,
    auto_execution,
    direct_execution,
    execution_hint,
    process_execution,
    thread_execution,
)

# The singleton instance for normal usage (lazy plugin discovery)
yaapp = Yaapp(auto_discover=False)

__version__ = "0.0.8"
__all__ = [
    "yaapp",  # Singleton instance
    "Yaapp",  # Class for testing
    "execution_hint",
    "direct_execution",
    "thread_execution",
    "process_execution",
    "auto_execution",
    "ExecutionStrategy",
]
