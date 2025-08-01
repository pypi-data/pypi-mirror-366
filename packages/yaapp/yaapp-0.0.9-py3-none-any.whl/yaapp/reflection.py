"""
Click reflection functionality for yaapp - refactored into focused classes.
"""

import inspect
import json
from typing import Any, Dict, Optional
from io import StringIO
import sys

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class CLIBuilder:
    """Handles creation of Click CLI groups with root-level options."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
    
    def build_cli(self) -> Optional['click.Group']:
        """Build the main CLI group with hierarchical help system."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None
        
        # Use the new hierarchical CLI builder
        from .cli_builder import HierarchicalCLIBuilder
        hierarchical_builder = HierarchicalCLIBuilder(self.core)
        cli = hierarchical_builder.build_cli()
        
        return cli
    
    def _start_server(self, host: str, port: int, reload: bool):
        """Start the web server using plugin system."""
        # Use the app's plugin system to get server runner
        server_runner = self.core._get_runner_plugin('server')
        if server_runner:
            server_runner.run(self.core, host=host, port=port, reload=reload)
        else:
            print("Error: Server runner plugin not found")
    
    def _start_tui(self, backend: str):
        """Start interactive TUI using plugin system."""
        print(f"Starting TUI with {backend} backend")

        tui_runner = self.core._get_runner_plugin(backend)
        if tui_runner:
            tui_runner.run(self.core)
        else:
            print(f"Unknown backend: {backend}")
            available_runners = [name for name in self.core._runner_plugins.keys() if name != 'server']
            print(f"Available TUI runners: {available_runners}")
            return
    
    def _list_functions(self):
        """List all exposed functions."""
        print("Available functions:")
        registry_items = self.core.get_registry_items()
        for name, func in sorted(registry_items.items()):
            func_type = "function"
            if inspect.isclass(func):
                func_type = "class"
            doc = getattr(func, '__doc__', '') or 'No description'
            if doc:
                doc = doc.split('\n')[0][:50] + ('...' if len(doc.split('\n')[0]) > 50 else '')
            print(f"  {name:<20} | {func_type:<8} | {doc}")


