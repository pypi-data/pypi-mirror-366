"""
Main Yaapp class that combines core functionality with plugin-based runners.
"""

import sys
import inspect
import importlib.util
from typing import Dict
from .core import YaappCore


class Yaapp(YaappCore):
    """
    Main yaapp application class that bridges CLI and web interfaces.
    """

    def __init__(self, auto_discover: bool = True, config_file: str = None):
        """Initialize the yaapp application.
        
        Args:
            auto_discover: Whether to automatically discover plugins from config
            config_file: Optional config file path that overrides standard search
        """
        super().__init__()
        self._auto_discover = auto_discover
        self._plugins_discovered = False
        self._runner_plugins = {}  # Cache for discovered runner plugins
        self._showcase_plugin = None  # Track if a showcase plugin is loaded
        
        # Set config file override if provided
        if config_file:
            self.set_config_file_override(config_file)
        
        # Auto-discover plugins from configuration
        if auto_discover:
            self._auto_discover_plugins()
    
    def _auto_discover_plugins(self):
        """Automatically discover and load plugins from configuration."""
        if self._plugins_discovered:
            return  # Already discovered

        try:
            # Load configuration which triggers plugin discovery and imports
            config = self._load_config()

            # Apply pending registrations from @expose decorators BEFORE registering plugins
            # This ensures plugins are in the registry when config tries to find them
            from .expose import apply_pending_registrations
            apply_pending_registrations(self)

            # Register discovered plugins with this app instance
            config.register_discovered_plugins(self)

            # Discover runner plugins
            self._discover_runner_plugins()

            self._plugins_discovered = True

        except Exception as e:
            # Don't fail if config loading fails - just warn
            print(f"Warning: Failed to auto-discover plugins: {e}")
            self._plugins_discovered = True  # Mark as attempted to avoid retries
    
    def _load_showcase_plugin(self, plugin_name: str):
        """Load a specific built-in plugin for showcase purposes."""
        if self._showcase_plugin:
            return  # Already loaded a showcase plugin
        
        try:
            # Import the plugin module to trigger @expose registration
            plugin_module_path = f"yaapp.plugins.{plugin_name}.plugin"
            import importlib
            importlib.import_module(plugin_module_path)
            
            # Apply pending registrations
            from .expose import apply_pending_registrations
            apply_pending_registrations(self)
            
            # Check if the plugin was registered
            if plugin_name in self._registry:
                obj, exposer = self._registry[plugin_name]
                
                # If it's a class, instantiate it with default config
                if isinstance(obj, type):
                    # Create default config for the plugin
                    default_config = self._get_default_plugin_config(plugin_name)
                    plugin_instance = obj(default_config)
                    
                    # Set the yaapp reference
                    plugin_instance.yaapp = self
                    
                    # Replace the class with the instance in the registry
                    self._registry[plugin_name] = (plugin_instance, exposer)
                    
                    print(f"✅ {plugin_name} ready (showcase mode)")
                else:
                    print(f"✅ {plugin_name} ready (showcase mode)")
                
                self._showcase_plugin = plugin_name
                self._plugins_discovered = True
            else:
                print(f"❌ Plugin '{plugin_name}' not found after import")
                self._list_available_plugins()
                
        except ImportError as e:
            print(f"❌ Plugin '{plugin_name}' not found: {e}")
            self._list_available_plugins()
        except Exception as e:
            print(f"❌ Failed to load plugin '{plugin_name}': {e}")
    
    def _get_default_plugin_config(self, plugin_name: str) -> dict:
        """Get default configuration for built-in plugins."""
        default_configs = {
            'storage': {
                'backend': 'memory'  # Fast, no persistence needed for showcase
            },
            'docker': {
                'host': 'unix://var/run/docker.sock'  # Default docker socket
            },
            'docker2': {
                'host': 'unix://var/run/docker.sock'  # Default docker socket
            },
            # Add more default configs as needed
        }
        
        return default_configs.get(plugin_name, {})
    
    def _list_available_plugins(self):
        """List available built-in plugins with descriptions."""
        import pkgutil
        import yaapp.plugins
        
        print("\n🔌 Available Built-in Plugins:")
        print("=" * 50)
        
        try:
            plugins_path = yaapp.plugins.__path__
            available = []
            
            for finder, name, ispkg in pkgutil.iter_modules(plugins_path):
                if ispkg and not name.startswith('_'):
                    # Check if it has a plugin.py file and get description
                    try:
                        plugin_module_path = f"yaapp.plugins.{name}.plugin"
                        spec = importlib.util.find_spec(plugin_module_path)
                        if spec:
                            description = self._get_plugin_description_from_module(plugin_module_path)
                            available.append((name, description))
                    except:
                        pass
            
            if available:
                # Sort by plugin name
                available.sort(key=lambda x: x[0])
                
                for plugin_name, description in available:
                    print(f"  📦 {plugin_name:<15} - {description}")
                
                print("\n💡 Usage Examples:")
                print("   yaapp --plugin storage --server     # Start storage API server")
                print("   yaapp --plugin storage --rich       # Interactive storage shell")
                print("   yaapp --plugin docker --help        # Show docker plugin commands")
                print("   yaapp -p storage storage set --key demo --value test")
                
                print("\n🚀 Quick Start:")
                print("   yaapp --plugin storage --server     # Instant storage API!")
                
            else:
                print("  ❌ No built-in plugins found")
                
        except Exception as e:
            print(f"  ❌ Error listing plugins: {e}")
    
    def _get_plugin_description_from_module(self, module_path: str) -> str:
        """Get a brief description of a plugin from its module."""
        plugin_name = module_path.split('.')[-2]  # Extract plugin name from path
        
        # Use curated descriptions for better UX
        descriptions = {
            'storage': 'Unified storage interface with multiple backends (memory, file, SQLite)',
            'docker': 'Docker client integration for container management',
            'docker2': 'Enhanced Docker plugin with dynamic introspection',
            'api': 'HTTP API client for external service integration',
            'app_proxy': 'Application proxy for distributed plugin execution',
            'auth': 'Authentication and authorization utilities',
            'issues': 'Issue tracking and management system',
            'mesh': 'Plugin mesh networking and discovery',
            'portalloc': 'Port allocation and management utilities',
            'registry': 'Service registry and discovery',
            'remote': 'Remote execution and process management',
            'remote_process': 'Remote process execution with PTY support',
            'router': 'Request routing and load balancing',
            'session': 'Session management and persistence',
        }
        
        if plugin_name in descriptions:
            return descriptions[plugin_name]
        
        # Try to get description from module docstring or class docstring
        try:
            module = importlib.import_module(module_path)
            
            # First try module docstring
            if hasattr(module, '__doc__') and module.__doc__:
                first_line = module.__doc__.strip().split('\n')[0]
                if first_line and len(first_line) > 10 and not first_line.startswith('"""'):
                    return first_line[:60] + ('...' if len(first_line) > 60 else '')
            
            # Look for main plugin class with meaningful docstring
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    hasattr(attr, '__doc__') and 
                    attr.__doc__ and
                    not attr_name.startswith('_') and
                    attr.__module__ == module.__name__):  # Only classes defined in this module
                    
                    # Get first line of docstring
                    first_line = attr.__doc__.strip().split('\n')[0]
                    if (first_line and 
                        len(first_line) > 10 and 
                        not first_line.startswith('"""') and
                        'Special type' not in first_line and  # Skip type annotations
                        'Helper class' not in first_line):   # Skip generic helpers
                        return first_line[:60] + ('...' if len(first_line) > 60 else '')
            
        except Exception:
            pass
            
        return 'Plugin functionality'
    
    def _discover_runner_plugins(self):
        """Discover runners by scanning the runners directory."""
        try:
            # Use the new runner discovery system
            from .runner_discovery import RunnerDiscovery
            self._runner_discovery = RunnerDiscovery()
            
            # Discover all runners
            discovered_runners = self._runner_discovery.discover_runners()
            
            # Store discovered runners for CLI builder
            self._available_runners = discovered_runners
                    
        except ImportError as e:
            print(f"Warning: Failed to import runner discovery: {e}")
            self._available_runners = {}
        except Exception as e:
            print(f"Warning: Failed to discover runners: {e}")
            self._available_runners = {}
    
    def _get_runner_plugin(self, runner_name: str):
        """Get a runner by name using the new discovery system."""
        if hasattr(self, '_runner_discovery'):
            return self._runner_discovery
        return None
    
    def run_runner(self, runner_name: str, **kwargs):
        """Execute a specific runner."""
        if hasattr(self, '_runner_discovery'):
            return self._runner_discovery.run_runner(runner_name, self, **kwargs)
        else:
            print(f"⚠️ Runner discovery not initialized")
    
    def get_available_runners(self) -> Dict[str, str]:
        """Get available runners with their help text."""
        if hasattr(self, '_runner_discovery'):
            return self._runner_discovery.get_available_runners()
        return {}

    def _run_server(self, host: str = "localhost", port: int = 8000, reload: bool = False) -> None:
        """Start web server using plugin system."""
        # Find any available server runner plugin
        server_runner = None
        for runner_name, runner in self._runner_plugins.items():
            if hasattr(runner, 'help') and 'server' in runner.help().lower():
                server_runner = runner
                break
        
        if server_runner:
            print(f"🚀 Using web server plugin")
            server_runner.run(self, host=host, port=port, reload=reload)
        else:
            print("❌ No web server plugin found. Make sure plugins are discovered.")
            print(f"Available runners: {list(self._runner_plugins.keys())}")
            return

    def _run_tui(self, backend: str = None) -> None:
        """Start interactive TUI with specified backend using plugin system."""
        # If no backend specified, find any TUI runner
        if backend is None:
            for runner_name, runner in self._runner_plugins.items():
                if hasattr(runner, 'help') and any(word in runner.help().lower() for word in ['tui', 'interactive', 'prompt', 'shell']):
                    backend = runner_name
                    break
        
        if backend:
            print(f"Starting TUI with {backend} backend")
            print(f"Available functions: {list(self._registry.keys())}")
            
            tui_runner = self._get_runner_plugin(backend)
            if tui_runner:
                tui_runner.run(self)
            else:
                print(f"Unknown backend: {backend}")
                print(f"Available runners: {list(self._runner_plugins.keys())}")
        else:
            print("❌ No TUI runner found. Make sure plugins are discovered.")
            print(f"Available runners: {list(self._runner_plugins.keys())}")
            return

    def _run_function(self, function_name: str, args: tuple) -> None:
        """Execute a specific function with arguments."""
        if function_name not in self._registry:
            print(f"Function '{function_name}' not found. Available: {list(self._registry.keys())}")
            return

        # Get the function object from registry
        registry_result = self.get_registry_item(function_name)
        if not registry_result.is_ok():
            print(f"Error getting function: {registry_result.as_error}")
            return
            
        func = registry_result.unwrap()
        try:
            # Convert args tuple to list for processing
            result = self._call_function_with_args(func, list(args))
            print(f"Result: {result}")
        except (KeyboardInterrupt, SystemExit):
            # Re-raise system exceptions to allow proper exit
            raise
        except Exception as e:
            print(f"Error executing {function_name}: {e}")

    def run_cli(self):
        """Run the main CLI interface using unified CLI builder."""
        try:
            from .unified_cli_builder import UnifiedCLIBuilder
            
            # Build and run the unified CLI
            builder = UnifiedCLIBuilder(self)
            cli = builder.build_cli()
            
            if cli:
                cli()
            else:
                # Fallback if CLI builder fails
                self._fallback_cli()
                
        except Exception as e:
            print(f"Error building CLI: {e}")
            self._fallback_cli()
    
    def _fallback_cli(self):
        """Fallback CLI when Click is not available."""
        print("Click not available. Install with: pip install click")
        print("YApp CLI not available - install click package")
        print("\nAvailable functions:")
        for name, obj in self._registry.items():
            print(f"  - {name}")
        print("\nTo use functions, install click: pip install click")
    

    def run_server(self, host: str = "localhost", port: int = 8000, reload: bool = False) -> None:
        """Start FastAPI web server (public method for CLI)."""
        # Ensure plugins are discovered
        if not self._plugins_discovered:
            self._auto_discover_plugins()
        
        self._run_server(host, port, reload)
    
    def run(self, config_file: str = None):
        """Run the main CLI interface (alias for run_cli).
        
        Args:
            config_file: Optional config file path that overrides standard search
        """
        # Set config file override if provided
        if config_file:
            self.set_config_file_override(config_file)
        
        # Lazy plugin discovery - always try to discover plugins when run() is called
        # This ensures we're in the correct working directory context
        # apply_pending_registrations() is called inside _auto_discover_plugins()
        if not self._plugins_discovered:
            # Temporarily enable auto_discover for lazy loading
            original_auto_discover = self._auto_discover
            self._auto_discover = True
            self._auto_discover_plugins()
            self._auto_discover = original_auto_discover
        
        self.run_cli()


# Main entry point moved to main.py to avoid circular imports