"""
Typer TUI runner for yaapp.
"""

from .interactive_base import InteractiveTUIRunner

try:
    import typer
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False


class TyperRunner(InteractiveTUIRunner):
    """Typer-based TUI runner."""
    
    def _check_dependencies(self) -> bool:
        """Check if typer is available."""
        if not HAS_TYPER:
            print("typer not available. Install with: pip install typer")
            return False
        return True
    
    def _get_backend_name(self) -> str:
        """Get the backend name for display."""
        return "Typer"
    
    def _get_user_input(self, prompt_str: str) -> str:
        """Get user input using simple input() function."""
        return input(prompt_str).strip()