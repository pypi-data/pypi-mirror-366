"""
Universal yaapp CLI entry point with three modes:
1. Default/Proxy mode - presents default plugins via app proxy
2. Client mode - connects to remote yaapp servers
3. Server mode - starts server for current directory
"""

import sys
import os
from pathlib import Path
from typing import Optional

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


def get_default_app_proxy_config():
    """Get the built-in default app proxy configuration."""
    return {
        "app_proxy": {
            "default_plugins": {
                "issues": {
                    "target_url": "http://localhost:8001",
                    "timeout": 30
                },
                "storage": {
                    "target_url": "http://localhost:8002", 
                    "timeout": 30
                },
                "routing": {
                    "target_url": "http://localhost:8003",
                    "timeout": 30
                },
                "session": {
                    "target_url": "http://localhost:8004",
                    "timeout": 30
                },
                "subprocess": {
                    "target_url": "http://localhost:8005",
                    "timeout": 30
                }
            },
            "discovery": ["localhost_scan", "mdns"],
            "ports": [8000, 8001, 8002, 8003, 8004, 8005]
        }
    }


def load_universal_config(config_file=None):
    """Load configuration for universal CLI."""
    # Start with built-in defaults
    config = get_default_app_proxy_config()
    has_local_config = False
    
    # If specific config file provided, use it
    if config_file:
        config_files = [config_file]
    else:
        # Override with user config if present
        config_files = ["yaapp.yaml", "yaapp.yml", "yaapp.json"]
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                from yaapp.config import YaappConfig
                user_config = YaappConfig.load(config_file=str(config_path))
                has_local_config = True
                
                # If local config has plugins, use local mode instead of proxy
                if hasattr(user_config, 'discovered_sections') and user_config.discovered_sections:
                    # Local plugins found - switch to local mode
                    config['local_mode'] = True
                    config['local_plugins'] = user_config.discovered_sections
                
                # Merge user config with defaults
                if hasattr(user_config, 'custom') and user_config.custom:
                    config.update(user_config.custom)
                break
            except Exception as e:
                print(f"Warning: Failed to load config {config_file}: {e}")
    
    config['has_local_config'] = has_local_config
    return config


def create_universal_cli():
    """Create the universal yaapp CLI with three modes."""
    if not HAS_CLICK:
        print("Click not available. Install with: pip install click")
        return None

    @click.group(invoke_without_command=True)
    @click.option('--client', help='Connect to remote yaapp server as client')
    @click.option('--server', is_flag=True, help='Start server mode for current directory')
    @click.option('--port', default=8000, help='Server port (default: 8000) [used with --server]')
    @click.option('--host', default='localhost', help='Server host (default: localhost) [used with --server]')
    @click.option('--token', help='Authentication token [used with --client]')
    @click.option('--config', help='Configuration file [used with --server]')
    @click.pass_context
    def cli(ctx, client, server, port, host, token, config):
        """Universal yaapp CLI with default plugin ecosystem."""
        
        if client:
            # Client mode - connect to remote yaapp server
            handle_client_mode(ctx, client, token)
        elif server:
            # Server mode - start server for current directory
            handle_server_mode(ctx, host, port, config)
        elif ctx.invoked_subcommand is None:
            # No subcommand and no mode flags - show help
            click.echo(ctx.get_help())
            ctx.exit()
        # If subcommand is provided, continue to default/proxy mode
    
    return cli


def handle_client_mode(ctx, server_url, token):
    """Handle client mode - connect to remote yaapp server."""
    try:
        from .client import YaappClient
        
        print(f"Connecting to yaapp server: {server_url}")
        
        # Create client and connect
        client = YaappClient(server_url, token=token)
        
        # Get remaining arguments for the remote command
        remaining_args = ctx.parent.params.get('args', [])
        if not remaining_args:
            # Show remote server help
            result = client.get_help()
            print(result)
        else:
            # Execute command on remote server
            command = remaining_args[0]
            args = remaining_args[1:] if len(remaining_args) > 1 else []
            result = client.execute_command(command, args)
            print(result)
            
    except ImportError:
        print("Client functionality not available. Install yaapp with client dependencies.")
    except Exception as e:
        print(f"Client error: {e}")
    
    ctx.exit()


