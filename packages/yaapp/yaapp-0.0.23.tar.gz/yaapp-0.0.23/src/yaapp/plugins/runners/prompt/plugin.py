"""
Prompt TUI runner plugin for yaapp.
Provides auto-completing interactive interface with prompt_toolkit.
"""

import inspect
# Import will be done dynamically to avoid circular imports

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import confirm
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

from yaapp import yaapp


@yaapp.expose("prompt")
class PromptRunner:
    """Prompt_toolkit-based TUI runner with auto-completion."""
    
    def __init__(self, config=None):
        """Initialize Prompt runner with optional configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        self.history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    
    def help(self) -> str:
        """Return Prompt runner-specific help text."""
        return """
💬 PROMPT TUI RUNNER HELP:
  --history       Enable command history
  --complete      Enable auto-completion
  --vi-mode       Use vi key bindings
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the Prompt runner with the app instance."""
        if not HAS_PROMPT_TOOLKIT:
            print("prompt_toolkit not available. Install with: pip install prompt_toolkit")
            return
        
        self.yaapp = app_instance
        
        # Extract Prompt configuration
        enable_history = kwargs.get('history', self.config.get('history', True))
        enable_complete = kwargs.get('complete', self.config.get('complete', True))
        vi_mode = kwargs.get('vi_mode', self.config.get('vi_mode', False))
        
        self._run_interactive(enable_history, enable_complete, vi_mode)
    
    def _run_interactive(self, enable_history: bool, enable_complete: bool, vi_mode: bool):
        """Run interactive Prompt TUI mode."""
        app_name = self.yaapp._get_app_name()
        print(f"{app_name} Interactive Shell (Prompt Toolkit)")
        print("Commands: function_name, help, list, back/.., exit/quit")
        print("Use TAB for auto-completion, UP/DOWN for history")
        print()

        while True:
            try:
                # Get current context for prompt and completion
                context_path = getattr(self.yaapp, '_current_context', [])
                context_str = ":".join(context_path) if context_path else app_name
                
                # Create completer for current context
                completer = None
                if enable_complete:
                    current_commands = self.yaapp._get_current_context_commands()
                    completion_words = list(current_commands.keys()) + ["help", "list", "back", "..", "exit", "quit"]
                    completer = WordCompleter(completion_words, ignore_case=True)
                
                # Get user input with completion and history
                user_input = prompt(
                    f"{context_str}> ",
                    completer=completer,
                    history=self.history if enable_history else None,
                    vi_mode=vi_mode
                ).strip()
                
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                elif user_input.lower() == "help":
                    self._show_contextual_help()
                elif user_input.lower() == "list":
                    self._list_current_commands()
                elif user_input.lower() in ["back", "..", "cd .."]:
                    if self.yaapp._exit_context():
                        context_path = getattr(self.yaapp, '_current_context', [])
                        context_str = ':'.join(context_path) if context_path else 'root'
                        print(f"Moved to {context_str}")
                        self._list_current_commands()
                    else:
                        print("Already at root level")
                else:
                    if not self._handle_contextual_command(user_input):
                        self._execute_tui_command(user_input)
            except (EOFError, KeyboardInterrupt):
                print("\\nGoodbye!")
                break
    
    def _handle_contextual_command(self, command: str) -> bool:
        """Handle contextual navigation for Prompt TUI."""
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
                print(f"Entered {context_str} context")
                self._list_current_commands()
                return True

        return False  # Let normal command execution handle it
    
    def _show_contextual_help(self) -> None:
        """Show contextual help."""
        print("\\nAvailable Commands:")
        print("  help          - Show this help message")
        print("  list          - List available commands in current context")
        print("  back / ..     - Go back to parent context")
        print("  exit / quit   - Exit the interactive shell")
        print("  <command>     - Execute function or navigate to context")

        context_path = getattr(self.yaapp, '_current_context', [])
        if context_path:
            print(f"\\nCurrent context: {':'.join(context_path)}")
        else:
            print("\\nCurrent context: root")

        current_commands = self.yaapp._get_current_context_commands()
        if current_commands:
            leaf_commands = [name for name in current_commands.keys() if self.yaapp._is_leaf_command(name)]
            nav_commands = [name for name in current_commands.keys() if not self.yaapp._is_leaf_command(name)]

            if leaf_commands:
                print(f"\\nExecutable commands: {', '.join(sorted(leaf_commands))}")
            if nav_commands:
                print(f"Navigation commands: {', '.join(sorted(nav_commands))}")
        print()
    
    def _list_current_commands(self):
        """List commands in current context."""
        current_commands = self.yaapp._get_current_context_commands()
        context_path = getattr(self.yaapp, '_current_context', [])
        context_str = ":".join(context_path) if context_path else "root"
        
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

            print(f"  {name:<20} | {func_type:<15} | {doc}")
        print()
    
    def _execute_tui_command(self, command: str):
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
                print(f"Command '{command_name}' not found")
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
                print(f"Result: {result}")
            else:
                print("Command executed successfully")

        except Exception as e:
            print(f"Error: {str(e)}")