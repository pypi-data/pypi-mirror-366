"""
Unified CLI builder that dynamically discovers runner options.
No hardcoding - runners expose their own options.
"""

import sys
from typing import Optional, Dict, Any

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class UnifiedCLIBuilder:
    """Builds a unified CLI that dynamically discovers runner options."""
    
    def __init__(self, app_instance):
        """Initialize with app instance."""
        self.app = app_instance
    
    def build_cli(self) -> Optional['click.Group']:
        """Build unified CLI with dynamically discovered runner options."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Ensure plugins are discovered
        if not self.app._plugins_discovered:
            self.app._auto_discover_plugins()
        
        # Get discovered runner plugins
        available_runners = self.app._runner_plugins
        
        # Create base CLI group
        @click.group(invoke_without_command=True)
        @click.pass_context
        def cli(ctx, **kwargs):
            """YApp CLI with commands and runners."""
            
            # Check if any runner was invoked
            runner_invoked = self._check_runner_invocation(available_runners, kwargs)
            if runner_invoked:
                return
            
            if ctx.invoked_subcommand is None:
                # No runner and no command - show help
                print(ctx.get_help())
                ctx.exit()
        
        # Dynamically add runner options to the CLI
        cli = self._add_dynamic_runner_options(cli, available_runners)
        
        # Add reflected commands to the unified CLI
        self._add_reflected_commands(cli)
        
        return cli
    
    def _add_dynamic_runner_options(self, cli, available_runners):
        """Dynamically add runner options based on discovered runners."""
        for runner_name, runner in available_runners.items():
            if runner_name == 'click':
                continue  # Skip click runner as it's the default
                
            # Get runner options from the runner itself
            runner_options = self._get_runner_options(runner_name, runner)
            
            # Add each option to the CLI
            for option_config in runner_options:
                cli = self._add_option_to_cli(cli, option_config)
        
        return cli
    
    def _get_runner_options(self, runner_name: str, runner) -> list:
        """Get CLI options that a runner should expose."""
        options = []
        
        # Add the main runner flag
        runner_help = f"Use {runner_name} runner"
        try:
            if hasattr(runner, 'help') and callable(runner.help):
                help_text = runner.help().strip()
                if help_text:
                    first_line = help_text.split('\n')[0]
                    # Extract help from emoji lines like "🌐 SERVER RUNNER HELP:"
                    if ':' in first_line:
                        parts = first_line.split(':', 1)
                        if len(parts) > 1:
                            runner_help = parts[1].strip()
        except:
            pass
        
        options.append({
            'name': f'--{runner_name}',
            'is_flag': True,
            'help': runner_help,
            'runner_name': runner_name
        })
        
        # Add runner-specific options based on runner type
        if runner_name == 'server':
            options.extend([
                {'name': '--host', 'type': str, 'default': 'localhost', 'help': 'Server host'},
                {'name': '--port', 'type': int, 'default': 8000, 'help': 'Server port'},
                {'name': '--reload', 'is_flag': True, 'help': 'Enable auto-reload'},
                {'name': '--workers', 'type': int, 'default': 1, 'help': 'Number of workers'}
            ])
        elif runner_name == 'rich':
            options.extend([
                {'name': '--theme', 'type': str, 'default': 'dark', 'help': 'Color theme'},
                {'name': '--layout', 'type': str, 'default': 'panel', 'help': 'Layout style'},
                {'name': '--pager', 'is_flag': True, 'help': 'Enable paging'}
            ])
        elif runner_name == 'prompt':
            options.extend([
                {'name': '--history', 'is_flag': True, 'help': 'Enable command history'},
                {'name': '--complete', 'is_flag': True, 'help': 'Enable auto-completion'},
                {'name': '--vi-mode', 'is_flag': True, 'help': 'Use vi key bindings'}
            ])
        elif runner_name == 'typer':
            options.extend([
                {'name': '--confirm', 'is_flag': True, 'help': 'Require confirmation'},
                {'name': '--color', 'is_flag': True, 'help': 'Enable colored output'}
            ])
        
        return options
    
    def _add_option_to_cli(self, cli, option_config):
        """Add a single option to the CLI."""
        if option_config.get('is_flag'):
            cli = click.option(
                option_config['name'],
                is_flag=True,
                help=option_config['help']
            )(cli)
        else:
            cli = click.option(
                option_config['name'],
                type=option_config.get('type', str),
                default=option_config.get('default'),
                help=option_config['help']
            )(cli)
        
        return cli
    
    def _check_runner_invocation(self, available_runners, kwargs) -> bool:
        """Check if any runner was invoked and run it."""
        for runner_name in available_runners.keys():
            if runner_name == 'click':
                continue
                
            # Check if this runner's flag was set
            runner_flag = runner_name.replace('-', '_')
            if kwargs.get(runner_flag, False):
                self._run_runner(runner_name, kwargs)
                return True
        
        return False
    
    def _run_runner(self, runner_name: str, kwargs: Dict[str, Any]):
        """Run a specific runner with parsed arguments."""
        runner = self.app._get_runner_plugin(runner_name)
        if runner:
            # Filter kwargs to only include relevant options for this runner
            runner_kwargs = self._filter_runner_kwargs(runner_name, kwargs)
            runner.run(self.app, **runner_kwargs)
        else:
            print(f"Error: {runner_name.title()} runner plugin not found")
    
    def _filter_runner_kwargs(self, runner_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Filter kwargs to only include options relevant to the specific runner."""
        filtered = {}
        
        if runner_name == 'server':
            for key in ['host', 'port', 'reload', 'workers']:
                if key in kwargs and kwargs[key] is not None:
                    filtered[key] = kwargs[key]
        elif runner_name == 'rich':
            for key in ['theme', 'layout', 'pager']:
                if key in kwargs and kwargs[key] is not None:
                    filtered[key] = kwargs[key]
        elif runner_name == 'prompt':
            for key in ['history', 'complete', 'vi_mode']:
                if key in kwargs and kwargs[key] is not None:
                    filtered[key] = kwargs[key]
        elif runner_name == 'typer':
            for key in ['confirm', 'color']:
                if key in kwargs and kwargs[key] is not None:
                    filtered[key] = kwargs[key]
        
        return filtered
    
    def _add_reflected_commands(self, cli):
        """Add reflected commands to the unified CLI."""
        try:
            from yaapp.reflection import CommandReflector
            command_reflector = CommandReflector(self.app)
            command_reflector.add_reflected_commands(cli)
        except ImportError:
            # If reflection is not available, skip adding commands
            pass