class CommandReflector:
    """Handles reflection of functions and classes into Click commands."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
    
    def add_reflected_commands(self, cli_group) -> None:
        """Add commands based on exposed objects with reflection."""
        registry_items = self.core.get_registry_items()
        
        # Get list of runner names to exclude from commands
        runner_names = set()
        if hasattr(self.core, '_runner_plugins'):
            runner_names = set(self.core._runner_plugins.keys())
        
        for name, obj in registry_items.items():
            # Skip runners - they should be options, not commands
            if name in runner_names:
                continue
                
            # Skip objects that have runner-like interface (help + run methods)
            if hasattr(obj, 'help') and hasattr(obj, 'run') and callable(getattr(obj, 'help')) and callable(getattr(obj, 'run')):
                continue
                
            if '.' in name:
                # Handle nested objects (e.g., "math.add")
                self._add_nested_command(cli_group, name, obj)
            elif inspect.isclass(obj):
                # Handle classes - create command group with methods as subcommands
                self._add_class_command(cli_group, name, obj)
            elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__') and not inspect.isfunction(obj) and not inspect.ismethod(obj):
                # Handle class instances - create command group with methods as subcommands
                self._add_instance_command(cli_group, name, obj)
            elif callable(obj):
                # Handle functions - create direct command
                self._add_function_command(cli_group, name, obj)
    
    def _add_nested_command(self, cli_group, full_name: str, obj) -> None:
        """Add nested commands (e.g., math.add -> math group with add subcommand)."""
        parts = full_name.split('.')
        group_name = parts[0]
        command_name = '.'.join(parts[1:])
        
        # Get or create the group using a safer approach
        group = self._get_or_create_group(cli_group, group_name)
        
        if callable(obj):
            self._add_function_command(group, command_name, obj)
    
    def _get_or_create_group(self, cli_group, group_name: str):
        """Safely get or create a command group."""
        group_attr = f'_yaapp_group_{group_name}'
        
        if not hasattr(cli_group, group_attr):
            @cli_group.group(name=group_name)
            def nested_group():
                f"""Commands in {group_name} namespace."""
                pass
            
            setattr(cli_group, group_attr, nested_group)
        
        return getattr(cli_group, group_attr)
    
    def _add_class_command(self, cli_group, name: str, cls) -> None:
        """Add a class as a command group with methods as subcommands."""
        @cli_group.group(name=name)
        def class_group():
            f"""Commands for {cls.__name__} class."""
            pass
        
        # Store class name for method resolution
        class_group._yaapp_class_name = name
        
        # Add methods as subcommands - inspect class directly without instantiation
        for method_name in dir(cls):
            if not method_name.startswith('_'):
                method = getattr(cls, method_name)
                if callable(method) and not isinstance(method, type):
                    # Create a bound method using a lazily instantiated class instance
                    # We'll handle the actual instantiation at execution time
                    self._add_class_method_command(class_group, method_name, name)
    
    def _add_instance_command(self, cli_group, name: str, instance) -> None:
        """Add a class instance as a command group with methods as subcommands."""
        # Check if this is a CustomExposer plugin
        if self._is_custom_exposer_plugin(name, instance):
            self._add_custom_exposer_commands(cli_group, name, instance)
            return
        
        @cli_group.group(name=name)
        def instance_group():
            f"""Commands for {instance.__class__.__name__} instance."""
            pass
        
        # Store instance name for method resolution
        instance_group._yaapp_instance_name = name
        
        # Add methods as subcommands - inspect instance methods
        for method_name in dir(instance):
            if not method_name.startswith('_'):
                method = getattr(instance, method_name)
                if callable(method) and not isinstance(method, type):
                    self._add_instance_method_command(instance_group, method_name, name)
    
    def _add_function_command(self, cli_group, name: str, func) -> None:
        """Add a function as a click command with proper options."""
        # Get function signature
        sig = inspect.signature(func)
        
        def create_command():
            @cli_group.command(name=name)
            def command(**kwargs):
                f"""Execute {name}."""
                try:
                    # Filter out None values (unset options)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    result = func(**filtered_kwargs)
                    if result is not None:
                        if isinstance(result, dict):
                            click.echo(json.dumps(result, indent=2))
                        else:
                            click.echo(str(result))
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
            
            # Add click options based on function parameters
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                command = self._add_parameter_option(command, param_name, param)
            
            return command
        
        create_command()
    
    def _add_class_method_command(self, cli_group, method_name: str, class_name: str) -> None:
        """Add a class method as a click command using the exposer system."""
        # Get the class from registry to inspect method signature
        registry_items = self.core.get_registry_items()
        cls = registry_items[class_name]
        method = getattr(cls, method_name)
        sig = inspect.signature(method)
        
        def create_command():
            @cli_group.command(name=method_name)
            def command(**kwargs):
                f"""Execute {class_name}.{method_name}."""
                try:
                    # Filter out None values (unset options)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    
                    # Use exposer system to execute class method
                    result = self.core._execute_from_registry(class_name, **filtered_kwargs)
                    
                    if hasattr(result, 'is_ok') and result.is_ok():
                        # Get the instance and call the method
                        instance = result.unwrap()
                        method_result = getattr(instance, method_name)(**filtered_kwargs)
                        if method_result is not None:
                            if isinstance(method_result, dict):
                                click.echo(json.dumps(method_result, indent=2))
                            else:
                                click.echo(str(method_result))
                    else:
                        click.echo(f"Error: {result.as_error if hasattr(result, 'as_error') else result}", err=True)
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
            
            # Add click options based on method parameters
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                command = self._add_parameter_option(command, param_name, param)
            
            return command
        
        create_command()
    
    def _add_instance_method_command(self, cli_group, method_name: str, instance_name: str) -> None:
        """Add an instance method as a click command."""
        # Get the instance from registry to inspect method signature
        registry_items = self.core.get_registry_items()
        instance = registry_items[instance_name]
        method = getattr(instance, method_name)
        sig = inspect.signature(method)
        
        def create_command():
            @cli_group.command(name=method_name)
            def command(**kwargs):
                f"""Execute {instance_name}.{method_name}."""
                try:
                    # Filter out None values (unset options)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    
                    # Call the method directly on the instance
                    method_result = method(**filtered_kwargs)
                    
                    if method_result is not None:
                        if isinstance(method_result, dict):
                            click.echo(json.dumps(method_result, indent=2))
                        else:
                            click.echo(str(method_result))
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
            
            # Add click options based on method parameters
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                command = self._add_parameter_option(command, param_name, param)
            
            return command
        
        create_command()
    
    def _is_custom_exposer_plugin(self, name: str, instance) -> bool:
        """Check if this instance is a CustomExposer plugin."""
        # Check if the instance has the CustomExposer interface
        return (hasattr(instance, 'expose_to_registry') and 
                hasattr(instance, 'execute_call') and
                hasattr(instance, '_discovered_methods'))
    
    def _add_custom_exposer_commands(self, cli_group, name: str, instance) -> None:
        """Add commands for CustomExposer plugins based on discovered methods."""
        @cli_group.group(name=name)
        def custom_group():
            f"""Commands for {instance.__class__.__name__} plugin."""
            pass
        
        # Store instance name for method resolution
        custom_group._yaapp_instance_name = name
        custom_group._yaapp_is_custom_exposer = True
        
        # Get discovered methods from the CustomExposer plugin
        if hasattr(instance, '_discovered_methods'):
            discovered_methods = instance._discovered_methods
            
            # Group methods by category for hierarchical organization
            method_groups = {}
            root_methods = []
            
            for method_path in discovered_methods.keys():
                if '/' in method_path:
                    # Hierarchical method like "containers/list"
                    category, method_name = method_path.split('/', 1)
                    if category not in method_groups:
                        method_groups[category] = []
                    method_groups[category].append((method_name, method_path))
                else:
                    # Root level method like "ping"
                    root_methods.append(method_path)
            
            # Add root level methods directly
            for method_name in root_methods:
                self._add_custom_exposer_method_command(custom_group, method_name, name)
            
            # Add hierarchical method groups
            for category, methods in method_groups.items():
                # Create a subgroup for each category
                category_group = self._get_or_create_group(custom_group, category)
                category_group._yaapp_instance_name = name
                category_group._yaapp_is_custom_exposer = True
                
                for method_name, full_path in methods:
                    self._add_custom_exposer_method_command(category_group, method_name, name, full_path)
    
    def _add_custom_exposer_method_command(self, cli_group, method_name: str, instance_name: str, full_path: str = None) -> None:
        """Add a CustomExposer method as a click command."""
        # Use the full path if provided, otherwise use method_name
        function_name = full_path or method_name
        
        def create_command():
            @cli_group.command(name=method_name)
            def command(**kwargs):
                f"""Execute {instance_name}.{function_name}."""
                try:
                    # Filter out None values (unset options)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    
                    # Use the CustomExposer execute_call interface
                    result = self.core._execute_from_registry(instance_name, function_name=function_name, **filtered_kwargs)
                    
                    if hasattr(result, 'is_ok') and result.is_ok():
                        method_result = result.unwrap()
                        if method_result is not None:
                            if isinstance(method_result, dict):
                                click.echo(json.dumps(method_result, indent=2))
                            else:
                                click.echo(str(method_result))
                    else:
                        click.echo(f"Error: {result.as_error if hasattr(result, 'as_error') else result}", err=True)
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
            
            # For CustomExposer methods, we don't have direct access to signatures
            # So we'll add some common options that might be useful
            # TODO: Could be enhanced to introspect Docker API signatures
            
            return command
        
        create_command()
    
    def _add_parameter_option(self, command, param_name: str, param):
        """Add a click option for a function parameter."""
        # Determine option type and default
        option_type = str  # Default to string
        default_value = None
        help_text = f"Parameter {param_name}"
        
        if param.default != inspect.Parameter.empty:
            default_value = param.default
            if isinstance(default_value, bool):
                # Boolean parameters become flags
                return click.option(
                    f"--{param_name.replace('_', '-')}", 
                    is_flag=True, 
                    default=default_value,
                    help=help_text
                )(command)
            elif isinstance(default_value, int):
                option_type = int
            elif isinstance(default_value, float):
                option_type = float
        
        # Add the option
        return click.option(
            f"--{param_name.replace('_', '-')}", 
            type=option_type, 
            default=default_value,
            help=help_text
        )(command)


class ExecutionHandler:
    """Handles safe command execution without dangerous stream hijacking."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
        self.cli_builder = CLIBuilder(core)
        self.command_reflector = CommandReflector(core)
    
    def execute_command_safely(self, func_name: str, args: list, console=None) -> None:
        """Execute a command through click interface with safe output capture."""
        # Create the click CLI
        cli = self.cli_builder.build_cli()
        if not cli:
            print("Error: Could not create click CLI")
            return
        
        # Add reflected commands
        self.command_reflector.add_reflected_commands(cli)
        
        # Build command arguments based on context
        click_args = self._build_command_args(func_name, args)
        
        # Execute with safe output capture
        self._execute_with_safe_capture(cli, click_args, console)
    
    def _build_command_args(self, func_name: str, args: list) -> list:
        """Build command arguments based on current context."""
        click_args = []
        
        # Handle contextual commands using context tree
        context_path = self.core._context_tree.get_current_context_path()
        if context_path and len(context_path) == 1:
            class_name = context_path[0]
            # Check if this is a class command
            registry_items = self.core.get_registry_items()
            if class_name in registry_items and inspect.isclass(registry_items[class_name]):
                click_args = [class_name, func_name] + args
            else:
                # Handle nested namespaces
                click_args = [func_name] + args
        else:
            # Root context or deeply nested - direct command
            click_args = [func_name] + args
        
        return click_args
    
    def _execute_with_safe_capture(self, cli, click_args: list, console=None) -> None:
        """Execute command with safe output capture without stream hijacking."""
        handler = ClickOutputHandler()
        
        try:
            stdout_output, stderr_output = handler.capture_output(cli, click_args)
        except Exception as e:
            stdout_output = ""
            stderr_output = f"Execution error: {e}"
        
        # Display captured output
        self._display_output(stdout_output, stderr_output, console)
    
    def _display_output(self, stdout_output: str, stderr_output: str, console=None) -> None:
        """Display captured output to the appropriate console."""
        if stdout_output.strip():
            if console:
                console.print(stdout_output.strip())
            else:
                print(stdout_output.strip())
                
        if stderr_output.strip():
            if console:
                console.print(f"[bold red]Error:[/bold red] {stderr_output.strip()}")
            else:
                print(f"Error: {stderr_output.strip()}")


