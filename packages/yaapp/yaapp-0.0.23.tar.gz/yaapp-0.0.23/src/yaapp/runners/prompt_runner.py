"""
Prompt toolkit TUI runner for yaapp.
"""

from .interactive_base import InteractiveTUIRunner

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.shortcuts import print_formatted_text
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


class PromptRunner(InteractiveTUIRunner):
    """Prompt toolkit-based TUI runner."""
    
    def _check_dependencies(self) -> bool:
        """Check if prompt_toolkit is available."""
        if not HAS_PROMPT_TOOLKIT:
            print("prompt_toolkit not available. Install with: pip install prompt_toolkit")
            return False
        return True
    
    def _get_backend_name(self) -> str:
        """Get the backend name for display."""
        return "prompt_toolkit"
    
    def _get_user_input(self, prompt_str: str) -> str:
        """Get user input using prompt_toolkit with completion."""
        # Update completer for current context
        current_commands = list(self.core._get_current_context_commands().keys())
        completer = WordCompleter(
            current_commands + ["help", "list", "exit", "quit", "back", ".."]
        )
        
        return prompt(prompt_str, completer=completer)