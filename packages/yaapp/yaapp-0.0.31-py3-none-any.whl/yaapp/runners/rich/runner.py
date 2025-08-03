"""
Rich TUI runner for yaapp.
Provides beautiful console interface with tables and rich formatting.
"""

import inspect

try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def help() -> str:
    """Return Rich runner-specific help text."""
    return """
🎨 RICH TUI RUNNER HELP:
  --theme TEXT    Color theme (default: dark)
  --layout TEXT   Layout style (default: panel)
  --pager         Enable paging for long output
    """


def run(app_instance, **kwargs):
    """Execute the Rich runner with the app instance."""
    if not HAS_RICH:
        print("rich not available. Install with: pip install rich")
        return
    
    # Extract Rich configuration
    theme = kwargs.get('theme', 'dark')
    layout = kwargs.get('layout', 'panel')
    pager = kwargs.get('pager', False)
    
    _run_interactive(app_instance)


def _run_interactive(app_instance):
    """Run interactive Rich TUI mode."""
    console = Console()
    app_name = getattr(app_instance, '_get_app_name', lambda: 'YApp')()
    
    console.print(Panel.fit(f"{app_name} Interactive Shell (Rich)", style="bold blue"))
    console.print(_create_context_table(app_instance, console))
    console.print("\\n[bold]Commands:[/bold] function_name, help, list, exit/quit\\n")

    while True:
        try:
            user_input = Prompt.ask(f"[bold cyan]{app_name}[/bold cyan]").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold green]Goodbye![/bold green]")
                break
            elif user_input.lower() == "help":
                _show_rich_help(console)
            elif user_input.lower() == "list":
                console.print(_create_context_table(app_instance, console))
            else:
                _execute_tui_command(app_instance, console, user_input)
        except (EOFError, KeyboardInterrupt):
            console.print("\\n[bold green]Goodbye![/bold green]")
            break


def _create_context_table(app_instance, console):
    """Create a table for available commands."""
    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Description", style="green")

    for name, (obj, exposer) in sorted(app_instance._registry.items()):
        func_type = "Function"
        if inspect.isclass(obj):
            func_type = "Class"
        elif hasattr(obj, '__call__'):
            func_type = "Callable"

        doc = getattr(obj, "__doc__", "") or "No description"
        if doc:
            doc = doc.split("\\n")[0][:50] + ("..." if len(doc.split("\\n")[0]) > 50 else "")

        table.add_row(name, func_type, doc)

    return table


def _show_rich_help(console):
    """Show help in Rich format."""
    help_table = Table(title="Available Commands")
    help_table.add_column("Command", style="cyan")
    help_table.add_column("Description", style="green")

    help_table.add_row("help", "Show this help message")
    help_table.add_row("list", "List available commands")
    help_table.add_row("exit / quit", "Exit the interactive shell")
    help_table.add_row("<command>", "Execute function")

    console.print(help_table)


def _execute_tui_command(app_instance, console, command: str):
    """Execute a TUI command with Rich formatting."""
    try:
        # Parse command and arguments
        parts = command.split()
        if not parts:
            return

        command_name = parts[0]
        
        if command_name not in app_instance._registry:
            console.print(f"[bold red]Command '{command_name}' not found[/bold red]")
            return

        # Execute function
        result = app_instance.execute_function(command_name)
        
        if result.is_ok():
            console.print(f"[bold green]Result:[/bold green] {result.unwrap()}")
        else:
            console.print(f"[bold red]Error:[/bold red] {result.as_error}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")