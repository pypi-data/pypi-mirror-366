"""
Unified CLI builder that shows both commands and runners in a single interface.
Final working version.
"""

import sys
from typing import Optional

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class UnifiedCLIBuilder:
    """Builds a unified CLI that shows both commands and runners."""
    
    def __init__(self, app_instance):
        """Initialize with app instance."""
        self.app = app_instance
    
    def build_cli(self) -> Optional['click.Group']:
        """Build unified CLI with both commands and runners."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Ensure plugins are discovered
        if not self.app._plugins_discovered:
            self.app._auto_discover_plugins()
        
        # Get discovered runner plugins (excluding 'click' as it's the default)
        available_runners = {name: runner for name, runner in self.app._runner_plugins.items() if name != 'click'}
        
        # We'll handle runner-specific help differently
        
        # Create the base CLI group with hardcoded runner options
        # This is the only way to make Click recognize them properly
        if 'server' in available_runners:
            server_help = "Use FastAPI web server runner"
            try:
                server_runner_help = available_runners['server'].help().strip()
                if server_runner_help:
                    first_line = server_runner_help.split('\n')[0]
                    if first_line.startswith('🌐'):
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            server_help = parts[1].strip()
            except:
                pass
        else:
            server_help = "Use FastAPI web server runner"
            
        if 'rich' in available_runners:
            rich_help = "Use Rich TUI runner"
            try:
                rich_runner_help = available_runners['rich'].help().strip()
                if rich_runner_help:
                    first_line = rich_runner_help.split('\n')[0]
                    if first_line.startswith('🎨'):
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            rich_help = parts[1].strip()
            except:
                pass
        else:
            rich_help = "Use Rich TUI runner"
            
        if 'prompt' in available_runners:
            prompt_help = "Use prompt_toolkit TUI runner"
            try:
                prompt_runner_help = available_runners['prompt'].help().strip()
                if prompt_runner_help:
                    first_line = prompt_runner_help.split('\n')[0]
                    if first_line.startswith('💬'):
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            prompt_help = parts[1].strip()
            except:
                pass
        else:
            prompt_help = "Use prompt_toolkit TUI runner"
            
        if 'typer' in available_runners:
            typer_help = "Use Typer TUI runner"
            try:
                typer_runner_help = available_runners['typer'].help().strip()
                if typer_runner_help:
                    first_line = typer_runner_help.split('\n')[0]
                    if first_line.startswith('⌨️'):
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            typer_help = parts[1].strip()
            except:
                pass
        else:
            typer_help = "Use Typer TUI runner"
        
        # Create the CLI with all available runner options
        @click.group(invoke_without_command=True)
        @click.option('--server', is_flag=True, help=server_help)
        @click.option('--rich', is_flag=True, help=rich_help)
        @click.option('--prompt', is_flag=True, help=prompt_help)
        @click.option('--typer', is_flag=True, help=typer_help)
        @click.pass_context
        def cli(ctx, server=False, rich=False, prompt=False, typer=False, **kwargs):
            """YApp CLI with commands and runners."""
            

            
            # Handle runner selection
            if server:
                self._run_runner('server')
                ctx.exit()
            elif rich:
                self._run_runner('rich')
                ctx.exit()
            elif prompt:
                self._run_runner('prompt')
                ctx.exit()
            elif typer:
                self._run_runner('typer')
                ctx.exit()
            
            if ctx.invoked_subcommand is None:
                # No runner and no command - show help (same as --help)
                print(ctx.get_help())
                ctx.exit()
        
        # Add reflected commands to the unified CLI
        self._add_reflected_commands(cli)
        
        # Override the help formatting to add runners section
        self._customize_help_formatting(cli, available_runners)
        
        return cli
    
    def _show_unified_help(self, ctx):
        """Show unified help with both commands and runners."""
        # Get the formatted help from Click
        help_text = ctx.get_help()
        
        # Print the unified help
        print(help_text)
    
    def _customize_help_formatting(self, cli, available_runners):
        """Customize the help formatting - remove duplicate runners section."""
        # Don't add a separate runners section since the options already show the runners
        # The runner options in the Options section are sufficient
        pass
    
    def _add_reflected_commands(self, cli):
        """Add reflected commands to the unified CLI."""
        try:
            from yaapp.reflection import CommandReflector
            command_reflector = CommandReflector(self.app)
            command_reflector.add_reflected_commands(cli)
        except ImportError:
            # If reflection is not available, skip adding commands
            pass
    
    def _run_runner(self, runner_name: str):
        """Run a specific runner with parsed arguments."""
        runner = self.app._get_runner_plugin(runner_name)
        if runner:
            kwargs = self._parse_runner_args(runner_name)
            runner.run(self.app, **kwargs)
        else:
            print(f"Error: {runner_name.title()} runner plugin not found")
    
    def _parse_runner_args(self, runner_name: str):
        """Parse runner-specific arguments from sys.argv."""
        if runner_name == 'server':
            return self._parse_server_args()
        elif runner_name == 'rich':
            return self._parse_rich_args()
        elif runner_name == 'prompt':
            return self._parse_prompt_args()
        elif runner_name == 'typer':
            return self._parse_typer_args()
        else:
            # For unknown runners, return empty kwargs
            return {}
    
    def _parse_server_args(self):
        """Parse server-specific arguments from sys.argv."""
        kwargs = {}
        
        if '--host' in sys.argv:
            try:
                host_index = sys.argv.index('--host')
                if host_index + 1 < len(sys.argv):
                    kwargs['host'] = sys.argv[host_index + 1]
            except (ValueError, IndexError):
                pass
        
        if '--port' in sys.argv:
            try:
                port_index = sys.argv.index('--port')
                if port_index + 1 < len(sys.argv):
                    kwargs['port'] = int(sys.argv[port_index + 1])
            except (ValueError, IndexError):
                pass
        
        if '--reload' in sys.argv:
            kwargs['reload'] = True
        
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
        
        if '--theme' in sys.argv:
            try:
                theme_index = sys.argv.index('--theme')
                if theme_index + 1 < len(sys.argv):
                    kwargs['theme'] = sys.argv[theme_index + 1]
            except (ValueError, IndexError):
                pass
        
        if '--layout' in sys.argv:
            try:
                layout_index = sys.argv.index('--layout')
                if layout_index + 1 < len(sys.argv):
                    kwargs['layout'] = sys.argv[layout_index + 1]
            except (ValueError, IndexError):
                pass
        
        if '--pager' in sys.argv:
            kwargs['pager'] = True
        
        return kwargs
    
    def _parse_prompt_args(self):
        """Parse Prompt-specific arguments from sys.argv."""
        kwargs = {}
        
        if '--history' in sys.argv:
            kwargs['history'] = True
        
        if '--complete' in sys.argv:
            kwargs['complete'] = True
        
        if '--vi-mode' in sys.argv:
            kwargs['vi_mode'] = True
        
        return kwargs
    
    def _parse_typer_args(self):
        """Parse Typer-specific arguments from sys.argv."""
        kwargs = {}
        
        if '--confirm' in sys.argv:
            kwargs['confirm'] = True
        
        if '--color' in sys.argv:
            kwargs['color'] = True
        
        return kwargs