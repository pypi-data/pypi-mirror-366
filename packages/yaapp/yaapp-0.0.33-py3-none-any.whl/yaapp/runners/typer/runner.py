"""
Typer TUI runner for yaapp.
Provides simple interactive mode with basic TUI features.
"""

import inspect

try:
    import typer
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False


def help() -> str:
    """Return Typer runner-specific help text."""
    return """
⌨️ TYPER TUI RUNNER HELP:
  --confirm       Require confirmation for destructive operations
  --color         Enable colored output
    """


def run(app_instance, **kwargs):
    """Execute the Typer runner with the app instance."""
    if not HAS_TYPER:
        print("typer not available. Install with: pip install typer")
        return
    
    # Extract Typer configuration
    confirm = kwargs.get('confirm', False)
    color = kwargs.get('color', True)
    
    _run_interactive(app_instance, confirm, color)


def _run_interactive(app_instance, confirm: bool, color: bool):
    """Run interactive Typer TUI mode."""
    app_name = getattr(app_instance, '_get_app_name', lambda: 'YApp')()
    
    if color:
        typer.secho(f"{app_name} Interactive Shell (Typer)", fg=typer.colors.BLUE, bold=True)
    else:
        print(f"{app_name} Interactive Shell (Typer)")
    
    print("Commands: function_name, help, list, exit/quit")
    print()

    while True:
        try:
            user_input = input(f"{app_name}> ").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                if color:
                    typer.secho("Goodbye!", fg=typer.colors.GREEN)
                else:
                    print("Goodbye!")
                break
            elif user_input.lower() == "help":
                _show_help(color)
            elif user_input.lower() == "list":
                _list_commands(app_instance, color)
            else:
                _execute_command(app_instance, user_input, confirm, color)
        except (EOFError, KeyboardInterrupt):
            if color:
                typer.secho("\\nGoodbye!", fg=typer.colors.GREEN)
            else:
                print("\\nGoodbye!")
            break


def _show_help(color: bool):
    """Show help."""
    if color:
        typer.secho("\\nAvailable Commands:", fg=typer.colors.CYAN, bold=True)
    else:
        print("\\nAvailable Commands:")
    
    print("  help          - Show this help message")
    print("  list          - List available commands")
    print("  exit / quit   - Exit the interactive shell")
    print("  <command>     - Execute function")
    print()


def _list_commands(app_instance, color: bool):
    """List available commands."""
    if color:
        typer.secho("\\nAvailable Commands:", fg=typer.colors.CYAN, bold=True)
    else:
        print("\\nAvailable Commands:")
    
    if not app_instance._registry:
        print("  No commands available")
        return
    
    for name, (obj, exposer) in sorted(app_instance._registry.items()):
        func_type = "Function"
        if inspect.isclass(obj):
            func_type = "Class"
        elif hasattr(obj, '__call__'):
            func_type = "Callable"

        doc = getattr(obj, "__doc__", "") or "No description"
        if doc:
            doc = doc.split("\\n")[0][:60] + ("..." if len(doc.split("\\n")[0]) > 60 else "")

        if color:
            typer.secho(f"  {name:<20}", fg=typer.colors.CYAN, nl=False)
            typer.secho(f" | {func_type:<15}", fg=typer.colors.MAGENTA, nl=False)
            typer.secho(f" | {doc}", fg=typer.colors.GREEN)
        else:
            print(f"  {name:<20} | {func_type:<15} | {doc}")
    print()


def _execute_command(app_instance, command: str, confirm: bool, color: bool):
    """Execute a command."""
    try:
        # Parse command and arguments
        parts = command.split()
        if not parts:
            return

        command_name = parts[0]
        
        if command_name not in app_instance._registry:
            if color:
                typer.secho(f"Command '{command_name}' not found", fg=typer.colors.RED)
            else:
                print(f"Command '{command_name}' not found")
            return

        # Check for confirmation if enabled
        if confirm:
            if not typer.confirm(f"Execute '{command}'?"):
                if color:
                    typer.secho("Command cancelled", fg=typer.colors.YELLOW)
                else:
                    print("Command cancelled")
                return

        # Execute function
        result = app_instance.execute_function(command_name)
        
        if result.is_ok():
            if color:
                typer.secho(f"Result: {result.unwrap()}", fg=typer.colors.GREEN)
            else:
                print(f"Result: {result.unwrap()}")
        else:
            if color:
                typer.secho(f"Error: {result.as_error}", fg=typer.colors.RED)
            else:
                print(f"Error: {result.as_error}")

    except Exception as e:
        if color:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
        else:
            print(f"Error: {str(e)}")