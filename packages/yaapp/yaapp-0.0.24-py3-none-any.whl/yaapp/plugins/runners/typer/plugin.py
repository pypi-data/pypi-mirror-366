"""
Typer TUI runner plugin for yaapp.
Provides simple interactive mode with basic TUI features.
"""

import inspect
# Import will be done dynamically to avoid circular imports

try:
    import typer
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

from yaapp import yaapp


@yaapp.expose("typer")
class TyperRunner:
    """Typer-based TUI runner with simple interactive features."""
    
    def __init__(self, config=None):
        """Initialize Typer runner with optional configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
    
    def help(self) -> str:
        """Return Typer runner-specific help text."""
        return """
⌨️ TYPER TUI RUNNER HELP:
  --confirm       Require confirmation for destructive operations
  --color         Enable colored output
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the Typer runner with the app instance."""
        if not HAS_TYPER:
            print("typer not available. Install with: pip install typer")
            return
        
        self.yaapp = app_instance
        
        # Extract Typer configuration
        confirm = kwargs.get('confirm', self.config.get('confirm', False))
        color = kwargs.get('color', self.config.get('color', True))
        
        self._run_interactive(confirm, color)
    
    def _run_interactive(self, confirm: bool, color: bool):
        """Run interactive Typer TUI mode."""
        app_name = self.yaapp._get_app_name()
        
        if color:
            typer.secho(f"{app_name} Interactive Shell (Typer)", fg=typer.colors.BLUE, bold=True)
        else:
            print(f"{app_name} Interactive Shell (Typer)")
        
        print("Commands: function_name, help, list, back/.., exit/quit")
        print()

        while True:
            try:
                # Get current context for prompt
                context_path = getattr(self.yaapp, '_current_context', [])
                context_str = ":".join(context_path) if context_path else app_name
                
                user_input = input(f"{context_str}> ").strip()
                
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    if color:
                        typer.secho("Goodbye!", fg=typer.colors.GREEN)
                    else:
                        print("Goodbye!")
                    break
                elif user_input.lower() == "help":
                    self._show_contextual_help(color)
                elif user_input.lower() == "list":
                    self._list_current_commands(color)
                elif user_input.lower() in ["back", "..", "cd .."]:
                    if self.yaapp._exit_context():
                        context_path = getattr(self.yaapp, '_current_context', [])
                        context_str = ':'.join(context_path) if context_path else 'root'
                        if color:
                            typer.secho(f"Moved to {context_str}", fg=typer.colors.GREEN)
                        else:
                            print(f"Moved to {context_str}")
                        self._list_current_commands(color)
                    else:
                        if color:
                            typer.secho("Already at root level", fg=typer.colors.YELLOW)
                        else:
                            print("Already at root level")
                else:
                    if not self._handle_contextual_command(user_input, color):
                        self._execute_tui_command(user_input, confirm, color)
            except (EOFError, KeyboardInterrupt):
                if color:
                    typer.secho("\\nGoodbye!", fg=typer.colors.GREEN)
                else:
                    print("\\nGoodbye!")
                break
    
    def _handle_contextual_command(self, command: str, color: bool) -> bool:
        """Handle contextual navigation for Typer TUI."""
        parts = command.split()
        if not parts:
            return False

        command_name = parts[0]
        current_commands = self.yaapp._get_current_context_commands()

        if command_name not in current_commands:
            return False

        # If it's not a leaf command, enter its context
        if not self.yaapp._is_leaf_command(command_name):
            if self.yaapp._enter_context(command_name):
                context_path = getattr(self.yaapp, '_current_context', [])
                context_str = ':'.join(context_path) if context_path else 'root'
                if color:
                    typer.secho(f"Entered {context_str} context", fg=typer.colors.GREEN)
                else:
                    print(f"Entered {context_str} context")
                self._list_current_commands(color)
                return True

        return False  # Let normal command execution handle it
    
    def _show_contextual_help(self, color: bool) -> None:
        """Show contextual help."""
        if color:
            typer.secho("\\nAvailable Commands:", fg=typer.colors.CYAN, bold=True)
        else:
            print("\\nAvailable Commands:")
        
        print("  help          - Show this help message")
        print("  list          - List available commands in current context")
        print("  back / ..     - Go back to parent context")
        print("  exit / quit   - Exit the interactive shell")
        print("  <command>     - Execute function or navigate to context")

        context_path = getattr(self.yaapp, '_current_context', [])
        if context_path:
            if color:
                typer.secho(f"\\nCurrent context: {':'.join(context_path)}", fg=typer.colors.MAGENTA)
            else:
                print(f"\\nCurrent context: {':'.join(context_path)}")
        else:
            if color:
                typer.secho("\\nCurrent context: root", fg=typer.colors.MAGENTA)
            else:
                print("\\nCurrent context: root")

        current_commands = self.yaapp._get_current_context_commands()
        if current_commands:
            leaf_commands = [name for name in current_commands.keys() if self.yaapp._is_leaf_command(name)]
            nav_commands = [name for name in current_commands.keys() if not self.yaapp._is_leaf_command(name)]

            if leaf_commands:
                if color:
                    typer.secho(f"\\nExecutable commands: {', '.join(sorted(leaf_commands))}", fg=typer.colors.CYAN)
                else:
                    print(f"\\nExecutable commands: {', '.join(sorted(leaf_commands))}")
            if nav_commands:
                if color:
                    typer.secho(f"Navigation commands: {', '.join(sorted(nav_commands))}", fg=typer.colors.MAGENTA)
                else:
                    print(f"Navigation commands: {', '.join(sorted(nav_commands))}")
        print()
    
    def _list_current_commands(self, color: bool):
        """List commands in current context."""
        current_commands = self.yaapp._get_current_context_commands()
        context_path = getattr(self.yaapp, '_current_context', [])
        context_str = ":".join(context_path) if context_path else "root"
        
        if color:
            typer.secho(f"\\nAvailable Commands - {context_str}:", fg=typer.colors.CYAN, bold=True)
        else:
            print(f"\\nAvailable Commands - {context_str}:")
        
        if not current_commands:
            print("  No commands available in this context")
            return
        
        for name, func in sorted(current_commands.items()):
            func_type = "function"
            if inspect.isclass(func):
                func_type = "class (navigate)"
            elif not self.yaapp._is_leaf_command(name):
                func_type = "namespace (navigate)"

            doc = getattr(func, "__doc__", "") or "No description"
            if doc:
                doc = doc.split("\\n")[0][:60] + ("..." if len(doc.split("\\n")[0]) > 60 else "")

            if color:
                typer.secho(f"  {name:<20}", fg=typer.colors.CYAN, nl=False)
                typer.secho(f" | {func_type:<15}", fg=typer.colors.MAGENTA, nl=False)
                typer.secho(f" | {doc}", fg=typer.colors.GREEN)
            else:
                print(f"  {name:<20} | {func_type:<15} | {doc}")
        print()
    
    def _execute_tui_command(self, command: str, confirm: bool, color: bool):
        """Execute a TUI command."""
        try:
            # Parse command and arguments
            parts = command.split()
            if not parts:
                return

            command_name = parts[0]
            args = parts[1:]

            # Get current context commands
            current_commands = self.yaapp._get_current_context_commands()
            
            if command_name not in current_commands:
                if color:
                    typer.secho(f"Command '{command_name}' not found", fg=typer.colors.RED)
                else:
                    print(f"Command '{command_name}' not found")
                return

            func = current_commands[command_name]
            
            # Check for confirmation if enabled
            if confirm:
                if not typer.confirm(f"Execute '{command}'?"):
                    if color:
                        typer.secho("Command cancelled", fg=typer.colors.YELLOW)
                    else:
                        print("Command cancelled")
                    return
            
            # Parse arguments into kwargs
            kwargs = {}
            for arg in args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    key = key.lstrip('-')  # Remove leading dashes
                    kwargs[key] = value
                else:
                    # Positional argument - for now, skip
                    pass

            # Execute function
            result = self.yaapp._call_function_with_args(func, **kwargs)
            
            if result is not None:
                if color:
                    typer.secho(f"Result: {result}", fg=typer.colors.GREEN)
                else:
                    print(f"Result: {result}")
            else:
                if color:
                    typer.secho("Command executed successfully", fg=typer.colors.GREEN)
                else:
                    print("Command executed successfully")

        except Exception as e:
            if color:
                typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            else:
                print(f"Error: {str(e)}")