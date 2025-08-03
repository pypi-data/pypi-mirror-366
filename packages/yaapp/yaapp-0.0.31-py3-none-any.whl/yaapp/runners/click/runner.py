"""
Click runner for yaapp.
Provides the default CLI interface with interactive shell capabilities.
"""

import sys

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


def help() -> str:
    """Return Click runner-specific help text."""
    return """
🖱️ CLICK CLI RUNNER HELP:
  --verbose       Enable verbose output
  --quiet         Suppress output
  --interactive   Start interactive shell mode
    """


def run(app_instance, **kwargs):
    """Execute the Click runner with the app instance."""
    if not HAS_CLICK:
        print("click not available. Install with: pip install click")
        return
    
    # Check if interactive mode is requested
    if kwargs.get('interactive', False):
        _run_interactive(app_instance, **kwargs)
    else:
        _run_standard(app_instance, **kwargs)


def _run_standard(app_instance, **kwargs):
    """Run standard Click CLI mode."""
    # Create a simple CLI with reflected commands (not hierarchical)
    cli = _create_simple_cli(app_instance)
    if cli:
        # Execute the CLI normally
        cli()


def _create_simple_cli(app_instance):
    """Create a unified CLI with all runner options and reflected commands."""
    if not HAS_CLICK:
        return None
    
    # Use the unified CLI builder for full functionality
    from yaapp.unified_cli_builder import UnifiedCLIBuilder
    
    builder = UnifiedCLIBuilder(app_instance)
    cli = builder.build_cli()
    
    return cli


def _run_interactive(app_instance, **kwargs):
    """Run interactive Click shell mode."""
    # Create a simple CLI with reflected commands
    cli = _create_simple_cli(app_instance)
    if cli:
        # Start click in interactive mode
        old_argv = sys.argv
        try:
            print("YApp Interactive Shell (Click)")
            print("Use --help for any command to see options")
            print("Available commands: help, plus all exposed functions")
            print()

            while True:
                try:
                    user_input = input(f"{app_instance._get_app_name()}> ").strip()
                    if not user_input:
                        continue

                    if user_input.lower() in ["exit", "quit"]:
                        print("Goodbye!")
                        break

                    # Parse command and execute through click
                    sys.argv = [app_instance._get_app_name()] + user_input.split()
                    try:
                        cli()
                    except SystemExit:
                        # Click calls sys.exit(), we want to continue the loop
                        pass
                    except Exception as e:
                        print(f"Error: {e}")

                except (EOFError, KeyboardInterrupt):
                    print("\\nGoodbye!")
                    break
        finally:
            sys.argv = old_argv