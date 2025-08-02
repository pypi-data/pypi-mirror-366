"""
CLI builder with hierarchical help system for runner plugins.
Implements Click callback override to provide runner-specific help.
"""

import sys
from typing import Optional

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class HierarchicalCLIBuilder:
    """Builds CLI with hierarchical help system for runner plugins."""
    
    def __init__(self, app_instance):
        """Initialize with app instance."""
        self.app = app_instance
    
    def build_cli(self) -> Optional['click.Group']:
        """Build CLI with hierarchical help system."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Custom help callback that intercepts --help and delegates to runners
        def custom_help_callback(ctx, param, value):
            """Custom help callback to intercept --help"""
            if not value or ctx.resilient_parsing:
                return
            
            # Check sys.argv for runner flags and delegate to plugin help
            if "--server" in sys.argv:
                server_runner = self.app._get_runner_plugin('server')
                if server_runner:
                    print(server_runner.help())
                else:
                    print("Server runner not available")
                ctx.exit()
            elif "--rich" in sys.argv:
                rich_runner = self.app._get_runner_plugin('rich')
                if rich_runner:
                    print(rich_runner.help())
                else:
                    print("Rich runner not available")
                ctx.exit()
            elif "--prompt" in sys.argv:
                prompt_runner = self.app._get_runner_plugin('prompt')
                if prompt_runner:
                    print(prompt_runner.help())
                else:
                    print("Prompt runner not available")
                ctx.exit()
            elif "--typer" in sys.argv:
                typer_runner = self.app._get_runner_plugin('typer')
                if typer_runner:
                    print(typer_runner.help())
                else:
                    print("Typer runner not available")
                ctx.exit()

            else:
                # Show main help with available runners
                self._show_main_help()
                ctx.exit()
        
        @click.group(invoke_without_command=True)
        @click.option('--help', '-h', is_flag=True, expose_value=False, is_eager=True,
                      callback=custom_help_callback, help='Show help message')
        @click.option('--server', is_flag=True, help='Use FastAPI web server runner')
        @click.option('--rich', is_flag=True, help='Use Rich TUI runner')
        @click.option('--prompt', is_flag=True, help='Use prompt_toolkit TUI runner')
        @click.option('--typer', is_flag=True, help='Use Typer TUI runner')
        @click.pass_context
        def cli(ctx, server, rich, prompt, typer):
            """YApp CLI with plugin-based runners."""
            
            # Ensure plugins are discovered
            if not self.app._plugins_discovered:
                self.app._auto_discover_plugins()
            
            # Handle runner selection
            if server:
                self._run_server_runner()
                ctx.exit()
            elif rich:
                self._run_rich_runner()
                ctx.exit()
            elif prompt:
                self._run_prompt_runner()
                ctx.exit()
            elif typer:
                self._run_typer_runner()
                ctx.exit()
            elif ctx.invoked_subcommand is None:
                # No runner specified and no command - use default Click runner
                self._run_click_runner()
                ctx.exit()
        
        # Add reflected commands to the hierarchical CLI
        # This allows users to run: python app.py <command>
        self._add_reflected_commands(cli)
        
        return cli
    
    def _show_main_help(self):
        """Show main help with available runners."""
        print("📋 MAIN HELP:")
        print("Available runners:")
        print("  (default)       Click CLI runner (no flag needed)")
        
        # Show available runners
        available_runners = list(self.app._runner_plugins.keys())
        for runner_name in sorted(available_runners):
            if runner_name == 'server':
                print("  --server        Use FastAPI web server runner")
            elif runner_name == 'rich':
                print("  --rich          Use Rich TUI runner")
            elif runner_name == 'prompt':
                print("  --prompt        Use prompt_toolkit TUI runner")
            elif runner_name == 'typer':
                print("  --typer         Use Typer TUI runner")

        
        print("\nUse --<runner> --help for runner-specific options")
        print("Example: python app.py --server --help")
        print("Default: python app.py (uses Click CLI runner)")
    
    def _add_reflected_commands(self, cli):
        """Add reflected commands to the hierarchical CLI."""
        # Import here to avoid circular imports
        try:
            from yaapp.reflection import CommandReflector
            command_reflector = CommandReflector(self.app)
            command_reflector.add_reflected_commands(cli)
        except ImportError:
            # If reflection is not available, skip adding commands
            pass
    
    def _run_server_runner(self):
        """Run server runner with parsed arguments."""
        server_runner = self.app._get_runner_plugin('server')
        if server_runner:
            # Parse server-specific arguments from sys.argv
            kwargs = self._parse_server_args()
            server_runner.run(self.app, **kwargs)
        else:
            print("Error: Server runner plugin not found")
    
    def _run_rich_runner(self):
        """Run Rich TUI runner with parsed arguments."""
        rich_runner = self.app._get_runner_plugin('rich')
        if rich_runner:
            # Parse rich-specific arguments from sys.argv
            kwargs = self._parse_rich_args()
            rich_runner.run(self.app, **kwargs)
        else:
            print("Error: Rich runner plugin not found")
    
    def _run_prompt_runner(self):
        """Run Prompt TUI runner with parsed arguments."""
        prompt_runner = self.app._get_runner_plugin('prompt')
        if prompt_runner:
            # Parse prompt-specific arguments from sys.argv
            kwargs = self._parse_prompt_args()
            prompt_runner.run(self.app, **kwargs)
        else:
            print("Error: Prompt runner plugin not found")
    
    def _run_typer_runner(self):
        """Run Typer TUI runner with parsed arguments."""
        typer_runner = self.app._get_runner_plugin('typer')
        if typer_runner:
            # Parse typer-specific arguments from sys.argv
            kwargs = self._parse_typer_args()
            typer_runner.run(self.app, **kwargs)
        else:
            print("Error: Typer runner plugin not found")
    
    def _run_click_runner(self):
        """Run Click CLI runner with parsed arguments."""
        click_runner = self.app._get_runner_plugin('click')
        if click_runner:
            # Parse click-specific arguments from sys.argv
            kwargs = self._parse_click_args()
            click_runner.run(self.app, **kwargs)
        else:
            print("Error: Click runner plugin not found")
    
    def _parse_server_args(self):
        """Parse server-specific arguments from sys.argv."""
        kwargs = {}
        
        # Parse --host
        if '--host' in sys.argv:
            try:
                host_index = sys.argv.index('--host')
                if host_index + 1 < len(sys.argv):
                    kwargs['host'] = sys.argv[host_index + 1]
            except (ValueError, IndexError):
                pass
        
        # Parse --port
        if '--port' in sys.argv:
            try:
                port_index = sys.argv.index('--port')
                if port_index + 1 < len(sys.argv):
                    kwargs['port'] = int(sys.argv[port_index + 1])
            except (ValueError, IndexError):
                pass
        
        # Parse --reload
        if '--reload' in sys.argv:
            kwargs['reload'] = True
        
        # Parse --workers
        if '--workers' in sys.argv:
            try:
                workers_index = sys.argv.index('--workers')
                if workers_index + 1 < len(sys.argv):
                    kwargs['workers'] = int(sys.argv[workers_index + 1])
            except (ValueError, IndexError):
                pass
        
        return kwargs
    
    def _parse_rich_args(self):
        """Parse Rich-specific arguments from sys.argv."""
        kwargs = {}
        
        # Parse --theme
        if '--theme' in sys.argv:
            try:
                theme_index = sys.argv.index('--theme')
                if theme_index + 1 < len(sys.argv):
                    kwargs['theme'] = sys.argv[theme_index + 1]
            except (ValueError, IndexError):
                pass
        
        # Parse --layout
        if '--layout' in sys.argv:
            try:
                layout_index = sys.argv.index('--layout')
                if layout_index + 1 < len(sys.argv):
                    kwargs['layout'] = sys.argv[layout_index + 1]
            except (ValueError, IndexError):
                pass
        
        # Parse --pager
        if '--pager' in sys.argv:
            kwargs['pager'] = True
        
        return kwargs
    
    def _parse_prompt_args(self):
        """Parse Prompt-specific arguments from sys.argv."""
        kwargs = {}
        
        # Parse --history
        if '--history' in sys.argv:
            kwargs['history'] = True
        
        # Parse --complete
        if '--complete' in sys.argv:
            kwargs['complete'] = True
        
        # Parse --vi-mode
        if '--vi-mode' in sys.argv:
            kwargs['vi_mode'] = True
        
        return kwargs
    
    def _parse_typer_args(self):
        """Parse Typer-specific arguments from sys.argv."""
        kwargs = {}
        
        # Parse --confirm
        if '--confirm' in sys.argv:
            kwargs['confirm'] = True
        
        # Parse --color
        if '--color' in sys.argv:
            kwargs['color'] = True
        
        return kwargs
    
    def _parse_click_args(self):
        """Parse Click-specific arguments from sys.argv."""
        kwargs = {}
        
        # Parse --verbose
        if '--verbose' in sys.argv:
            kwargs['verbose'] = True
        
        # Parse --quiet
        if '--quiet' in sys.argv:
            kwargs['quiet'] = True
        
        # Parse --interactive
        if '--interactive' in sys.argv:
            kwargs['interactive'] = True
        
        return kwargs