class ClickOutputHandler:
    """Handler for Click command output without dangerous stream hijacking."""
    
    def __init__(self):
        self.output_buffer = []
        self.error_buffer = []
    
    def capture_output(self, cli, click_args: list) -> tuple[str, str]:
        """Execute Click command and capture output safely."""
        try:
            # Use Click's built-in testing utilities instead of stream hijacking
            from click.testing import CliRunner
            runner = CliRunner()
            
            # Run the command in isolated environment
            result = runner.invoke(cli, click_args, catch_exceptions=False)
            
            return result.output, result.stderr_bytes.decode() if result.stderr_bytes else ""
            
        except ImportError:
            # Fallback: execute without capture if click.testing not available  
            try:
                ctx = click.Context(cli)
                with ctx:
                    cli.main(click_args, standalone_mode=False)
                return "Command executed successfully", ""
            except SystemExit:
                # Click uses SystemExit for --help and errors - this is expected
                return "Command completed", ""
            except Exception as e:
                return "", f"Execution error: {e}"
    
    def write_error(self, message: str) -> None:
        """Write an error message to error buffer."""
        self.error_buffer.append(message)


class ClickReflection:
    """Maintains backward compatibility with existing runners while using refactored components."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
        self.execution_handler = ExecutionHandler(core)
    
    def create_reflective_cli(self):
        """Create enhanced CLI with reflection for objects and subcommands."""
        cli_builder = CLIBuilder(self.core)
        cli = cli_builder.build_cli()
        
        if cli:
            # Add reflected commands
            command_reflector = CommandReflector(self.core)
            command_reflector.add_reflected_commands(cli)
        
        return cli
    
    def execute_command_through_click(self, func_name: str, args: list, console=None) -> None:
        """Execute a command through the click interface with safe handling."""
        self.execution_handler.execute_command_safely(func_name, args, console)
    
    def _parse_args_to_kwargs(self, args: list) -> Dict[str, Any]:
        """Parse command line arguments to kwargs format."""
        from .reflection_utils import ArgumentParser
        parser = ArgumentParser()
        return parser.parse_args_to_kwargs(args)

class SafeStreamCapture:
    """Safe stream capture for testing."""
    def __init__(self):
        self.captured = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def getvalue(self):
        return "\n".join(self.captured)