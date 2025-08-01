"""
Dynamic CLI builder that discovers runner options from the runners themselves.
No hardcoding - pure discovery.
"""

import sys
from typing import Optional, Dict, Any, List

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class UnifiedCLIBuilder:
    """Builds CLI by discovering options from runners dynamically."""
    
    def __init__(self, app_instance):
        """Initialize with app instance."""
        self.app = app_instance
    
    def build_cli(self) -> Optional['click.Group']:
        """Build CLI with dynamically discovered runner options."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Ensure plugins are discovered
        if not self.app._plugins_discovered:
            self.app._auto_discover_plugins()
        
        # Get discovered runner plugins
        available_runners = self.app._runner_plugins
        
        # Discover all options from all runners
        all_options = self._discover_all_runner_options(available_runners)
        
        # Create CLI function with dynamic options
        cli_func = self._create_dynamic_cli_function(available_runners, all_options)
        
        # Apply all discovered options to the CLI function
        for option_config in reversed(all_options):  # Reverse for proper decorator order
            cli_func = self._apply_option_decorator(cli_func, option_config)
        
        # Convert to click group
        cli = click.group(invoke_without_command=True)(cli_func)
        
        # Add reflected commands
        self._add_reflected_commands(cli)
        
        return cli
    
    def _discover_all_runner_options(self, available_runners: Dict) -> List[Dict]:
        """Discover all CLI options from all runners."""
        all_options = []
        
        for runner_name, runner in available_runners.items():
            if runner_name == 'click':
                continue  # Skip click runner as it's the default
            
            # Add main runner flag
            runner_help = self._get_runner_help(runner_name, runner)
            all_options.append({
                'name': f'--{runner_name}',
                'is_flag': True,
                'help': runner_help,
                'runner_name': runner_name,
                'param_name': runner_name.replace('-', '_')
            })
            
            # Get runner-specific options
            runner_options = self._get_runner_specific_options(runner_name, runner)
            all_options.extend(runner_options)
        
        return all_options
    
    def _get_runner_help(self, runner_name: str, runner) -> str:
        """Get help text for a runner."""
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
        return runner_help
    
    def _get_runner_specific_options(self, runner_name: str, runner) -> List[Dict]:
        """Get runner-specific options by asking the runner itself."""
        options = []
        
        # First, try to get options from the runner if it has a get_cli_options method
        if hasattr(runner, 'get_cli_options') and callable(runner.get_cli_options):
            try:
                runner_options = runner.get_cli_options()
                for opt in runner_options:
                    opt['runner_name'] = runner_name
                    opt['param_name'] = opt['name'].lstrip('-').replace('-', '_')
                    options.append(opt)
                return options
            except:
                pass
        
        # Fallback: parse options from help text
        if hasattr(runner, 'help') and callable(runner.help):
            try:
                help_text = runner.help()
                options = self._parse_options_from_help(help_text, runner_name)
            except:
                pass
        
        return options
    
    def _parse_options_from_help(self, help_text: str, runner_name: str) -> List[Dict]:
        """Parse CLI options from runner help text."""
        options = []
        lines = help_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('--'):
                # Parse option line like "  --host TEXT     Server host (default: localhost)"
                parts = line.split(None, 2)  # Split into max 3 parts
                if len(parts) >= 2:
                    option_name = parts[0]  # --host
                    option_type = parts[1] if len(parts) > 1 else 'TEXT'  # TEXT
                    option_help = parts[2] if len(parts) > 2 else f"{option_name} option"  # Description
                    
                    # Determine if it's a flag or has a value
                    is_flag = (option_type == '' or 
                              'flag' in option_help.lower() or 
                              'Enable' in option_help or
                              option_type not in ['TEXT', 'INTEGER', 'INT', 'FLOAT'])
                    
                    # Extract default value if present
                    default_value = None
                    if 'default:' in option_help:
                        try:
                            default_part = option_help.split('default:')[1].split(')')[0].strip()
                            if option_type in ['INTEGER', 'INT']:
                                default_value = int(default_part)
                            elif option_type == 'FLOAT':
                                default_value = float(default_part)
                            else:
                                default_value = default_part
                        except:
                            pass
                    
                    # Determine Python type
                    py_type = str
                    if option_type in ['INTEGER', 'INT']:
                        py_type = int
                    elif option_type == 'FLOAT':
                        py_type = float
                    
                    option_config = {
                        'name': option_name,
                        'help': option_help,
                        'runner_name': runner_name,
                        'param_name': option_name.lstrip('-').replace('-', '_')
                    }
                    
                    if is_flag:
                        option_config['is_flag'] = True
                    else:
                        option_config['type'] = py_type
                        if default_value is not None:
                            option_config['default'] = default_value
                    
                    options.append(option_config)
        
        return options
    
    def _create_dynamic_cli_function(self, available_runners: Dict, all_options: List[Dict]):
        """Create the main CLI function that handles all discovered options."""
        
        @click.pass_context
        def cli(ctx, **kwargs):
            """YApp CLI with dynamically discovered runner options."""
            
            # Check if any runner was invoked
            runner_invoked = self._check_runner_invocation(available_runners, kwargs)
            if runner_invoked:
                return
            
            if ctx.invoked_subcommand is None:
                # No runner and no command - show help
                print(ctx.get_help())
                ctx.exit()
        
        return cli
    
    def _apply_option_decorator(self, func, option_config: Dict):
        """Apply a click option decorator to a function."""
        if option_config.get('is_flag'):
            return click.option(
                option_config['name'],
                is_flag=True,
                help=option_config['help']
            )(func)
        else:
            return click.option(
                option_config['name'],
                type=option_config.get('type', str),
                default=option_config.get('default'),
                help=option_config['help']
            )(func)
    
    def _check_runner_invocation(self, available_runners: Dict, kwargs: Dict) -> bool:
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
        
        # Get all options for this runner and filter kwargs
        runner = self.app._get_runner_plugin(runner_name)
        if runner:
            runner_options = self._get_runner_specific_options(runner_name, runner)
            for option in runner_options:
                param_name = option['param_name']
                if param_name in kwargs and kwargs[param_name] is not None:
                    filtered[param_name] = kwargs[param_name]
        
        return filtered
    
    def _add_reflected_commands(self, cli):
        """Add reflected commands to the CLI."""
        try:
            from yaapp.reflection import CommandReflector
            command_reflector = CommandReflector(self.app)
            command_reflector.add_reflected_commands(cli)
        except ImportError:
            # If reflection is not available, skip adding commands
            pass