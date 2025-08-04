"""
Simple calculator plugin for yaapp-core example.
"""

from yaapp import expose

@expose(name='calculator')
class Calculator:
    """Simple calculator with basic operations."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.history = []
    
    def add(self, x: float, y: float) -> float:
        """Add two numbers."""
        result = x + y
        self.history.append(f"{x} + {y} = {result}")
        return result
    
    def subtract(self, x: float, y: float) -> float:
        """Subtract y from x."""
        result = x - y
        self.history.append(f"{x} - {y} = {result}")
        return result
    
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        result = x * y
        self.history.append(f"{x} * {y} = {result}")
        return result
    
    def divide(self, x: float, y: float) -> float:
        """Divide x by y."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        result = x / y
        self.history.append(f"{x} / {y} = {result}")
        return result
    
    def get_history(self, limit: int = 10) -> list:
        """Get calculation history."""
        return self.history[-limit:]
    
    def clear_history(self) -> str:
        """Clear calculation history."""
        self.history.clear()
        return "History cleared"