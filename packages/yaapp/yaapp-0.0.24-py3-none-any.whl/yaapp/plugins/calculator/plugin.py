"""
Calculator Plugin - Simple Math Operations

Provides basic mathematical operations for testing mesh communication.
"""

from yaapp import yaapp
from yaapp.result import Result, Ok, Err


@yaapp.expose("calculator", custom=True)
class Calculator:
    """Simple calculator for mesh testing."""
    
    def __init__(self, config=None):
        """Initialize Calculator with configuration."""
        self.config = config or {}
    
    def expose_to_registry(self, name: str, exposer):
        """Expose Calculator methods to the registry."""
        print(f"🧮 Calculator: Math operations ready")
        print(f"   Operations: add, subtract, multiply, divide")
    
    def execute_call(self, function_name: str, **kwargs) -> Result[any]:
        """Execute Calculator method calls."""
        method = getattr(self, function_name, None)
        if not method:
            return Err(f"Method '{function_name}' not found")
        
        result = method(**kwargs)
        return Ok(result)
    
    def add(self, x: float, y: float) -> float:
        """Add two numbers."""
        return x + y
    
    def subtract(self, x: float, y: float) -> float:
        """Subtract y from x."""
        return x - y
    
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y
    
    def divide(self, x: float, y: float) -> Result[float]:
        """Divide x by y."""
        if y == 0:
            return Err("Division by zero")
        return Ok(x / y)