def handle_server_mode(ctx, host, port, config_file):
    """Handle server mode - start server for current directory."""
    try:
        from .app import Yaapp
        
        print(f"Starting yaapp server on {host}:{port}")
        
        # Create yaapp instance with current directory config
        app = Yaapp()
        
        # Load config if specified
        if config_file:
            print(f"Using config file: {config_file}")
        
        # Start server
        app.run_server(host=host, port=port)
        
    except Exception as e:
        print(f"Server error: {e}")
    
    ctx.exit()


def add_default_plugin_commands(cli, config_file=None):
    """Add default plugin commands to the CLI."""
    config = load_universal_config(config_file)
    
    # Check if we're in local mode (local plugins found)
    if config.get('local_mode', False):
        # Use local yaapp instance to get actual commands
        add_local_plugin_commands(cli, config)
    else:
        # Use default proxy mode
        app_proxy_config = config.get("app_proxy", {})
        default_plugins = app_proxy_config.get("default_plugins", {})
        
        for plugin_name, plugin_config in default_plugins.items():
            add_plugin_command_group(cli, plugin_name, plugin_config)


def add_local_plugin_commands(cli, config):
    """Add commands from local yaapp instance."""
    try:
        from yaapp.app import Yaapp
        
        # Create local yaapp instance with auto-discovery disabled
        # We'll manually register the plugins from the config
        app = Yaapp(auto_discover=False)
        
        # Manually register plugins from the discovered sections
        local_plugins = config.get('local_plugins', {})
        
        # Import the config system to get plugin instances
        from yaapp.config import YaappConfig
        
        # Load the config again to get the plugin instances
        # This is a bit redundant but ensures we get the same plugin instances
        # that were discovered during config loading
        
        # For now, let's use a simpler approach - just use the reflection system
        # from an existing working directory
        from yaapp.reflection import ClickReflection
        
        # Create a temporary yaapp instance in the current directory
        # This should pick up the local config and plugins
        temp_app = Yaapp(auto_discover=True)
        
        # Get registry items from the temp app
        registry_items = temp_app.get_registry_items()
        
        # Add simple commands for each registry item
        for name, obj in registry_items.items():
            if callable(obj):
                add_simple_command(cli, name, obj)
        
    except Exception as e:
        print(f"Warning: Failed to load local plugins: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to proxy mode
        app_proxy_config = config.get("app_proxy", {})
        default_plugins = app_proxy_config.get("default_plugins", {})
        
        for plugin_name, plugin_config in default_plugins.items():
            add_plugin_command_group(cli, plugin_name, plugin_config)


def add_simple_command(cli, name, func):
    """Add a simple command for a function."""
    import inspect
    
    # Get function signature
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        # Skip if we can't get signature
        return
    
    @cli.command(name=name)
    def command(**kwargs):
        f"""Execute {name}."""
        try:
            # Filter out None values
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            result = func(**filtered_kwargs)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Error: {e}")
    
    # Add options based on function parameters
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        
        option_type = str
        default_value = None
        
        if param.default != inspect.Parameter.empty:
            default_value = param.default
            if isinstance(default_value, bool):
                command = click.option(
                    f"--{param_name.replace('_', '-')}", 
                    is_flag=True, 
                    default=default_value,
                    help=f"Parameter {param_name}"
                )(command)
                continue
            elif isinstance(default_value, int):
                option_type = int
            elif isinstance(default_value, float):
                option_type = float
        
        command = click.option(
            f"--{param_name.replace('_', '-')}", 
            type=option_type, 
            default=default_value,
            help=f"Parameter {param_name}"
        )(command)


def add_plugin_command_group(cli, plugin_name, plugin_config):
    """Add a plugin command group to the CLI."""
    
    @cli.group(name=plugin_name)
    def plugin_group():
        f"""Commands for {plugin_name} plugin."""
        pass
    
    # Add common plugin subcommands based on plugin type
    add_plugin_subcommands(plugin_group, plugin_name, plugin_config)


def add_plugin_subcommands(plugin_group, plugin_name, plugin_config):
    """Add subcommands for a plugin based on its type."""
    
    if plugin_name == "issues":
        add_issues_commands(plugin_group, plugin_config)
    elif plugin_name == "storage":
        add_storage_commands(plugin_group, plugin_config)
    elif plugin_name == "routing":
        add_routing_commands(plugin_group, plugin_config)
    elif plugin_name == "session":
        add_session_commands(plugin_group, plugin_config)
    elif plugin_name == "subprocess":
        add_subprocess_commands(plugin_group, plugin_config)


def add_issues_commands(group, config):
    """Add issues plugin commands."""
    
    @group.command()
    @click.option('--title', required=True, help='Issue title')
    @click.option('--description', default='', help='Issue description')
    @click.option('--reporter', required=True, help='Issue reporter')
    @click.option('--priority', default='medium', help='Issue priority')
    @click.option('--assignee', help='Issue assignee')
    def create(title, description, reporter, priority, assignee):
        """Create a new issue."""
        execute_plugin_command('issues', 'create', config, {
            'title': title,
            'description': description,
            'reporter': reporter,
            'priority': priority,
            'assignee': assignee
        })
    
    @group.command()
    @click.option('--id', 'issue_id', required=True, help='Issue ID')
    def get(issue_id):
        """Get issue by ID."""
        execute_plugin_command('issues', 'get', config, {'id': issue_id})
    
    @group.command()
    @click.option('--id', 'issue_id', required=True, help='Issue ID')
    @click.option('--title', help='New title')
    @click.option('--description', help='New description')
    @click.option('--priority', help='New priority')
    @click.option('--assignee', help='New assignee')
    def update(issue_id, title, description, priority, assignee):
        """Update issue."""
        params = {'id': issue_id}
        if title: params['title'] = title
        if description: params['description'] = description
        if priority: params['priority'] = priority
        if assignee: params['assignee'] = assignee
        execute_plugin_command('issues', 'update', config, params)
    
    @group.command()
    @click.option('--id', 'issue_id', required=True, help='Issue ID')
    def delete(issue_id):
        """Delete issue."""
        execute_plugin_command('issues', 'delete', config, {'id': issue_id})
    
    @group.command()
    @click.option('--status', help='Filter by status')
    @click.option('--assignee', help='Filter by assignee')
    def list(status, assignee):
        """List issues."""
        params = {}
        if status: params['status'] = status
        if assignee: params['assignee'] = assignee
        execute_plugin_command('issues', 'list', config, params)


def add_storage_commands(group, config):
    """Add storage plugin commands."""
    
    @group.command()
    @click.option('--key', required=True, help='Storage key')
    def get(key):
        """Get value by key."""
        execute_plugin_command('storage', 'get', config, {'key': key})
    
    @group.command()
    @click.option('--key', required=True, help='Storage key')
    @click.option('--value', required=True, help='Storage value')
    def set(key, value):
        """Set value for key."""
        execute_plugin_command('storage', 'set', config, {'key': key, 'value': value})
    
    @group.command()
    @click.option('--key', required=True, help='Storage key')
    def delete(key):
        """Delete key."""
        execute_plugin_command('storage', 'delete', config, {'key': key})
    
    @group.command()
    @click.option('--key', required=True, help='Storage key')
    def exists(key):
        """Check if key exists."""
        execute_plugin_command('storage', 'exists', config, {'key': key})
    
    @group.command()
    def keys():
        """List all keys."""
        execute_plugin_command('storage', 'keys', config, {})
    
    @group.command()
    def clear():
        """Clear all data."""
        execute_plugin_command('storage', 'clear', config, {})


def add_routing_commands(group, config):
    """Add routing plugin commands."""
    
    @group.command()
    @click.option('--path', required=True, help='Route path')
    @click.option('--target', required=True, help='Target URL')
    def add_route(path, target):
        """Add a new route."""
        execute_plugin_command('routing', 'add_route', config, {'path': path, 'target': target})
    
    @group.command()
    @click.option('--path', required=True, help='Route path')
    def remove_route(path):
        """Remove a route."""
        execute_plugin_command('routing', 'remove_route', config, {'path': path})
    
    @group.command()
    def list_routes():
        """List all routes."""
        execute_plugin_command('routing', 'list_routes', config, {})


def add_session_commands(group, config):
    """Add session plugin commands."""
    
    @group.command()
    @click.option('--user', required=True, help='User ID')
    def create(user):
        """Create a new session."""
        execute_plugin_command('session', 'create', config, {'user': user})
    
    @group.command()
    @click.option('--session-id', required=True, help='Session ID')
    def get(session_id):
        """Get session info."""
        execute_plugin_command('session', 'get', config, {'session_id': session_id})
    
    @group.command()
    @click.option('--session-id', required=True, help='Session ID')
    def delete(session_id):
        """Delete session."""
        execute_plugin_command('session', 'delete', config, {'session_id': session_id})


def add_subprocess_commands(group, config):
    """Add subprocess plugin commands."""
    
    @group.command()
    @click.option('--command', required=True, help='Command to run')
    @click.option('--args', help='Command arguments')
    def run(command, args):
        """Run a subprocess command."""
        params = {'command': command}
        if args: params['args'] = args
        execute_plugin_command('subprocess', 'run', config, params)
    
    @group.command()
    @click.option('--process-id', required=True, help='Process ID')
    def status(process_id):
        """Get process status."""
        execute_plugin_command('subprocess', 'status', config, {'process_id': process_id})
    
    @group.command()
    @click.option('--process-id', required=True, help='Process ID')
    def kill(process_id):
        """Kill process."""
        execute_plugin_command('subprocess', 'kill', config, {'process_id': process_id})


def execute_plugin_command(plugin_name, command, config, params):
    """Execute a plugin command via app proxy."""
    try:
        target_url = config.get('target_url')
        if not target_url:
            print(f"Error: No target URL configured for {plugin_name} plugin")
            return
        
        # Try to use app proxy to execute command
        try:
            from yaapp.plugins.app_proxy import AppProxy
        except ImportError:
            print(f"App proxy not available. Cannot execute {plugin_name}.{command}")
            return
        
        proxy_config = {
            'target_url': target_url,
            'timeout': config.get('timeout', 30)
        }
        
        proxy = AppProxy(proxy_config)
        result = proxy.execute_call(f"{plugin_name}.{command}", **params)
        
        if result:
            print(result)
        else:
            print(f"Command executed successfully")
            
    except ImportError:
        print(f"App proxy not available. Cannot execute {plugin_name}.{command}")
    except Exception as e:
        print(f"Error executing {plugin_name}.{command}: {e}")


def main():
    """Main CLI entry point for installed yaapp package."""
    if not HAS_CLICK:
        print("Click not available. Install with: pip install click")
        print("Install yaapp with CLI support: pip install yaapp[cli]")
        return
    
    try:
        # Parse config file from command line args if provided
        config_file = None
        if '--config' in sys.argv:
            config_index = sys.argv.index('--config')
            if config_index + 1 < len(sys.argv):
                config_file = sys.argv[config_index + 1]
        
        # Create universal CLI
        cli = create_universal_cli()
        if not cli:
            return
        
        # Add default plugin commands with config file
        add_default_plugin_commands(cli, config_file)
        
        # Run CLI
        cli()
        
    except Exception as e:
        print(f"CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()