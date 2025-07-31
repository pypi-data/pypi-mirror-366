"""
Click TUI runner for yaapp.
"""

import sys
from .base import BaseRunner

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class ClickRunner(BaseRunner):
    """Click-based TUI runner."""
    
    def run(self):
        """Run TUI using click with proper command structure and reflection."""
        if not HAS_CLICK:
            print("click not available. Install with: pip install click")
            return

        from ..reflection import ClickReflection
        reflection = ClickReflection(self.core)
        
        # Create a comprehensive click CLI with object reflection
        cli = reflection.create_reflective_cli()
        if cli:
            # Start click in interactive mode
            old_argv = sys.argv
            try:
                print("YApp Interactive Shell (Click)")
                print("Use --help for any command to see options")
                print("Available commands: help, list, server, tui, run, plus all exposed functions")
                print()

                while True:
                    try:
                        user_input = input(f"{self.core._get_app_name()}> ").strip()
                        if not user_input:
                            continue

                        if user_input.lower() in ["exit", "quit"]:
                            print("Goodbye!")
                            break

                        # Parse command and execute through click
                        sys.argv = [self.core._get_app_name()] + user_input.split()
                        try:
                            cli()
                        except SystemExit:
                            # Click calls sys.exit(), we want to continue the loop
                            pass
                        except Exception as e:
                            print(f"Error: {e}")

                    except (EOFError, KeyboardInterrupt):
                        print("\nGoodbye!")
                        break
            finally:
                sys.argv = old_argv