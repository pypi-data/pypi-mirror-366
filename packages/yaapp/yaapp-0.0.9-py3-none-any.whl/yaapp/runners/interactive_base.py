"""
Base class for interactive TUI runners with common functionality.
"""

import json
from abc import abstractmethod
from .base import BaseRunner


class InteractiveTUIRunner(BaseRunner):
    """Base class for interactive TUI runners with shared command execution logic."""
    
    def run(self):
        """Run interactive TUI with input loop."""
        if not self._check_dependencies():
            return

        app_name = self.core._get_app_name()
        backend_name = self._get_backend_name()
        print(f"{app_name} Interactive Shell ({backend_name})")
        print("Type 'help' for available commands, 'exit' or 'quit' to exit")
        self._show_current_context_info()

        while True:
            try:
                prompt_str = self.core._get_prompt_string()
                user_input = self._get_user_input(prompt_str)
                
                if not user_input.strip():
                    continue

                if user_input.strip().lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                elif user_input.strip().lower() == "help":
                    self._show_contextual_help()
                elif user_input.strip().lower() == "list":
                    self._list_current_context()
                elif user_input.strip().lower() in ["back", "..", "cd .."]:
                    if self.core._exit_context():
                        context_path = getattr(self.core, '_current_context', [])
                        context_str = ':'.join(context_path) if context_path else 'root'
                        print(f"Moved to {context_str}")
                        self._show_current_context_info()
                    else:
                        print("Already at root level")
                else:
                    if not self._handle_contextual_command(user_input.strip()):
                        self._execute_tui_command(user_input.strip())
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
    
    @abstractmethod
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available. Return True if available."""
        pass
    
    @abstractmethod
    def _get_backend_name(self) -> str:
        """Get the name of the backend for display purposes."""
        pass
    
    @abstractmethod
    def _get_user_input(self, prompt_str: str) -> str:
        """Get user input using the specific backend's input method."""
        pass
    
    def _execute_tui_command(self, command: str, console=None) -> None:
        """Execute a command in TUI mode using click interface."""
        parts = command.split()
        if not parts:
            return

        func_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Get commands available in current context
        current_commands = self.core._get_current_context_commands()

        if func_name not in current_commands:
            error_msg = f"Function '{func_name}' not found. Available: {', '.join(current_commands.keys())}"
            self._print_error(error_msg, console)
            return

        # Try to execute through click interface for proper --help support
        try:
            from ..reflection import ClickReflection
            reflection = ClickReflection(self.core)
            reflection.execute_command_through_click(func_name, args, console)
            return
        except ImportError:
            pass
        except Exception as e:
            # Fallback to direct execution if click fails
            warning_msg = f"Click execution failed, falling back to direct: {str(e)}"
            self._print_warning(warning_msg, console)

        # Fallback to direct function execution
        try:
            func = current_commands[func_name]
            result = self.core._call_function_with_args(func, args)
            self._print_result(result, console)
                
        except (KeyboardInterrupt, SystemExit):
            # Re-raise system exceptions to allow proper exit
            raise
        except Exception as e:
            error_msg = f"Error executing {func_name}: {str(e)}"
            self._print_error(error_msg, console)
    
    def _print_error(self, message: str, console=None) -> None:
        """Print an error message, with optional console formatting."""
        if console and hasattr(console, 'print'):
            console.print(f"[bold red]Error:[/bold red] {message}")
        else:
            print(f"Error: {message}")
    
    def _print_warning(self, message: str, console=None) -> None:
        """Print a warning message, with optional console formatting."""
        if console and hasattr(console, 'print'):
            console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
        else:
            print(f"Warning: {message}")
    
    def _print_result(self, result, console=None) -> None:
        """Print a result, with optional console formatting."""
        if console and hasattr(console, 'print'):
            if isinstance(result, dict):
                console.print_json(json.dumps(result, indent=2))
            else:
                console.print(f"[bold green]Result:[/bold green] {result}")
        else:
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))
            else:
                print(f"Result: {result}")