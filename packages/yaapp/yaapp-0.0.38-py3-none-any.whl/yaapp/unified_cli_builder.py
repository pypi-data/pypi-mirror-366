"""
Dynamic CLI builder with runners as options and plugin methods as subcommands.
"""

import sys
import inspect
from typing import Optional, Dict, Any, List

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class UnifiedCLIBuilder:
    """Builds CLI with runners as options and plugin methods as subcommands."""
    
    def __init__(self, app_instance):
        """Initialize with app instance."""
        self.app = app_instance
    
    def _get_available_runners(self) -> Dict[str, Any]:
        """Get all available runners from the new discovery system."""
        if hasattr(self.app, '_runner_discovery'):
            # Get both discovered and available runners
            discovered = self.app._runner_discovery._discovered_runners
            available_paths = getattr(self.app._runner_discovery, '_available_runner_paths', {})
            
            # Combine discovered runners with available paths
            all_runners = {}
            all_runners.update(discovered)
            for name in available_paths.keys():
                if name not in discovered:
                    all_runners[name] = None  # Placeholder for lazy loading
            
            return all_runners
        return {}
    
    def build_cli(self) -> Optional['click.Group']:
        """Build hierarchical CLI with runners as options and plugin methods as subcommands."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Check for --plugin argument in sys.argv to load showcase plugin early
        import sys
        if '--plugin' in sys.argv or '-p' in sys.argv:
            try:
                plugin_index = sys.argv.index('--plugin') if '--plugin' in sys.argv else sys.argv.index('-p')
                if plugin_index + 1 < len(sys.argv):
                    plugin_name = sys.argv[plugin_index + 1]
                    if not plugin_name.startswith('-'):  # Make sure it's not another option
                        self.app._load_showcase_plugin(plugin_name)
            except (IndexError, ValueError):
                pass
        
        # Check for --suite argument to load all plugins
        elif '--suite' in sys.argv or '-s' in sys.argv:
            self.app._load_complete_suite()
        
        # Ensure plugins are discovered (if not using --plugin)
        if not self.app._plugins_discovered:
            self.app._auto_discover_plugins()
        
        # Get runner plugins and commands from registry
        available_runners = self._get_available_runners()
        available_commands = self._get_available_commands(available_runners)
        
        # Create main CLI group with runner options and global options
        cli = self._create_main_cli_group(available_runners, available_commands)
        
        # Add plugin commands as subgroups
        self._add_plugin_commands(cli, available_commands, available_runners)
        
        return cli
    
    def _create_main_cli_group(self, available_runners: Dict, available_commands: List[str]):
        """Create main CLI group with runner options."""
        # Create base group
        @click.group(invoke_without_command=True)
        @click.option('--verbose', '-v', is_flag=True, help='Verbose output')
        @click.option('--config', '-c', help='Configuration file path')
        @click.option('--plugin', '-p', help='Load specific built-in plugin (e.g., storage, docker)')
        @click.option('--suite', '-s', is_flag=True, help='Load complete plugin suite (all plugins as root commands)')
        @click.option('--list-plugins', '-l', is_flag=True, help='List all available built-in plugins')
        @click.option('--version', is_flag=True, help='Show version and exit')
        @click.pass_context
        def cli(ctx, verbose, config, plugin, suite, list_plugins, version, **runner_kwargs):
            """Yet Another App - CLI and Web API framework"""
            # Store global options in context
            ctx.ensure_object(dict)
            ctx.obj['verbose'] = verbose
            ctx.obj['config'] = config
            ctx.obj['plugin'] = plugin
            ctx.obj['suite'] = suite
            ctx.obj['list_plugins'] = list_plugins
            ctx.obj['version'] = version
            ctx.obj.update(runner_kwargs)
            
            # Handle --version option
            if version:
                from yaapp import __version__
                print(f"yaapp {__version__}")
                ctx.exit()
            
            # Handle --list-plugins option
            if list_plugins:
                self.app._list_available_plugins()
                ctx.exit()
            
            # Check if a runner was selected
            selected_runner = None
            for runner_name in available_runners.keys():
                if runner_name != 'click' and ctx.obj.get(runner_name, False):
                    selected_runner = runner_name
                    break
            
            if ctx.invoked_subcommand is None:
                if selected_runner:
                    # Run the selected runner
                    self.app.run_runner(selected_runner, **runner_kwargs)
                else:
                    # Root invocation - show help
                    self._show_main_help(available_runners, available_commands)
        
        # Add runner options (excluding click as it's default)
        for runner_name in available_runners.keys():
            if runner_name != 'click':  # Skip click as it's default
                cli = click.option(f'--{runner_name}', is_flag=True, help=f'Use {runner_name} runner')(cli)
        
        return cli
    
    def _add_plugin_commands(self, cli, available_commands: List[str], available_runners: Dict):
        """Add plugin commands as subgroups with their methods as subcommands."""
        for cmd_name in available_commands:
            # Get the plugin object from registry
            if cmd_name in self.app._registry:
                obj, exposer = self.app._registry[cmd_name]
                
                # Get plugin description for help
                description = self._get_plugin_description(cmd_name)
                
                # Create command group for this plugin
                plugin_group = self._create_plugin_command_group(cmd_name, obj, available_runners, description)
                
                # Add plugin methods as subcommands
                self._add_plugin_methods_as_subcommands(plugin_group, obj, cmd_name)
                
                # Add to main CLI
                cli.add_command(plugin_group, name=cmd_name)
    
    def _create_plugin_command_group(self, cmd_name: str, obj: Any, available_runners: Dict, description: str):
        """Create a command group for a plugin with runner options."""
        
        @click.group(invoke_without_command=True, help=description)
        @click.pass_context
        def plugin_group(ctx, **runner_kwargs):
            # Store runner options in context
            ctx.ensure_object(dict)
            ctx.obj.update(runner_kwargs)
            
            # Check if a runner was selected
            selected_runner = None
            for runner_name in available_runners.keys():
                if runner_name != 'click' and ctx.obj.get(runner_name, False):
                    selected_runner = runner_name
                    break
            
            if ctx.invoked_subcommand is None:
                if selected_runner:
                    # Run the plugin via the selected runner
                    self.app.run_runner(selected_runner, command=cmd_name, **runner_kwargs)
                else:
                    # Show plugin help
                    self._show_plugin_help(cmd_name, obj, available_runners)
        
        # Set the docstring dynamically
        plugin_group.__doc__ = description
        
        # Add runner options (excluding click as it's default)
        for runner_name in available_runners.keys():
            if runner_name != 'click':  # Skip click as it's default
                plugin_group = click.option(f'--{runner_name}', is_flag=True, help=f'Use {runner_name} runner')(plugin_group)
        
        return plugin_group
    
    def _add_plugin_methods_as_subcommands(self, group, obj, plugin_name: str):
        """Add plugin methods as CLI subcommands."""
        import inspect
        
        # Get public methods from the object
        if inspect.isclass(obj):
            # For classes, get methods from the class
            methods = inspect.getmembers(obj, predicate=inspect.isfunction)
        else:
            # For instances, get methods from the instance
            methods = inspect.getmembers(obj, predicate=inspect.ismethod)
        
        for method_name, method in methods:
            # Skip private methods and special methods
            if method_name.startswith('_'):
                continue
            
            # Create click command for this method
            cmd = self._create_method_command(method, method_name, plugin_name)
            group.add_command(cmd, name=method_name)
    
    def _create_method_command(self, method, method_name: str, plugin_name: str):
        """Create a click command for a plugin method."""
        import inspect
        
        # Get method signature
        sig = inspect.signature(method)
        
        # Create click command function
        @click.command()
        @click.pass_context
        def method_command(ctx, **kwargs):
            # Get the plugin instance from registry
            if plugin_name in self.app._registry:
                obj, exposer = self.app._registry[plugin_name]
                
                # Call the method on the plugin instance
                try:
                    method_result = getattr(obj, method_name)(**kwargs)
                    print(f"Result: {method_result}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Error: Plugin '{plugin_name}' not found in registry")
        
        # Add method docstring as help
        if method.__doc__:
            method_command.__doc__ = method.__doc__.strip()
        else:
            method_command.__doc__ = f"{method_name.replace('_', ' ').title()}"
        
        # Add options based on method parameters
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Determine option type and requirements
            is_required = param.default == inspect.Parameter.empty
            param_type = str  # Default to string
            
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = int
                elif param.annotation == float:
                    param_type = float
                elif param.annotation == bool:
                    param_type = bool
            
            # Create click option
            option_name = f'--{param_name.replace("_", "-")}'
            help_text = f"{param_name.replace('_', ' ').title()}"
            
            if is_required:
                help_text += " [required]"
            
            if param_type == bool:
                method_command = click.option(option_name, is_flag=True, help=help_text)(method_command)
            else:
                method_command = click.option(
                    option_name, 
                    type=param_type, 
                    required=is_required,
                    default=param.default if param.default != inspect.Parameter.empty else None,
                    help=help_text
                )(method_command)
        
        return method_command
    
    def _show_plugin_help(self, plugin_name: str, obj: Any, available_runners: Dict):
        """Show help for a plugin command."""
        import inspect
        
        print(f"Usage: app.py {plugin_name} [OPTIONS] COMMAND [ARGS]...")
        print("")
        print(f"  {plugin_name.title()} operations")
        print("")
        print("Options:")
        
        # Show runner options
        for runner_name in sorted(available_runners.keys()):
            if runner_name != 'click':
                print(f"  --{runner_name:<12} Use {runner_name} runner")
        
        print("  --help           Show this message and exit.")
        print("")
        print("Commands:")
        
        # Show available methods
        if inspect.isclass(obj):
            methods = inspect.getmembers(obj, predicate=inspect.isfunction)
        else:
            methods = inspect.getmembers(obj, predicate=inspect.ismethod)
        
        for method_name, method in methods:
            if not method_name.startswith('_'):
                help_text = method.__doc__.split('\n')[0] if method.__doc__ else f"{method_name.replace('_', ' ').title()}"
                print(f"  {method_name:<7} {help_text}")
    
    def _show_main_help(self, available_runners: Dict, available_commands: List[str]):
        """Show clean, short help consistent with click format."""
        print("Usage: yaapp [OPTIONS] COMMAND [ARGS]...")
        print("")
        print("  Yet Another App - CLI and Web API framework")
        print("")
        print("Options:")
        
        # Show runner options (excluding click as it's default)
        for runner_name in sorted(available_runners.keys()):
            if runner_name != 'click':
                print(f"  --{runner_name:<12} Use {runner_name} runner")
        
        print("  -v, --verbose        Verbose output")
        print("  -c, --config TEXT    Configuration file path")
        print("  -p, --plugin TEXT    Load specific built-in plugin (e.g., storage, docker)")
        print("  -s, --suite          Load complete plugin suite (all plugins as root commands)")
        print("  -l, --list-plugins   List all available built-in plugins")
        print("  --version            Show version and exit")
        print("  --help               Show this message and exit.")
        print("")
        print("Commands:")
        
        # Show available plugin commands
        for cmd_name in sorted(available_commands):
            # Get plugin description from registry
            description = self._get_plugin_description(cmd_name)
            print(f"  {cmd_name:<12} {description}")
    
    def _get_available_commands(self, available_runners: Dict) -> List[str]:
        """Get non-runner commands from registry."""
        commands = []
        for name, (obj, exposer) in self.app._registry.items():
            # Skip runners
            if name in available_runners:
                continue
            # Add other exposed objects as commands
            commands.append(name)
        return commands
    
    def _get_plugin_description(self, plugin_name: str) -> str:
        """Get description for a plugin from its docstring or methods."""
        if plugin_name not in self.app._registry:
            return f"{plugin_name.title()} operations"
        
        obj, exposer = self.app._registry[plugin_name]
        
        # Try to get description from class docstring
        if hasattr(obj, '__doc__') and obj.__doc__:
            # Get first line of docstring
            first_line = obj.__doc__.strip().split('\n')[0]
            if first_line and not first_line.startswith('"""'):
                return first_line
        
        # Fallback: generate description from available methods
        import inspect
        if inspect.isclass(obj):
            methods = [name for name, method in inspect.getmembers(obj, predicate=inspect.isfunction) 
                      if not name.startswith('_')]
        else:
            methods = [name for name, method in inspect.getmembers(obj, predicate=inspect.ismethod) 
                      if not name.startswith('_')]
        
        if methods:
            # Show first few methods
            method_list = ', '.join(sorted(methods)[:6])
            if len(methods) > 6:
                method_list += ', ...'
            return f"{plugin_name.title()} operations ({method_list})"
        
        return f"{plugin_name.title()} operations"
    
