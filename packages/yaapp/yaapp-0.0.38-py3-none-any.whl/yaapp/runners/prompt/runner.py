"""
Prompt TUI runner for yaapp.
Provides auto-completing interactive interface with prompt_toolkit.
"""

import inspect

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import confirm
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


def help() -> str:
    """Return Prompt runner-specific help text."""
    return """
💬 PROMPT TUI RUNNER HELP:
  --history       Enable command history
  --complete      Enable auto-completion
  --vi-mode       Use vi key bindings
    """


def run(app_instance, **kwargs):
    """Execute the Prompt runner with the app instance."""
    if not HAS_PROMPT_TOOLKIT:
        print("prompt_toolkit not available. Install with: pip install prompt_toolkit")
        return
    
    # Extract Prompt configuration
    enable_history = kwargs.get('history', True)
    enable_complete = kwargs.get('complete', True)
    vi_mode = kwargs.get('vi_mode', False)
    
    _run_interactive(app_instance, enable_history, enable_complete, vi_mode)


def _run_interactive(app_instance, enable_history: bool, enable_complete: bool, vi_mode: bool):
    """Run interactive Prompt TUI mode."""
    history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    app_name = getattr(app_instance, '_get_app_name', lambda: 'YApp')()
    
    print(f"{app_name} Interactive Shell (Prompt Toolkit)")
    print("Commands: function_name, help, list, exit/quit")
    print("Use TAB for auto-completion, UP/DOWN for history")
    print()

    while True:
        try:
            # Create completer for current context
            completer = None
            if enable_complete:
                # Get available commands from registry
                completion_words = list(app_instance._registry.keys()) + ["help", "list", "exit", "quit"]
                completer = WordCompleter(completion_words, ignore_case=True)
            
            # Get user input with completion and history
            user_input = prompt(
                f"{app_name}> ",
                completer=completer,
                history=history if enable_history else None,
                vi_mode=vi_mode
            ).strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            elif user_input.lower() == "help":
                _show_help(app_instance)
            elif user_input.lower() == "list":
                _list_commands(app_instance)
            else:
                _execute_command(app_instance, user_input)
        except (EOFError, KeyboardInterrupt):
            print("\\nGoodbye!")
            break


def _show_help(app_instance):
    """Show help."""
    print("\\nAvailable Commands:")
    print("  help          - Show this help message")
    print("  list          - List available commands")
    print("  exit / quit   - Exit the interactive shell")
    print("  <command>     - Execute function")
    print()


def _list_commands(app_instance):
    """List available commands."""
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

        print(f"  {name:<20} | {func_type:<15} | {doc}")
    print()


def _execute_command(app_instance, command: str):
    """Execute a command."""
    try:
        # Parse command and arguments
        parts = command.split()
        if not parts:
            return

        command_name = parts[0]
        
        if command_name not in app_instance._registry:
            print(f"Command '{command_name}' not found")
            return

        # Check if this is a class/object with methods (like storage)
        obj, exposer = app_instance._registry[command_name]
        
        # If it's a class or object with methods, show available methods instead of executing
        if hasattr(obj, '__dict__') or inspect.isclass(obj):
            _show_object_methods(command_name, obj)
            return

        # Execute function
        result = app_instance.execute_function(command_name)
        
        if result.is_ok():
            print(f"Result: {result.unwrap()}")
        else:
            print(f"Error: {result.as_error}")

    except Exception as e:
        print(f"Error: {str(e)}")


def _show_object_methods(name: str, obj):
    """Show available methods for an object."""
    print(f"\\n'{name}' has the following methods:")
    print(f"Usage: {name} <method> [args...]")
    print()
    
    # Get public methods
    if inspect.isclass(obj):
        methods = inspect.getmembers(obj, predicate=inspect.isfunction)
    else:
        methods = inspect.getmembers(obj, predicate=inspect.ismethod)
    
    public_methods = [(method_name, method) for method_name, method in methods if not method_name.startswith('_')]
    
    if not public_methods:
        print("  No public methods available")
        return
    
    for method_name, method in sorted(public_methods):
        doc = getattr(method, '__doc__', '') or 'No description'
        if doc:
            doc = doc.split('\\n')[0][:60] + ('...' if len(doc.split('\\n')[0]) > 60 else '')
        print(f"  {method_name:<15} - {doc}")
    
    print(f"\\nExample: {name} get --key mykey")
    print()