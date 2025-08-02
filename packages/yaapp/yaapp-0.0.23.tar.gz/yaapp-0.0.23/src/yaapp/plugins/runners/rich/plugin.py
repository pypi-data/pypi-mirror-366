"""
Rich TUI runner plugin for yaapp.
Provides beautiful console interface with tables and rich formatting.
"""

import inspect
# Import will be done dynamically to avoid circular imports

try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from yaapp import yaapp


@yaapp.expose("rich")
class RichRunner:
    """Rich-based TUI runner with enhanced formatting."""
    
    def __init__(self, config=None):
        """Initialize Rich runner with optional configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        self.console = Console() if HAS_RICH else None
    
    def help(self) -> str:
        """Return Rich runner-specific help text."""
        return """
🎨 RICH TUI RUNNER HELP:
  --theme TEXT    Color theme (default: dark)
  --layout TEXT   Layout style (default: panel)
  --pager         Enable paging for long output
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the Rich runner with the app instance."""
        if not HAS_RICH:
            print("rich not available. Install with: pip install rich")
            return
        
        self.yaapp = app_instance
        
        # Extract Rich configuration
        theme = kwargs.get('theme', self.config.get('theme', 'dark'))
        layout = kwargs.get('layout', self.config.get('layout', 'panel'))
        pager = kwargs.get('pager', self.config.get('pager', False))
        
        self._run_interactive()
    
    def _run_interactive(self):
        """Run interactive Rich TUI mode."""
        app_name = self.yaapp._get_app_name()
        self.console.print(Panel.fit(f"{app_name} Interactive Shell (Rich)", style="bold blue"))
        self.console.print(self._create_context_table())
        self.console.print("\\n[bold]Commands:[/bold] function_name, help, list, back/.., exit/quit\\n")

        while True:
            try:
                user_input = self._get_user_input("")
                
                if not user_input.strip():
                    continue

                if user_input.strip().lower() in ["exit", "quit"]:
                    self.console.print("[bold green]Goodbye![/bold green]")
                    break
                elif user_input.strip().lower() == "help":
                    self._show_rich_contextual_help()
                elif user_input.strip().lower() == "list":
                    self.console.print(self._create_context_table())
                elif user_input.strip().lower() in ["back", "..", "cd .."]:
                    if self.yaapp._exit_context():
                        context_path = getattr(self.yaapp, '_current_context', [])
                        context_str = ':'.join(context_path) if context_path else 'root'
                        self.console.print(f"[bold green]Moved to {context_str}[/bold green]")
                        self.console.print(self._create_context_table())
                    else:
                        self.console.print("[bold yellow]Already at root level[/bold yellow]")
                else:
                    if not self._handle_rich_contextual_command(user_input.strip()):
                        self._execute_tui_command(user_input.strip())
            except (EOFError, KeyboardInterrupt):
                self.console.print("\\n[bold green]Goodbye![/bold green]")
                break
    
    def _get_user_input(self, prompt_str: str) -> str:
        """Get user input using Rich prompt."""
        context_name = ":".join(getattr(self.yaapp, '_current_context', [])) if hasattr(self.yaapp, '_current_context') and self.yaapp._current_context else self.yaapp._get_app_name()
        return Prompt.ask(f"[bold cyan]{context_name}[/bold cyan]").strip()
    
    def _create_context_table(self):
        """Create a table for the current context."""
        current_commands = self.yaapp._get_current_context_commands()
        context_path = getattr(self.yaapp, '_current_context', [])
        context_str = ":".join(context_path) if context_path else "root"
        table = Table(title=f"Available Commands - {context_str}")
        table.add_column("Command", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")

        for name, func in sorted(current_commands.items()):
            func_type = "Function"
            if inspect.isclass(func):
                func_type = "Class (navigate)"
            elif not self.yaapp._is_leaf_command(name):
                func_type = "Namespace (navigate)"

            doc = getattr(func, "__doc__", "") or "No description"
            if doc:
                doc = doc.split("\\n")[0][:50] + ("..." if len(doc.split("\\n")[0]) > 50 else "")

            table.add_row(name, func_type, doc)

        return table
    
    def _handle_rich_contextual_command(self, command: str) -> bool:
        """Handle contextual navigation for Rich TUI."""
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
                self.console.print(f"[bold green]Entered {context_str} context[/bold green]")
                self.console.print(self._create_context_table())
                return True

        return False  # Let normal command execution handle it
    
    def _show_rich_contextual_help(self) -> None:
        """Show contextual help in Rich format."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="green")

        help_table.add_row("help", "Show this help message")
        help_table.add_row("list", "List available commands in current context")
        help_table.add_row("back / ..", "Go back to parent context")
        help_table.add_row("exit / quit", "Exit the interactive shell")
        help_table.add_row("<command>", "Execute function or navigate to context")

        self.console.print(help_table)

        context_path = getattr(self.yaapp, '_current_context', [])
        if context_path:
            self.console.print(f"\\n[bold]Current context:[/bold] {':'.join(context_path)}")
        else:
            self.console.print("\\n[bold]Current context:[/bold] root")

        current_commands = self.yaapp._get_current_context_commands()
        if current_commands:
            leaf_commands = [name for name in current_commands.keys() if self.yaapp._is_leaf_command(name)]
            nav_commands = [name for name in current_commands.keys() if not self.yaapp._is_leaf_command(name)]

            if leaf_commands:
                self.console.print(f"\\n[bold cyan]Executable commands:[/bold cyan] {', '.join(sorted(leaf_commands))}")
            if nav_commands:
                self.console.print(f"[bold magenta]Navigation commands:[/bold magenta] {', '.join(sorted(nav_commands))}")
    
    def _execute_tui_command(self, command: str):
        """Execute a TUI command with Rich formatting."""
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
                self.console.print(f"[bold red]Command '{command_name}' not found[/bold red]")
                return

            func = current_commands[command_name]
            
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
                self.console.print(f"[bold green]Result:[/bold green] {result}")
            else:
                self.console.print("[bold green]Command executed successfully[/bold green]")

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")