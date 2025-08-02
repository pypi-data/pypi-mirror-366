"""
Utility classes for reflection system - extracted for better separation of concerns.
"""

from typing import Any, Dict


class ArgumentParser:
    """Handles safe argument parsing for reflected commands."""
    
    def parse_args_to_kwargs(self, args: list) -> Dict[str, Any]:
        """Parse command line arguments to kwargs format with safe handling."""
        kwargs = {}
        
        for arg in args:
            if arg.startswith("--"):
                if "=" in arg:
                    key, value = arg[2:].split("=", 1)
                    kwargs[key] = value
                else:
                    # Boolean flag without value
                    kwargs[arg[2:]] = True
        
        return kwargs