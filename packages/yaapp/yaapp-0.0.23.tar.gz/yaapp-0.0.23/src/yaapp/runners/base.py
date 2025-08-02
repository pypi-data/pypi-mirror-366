"""
Base runner class for yaapp runners.
"""

import inspect
from abc import ABC, abstractmethod


class BaseRunner(ABC):
    """Base class for all yaapp runners."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
    
    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the interface."""
        pass
    
    def _show_current_context_info(self) -> None:
        """Show information about the current context."""
        current_commands = self.core._get_current_context_commands()
        context_path = self.core._context_tree.get_current_context_path()
        if context_path:
            print(f"Current context: {':'.join(context_path)}")
        else:
            print("Current context: root")
        print("Available commands:", ", ".join(sorted(current_commands.keys())))
        print()

    def _list_current_context(self) -> None:
        """List commands available in current context."""
        current_commands = self.core._get_current_context_commands()

        if not current_commands:
            print("No commands available in current context.")
            return

        print("Available commands:")
        for name, obj in sorted(current_commands.items()):
            obj_type = "function"
            if inspect.isclass(obj):
                obj_type = "class (has subcommands)"
            elif not self.core._is_leaf_command(name):
                obj_type = "namespace (has subcommands)"

            doc = getattr(obj, "__doc__", "") or "No description"
            if doc:
                doc = doc.split("\n")[0][:50] + (
                    "..." if len(doc.split("\n")[0]) > 50 else ""
                )

            print(f"  {name:<20} | {obj_type:<25} | {doc}")

    def _show_contextual_help(self) -> None:
        """Show help for current context."""
        print("Available commands:")
        print("  help    - Show this help message")
        print("  list    - List available commands in current context")
        print("  back    - Go back to parent context (alias: .. or 'cd ..')")
        print("  exit    - Exit the interactive shell")
        print("  quit    - Exit the interactive shell")
        print()

        context_path = self.core._context_tree.get_current_context_path()
        if context_path:
            print(f"Current context: {':'.join(context_path)}")
            current_commands = self.core._get_current_context_commands()
        else:
            print("Current context: root (all functions and objects)")
            current_commands = self.core._get_current_context_commands()

        print("\nTo execute commands:")
        print("  • Enter command name to execute (if it's a function)")
        print("  • Enter command name to navigate (if it has subcommands)")
        print("  • Use --param=value for parameters")
        print("  • Use --flag for boolean parameters")

        if current_commands:
            leaf_commands = [
                name for name in current_commands.keys() if self.core._is_leaf_command(name)
            ]
            nav_commands = [
                name
                for name in current_commands.keys()
                if not self.core._is_leaf_command(name)
            ]

            if leaf_commands:
                print(f"\nExecutable commands: {', '.join(sorted(leaf_commands))}")
            if nav_commands:
                print(f"Navigation commands: {', '.join(sorted(nav_commands))}")

    def _handle_contextual_command(self, command: str) -> bool:
        """Handle contextual navigation. Returns True if command was handled."""
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
                context_path = self.core._context_tree.get_current_context_path()
                print(f"Entered {':'.join(context_path)} context")
                self._show_current_context_info()
                return True

        return False  # Let normal command execution handle it