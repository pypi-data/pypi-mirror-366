"""
Rich TUI runner for yaapp.
"""

import inspect
from .interactive_base import InteractiveTUIRunner

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class RichRunner(InteractiveTUIRunner):
    """Rich-based TUI runner with enhanced formatting."""
    
    def __init__(self, core):
        """Initialize with rich console."""
        super().__init__(core)
        self.console = Console() if HAS_RICH else None
    
    def _check_dependencies(self) -> bool:
        """Check if rich is available."""
        if not HAS_RICH:
            print("rich not available. Install with: pip install rich")
            return False
        return True
    
    def _get_backend_name(self) -> str:
        """Get the backend name for display."""
        return "Rich"
    
    def _get_user_input(self, prompt_str: str) -> str:
        """Get user input using Rich prompt."""
        context_name = ":".join(getattr(self.core, '_current_context', [])) if hasattr(self.core, '_current_context') and self.core._current_context else self.core._get_app_name()
        return Prompt.ask(f"[bold cyan]{context_name}[/bold cyan]").strip()
    
    def run(self):
        """Run interactive TUI with rich formatting enhancements.""" 
        if not self._check_dependencies():
            return

        app_name = self.core._get_app_name()
        self.console.print(Panel.fit(f"{app_name} Interactive Shell (Rich)", style="bold blue"))
        self.console.print(self._create_context_table())
        self.console.print("\n[bold]Commands:[/bold] function_name, help, list, back/.., exit/quit\n")

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
                    if self.core._exit_context():
                        context_path = getattr(self.core, '_current_context', [])
                        context_str = ':'.join(context_path) if context_path else 'root'
                        self.console.print(f"[bold green]Moved to {context_str}[/bold green]")
                        self.console.print(self._create_context_table())
                    else:
                        self.console.print("[bold yellow]Already at root level[/bold yellow]")
                else:
                    if not self._handle_rich_contextual_command(user_input.strip()):
                        self._execute_tui_command(user_input.strip(), self.console)
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[bold green]Goodbye![/bold green]")
                break
    
    def _create_context_table(self):
        """Create a table for the current context."""
        current_commands = self.core._get_current_context_commands()
        context_path = getattr(self.core, '_current_context', [])
        context_str = ":".join(context_path) if context_path else "root"
        table = Table(title=f"Available Commands - {context_str}")
        table.add_column("Command", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")

        for name, func in sorted(current_commands.items()):
            func_type = "Function"
            if inspect.isclass(func):
                func_type = "Class (navigate)"
            elif not self.core._is_leaf_command(name):
                func_type = "Namespace (navigate)"

            doc = getattr(func, "__doc__", "") or "No description"
            if doc:
                doc = doc.split("\n")[0][:50] + ("..." if len(doc.split("\n")[0]) > 50 else "")

            table.add_row(name, func_type, doc)

        return table
    
    def _handle_rich_contextual_command(self, command: str) -> bool:
        """Handle contextual navigation for Rich TUI."""
        parts = command.split()
        if not parts:
            return False

        command_name = parts[0]
        current_commands = self.core._get_current_context_commands()

        if command_name not in current_commands:
            return False

        # If it's not a leaf command, enter its context
        if not self.core._is_leaf_command(command_name):
            if self.core._enter_context(command_name):
                context_path = getattr(self.core, '_current_context', [])
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

        context_path = getattr(self.core, '_current_context', [])
        if context_path:
            self.console.print(f"\n[bold]Current context:[/bold] {':'.join(context_path)}")
        else:
            self.console.print("\n[bold]Current context:[/bold] root")

        current_commands = self.core._get_current_context_commands()
        if current_commands:
            leaf_commands = [name for name in current_commands.keys() if self.core._is_leaf_command(name)]
            nav_commands = [name for name in current_commands.keys() if not self.core._is_leaf_command(name)]

            if leaf_commands:
                self.console.print(f"\n[bold cyan]Executable commands:[/bold cyan] {', '.join(sorted(leaf_commands))}")
            if nav_commands:
                self.console.print(f"[bold magenta]Navigation commands:[/bold magenta] {', '.join(sorted(nav_commands))}")