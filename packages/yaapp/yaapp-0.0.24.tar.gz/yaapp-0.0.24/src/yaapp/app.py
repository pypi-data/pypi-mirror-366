"""
Main Yaapp class that combines core functionality with plugin-based runners.
"""

import sys
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
            # Load configuration which triggers plugin discovery
            config = self._load_config()
            
            # Register discovered plugins with this app instance
            config.register_discovered_plugins(self)
            
            # Discover runner plugins
            self._discover_runner_plugins()
            
            self._plugins_discovered = True
            
        except Exception as e:
            # Don't fail if config loading fails - just warn
            print(f"Warning: Failed to auto-discover plugins: {e}")
            self._plugins_discovered = True  # Mark as attempted to avoid retries
    
    def _discover_runner_plugins(self):
        """Discover runner plugins by scanning the runners directory."""
        try:
            # Use the discovery system to scan the runners directory
            from .discovery import PluginDiscovery
            discovery = PluginDiscovery()
            
            # Discover all runners by scanning the directory
            discovered_runners = discovery.discover_runners()
            
            # Get runner plugins from registry (they should be auto-registered by @yaapp.expose)
            for runner_name in discovered_runners.keys():
                if runner_name in self._registry:
                    obj, exposer = self._registry[runner_name]
                    if hasattr(obj, 'help') and hasattr(obj, 'run'):
                        # Don't cache here - let _get_runner_plugin handle instantiation
                        print(f"✅ Discovered runner plugin: {runner_name}")
                    else:
                        print(f"⚠️ Object '{runner_name}' in registry is not a valid runner")
                else:
                    print(f"⚠️ Runner '{runner_name}' not found in registry")
                    
        except ImportError as e:
            print(f"Warning: Failed to import runner plugins: {e}")
        except Exception as e:
            print(f"Warning: Failed to discover runner plugins: {e}")
    
    def _get_runner_plugin(self, runner_name: str):
        """Get a runner plugin by name."""
        if runner_name in self._runner_plugins:
            return self._runner_plugins[runner_name]
        
        # Try to get from registry
        if runner_name in self._registry:
            obj, exposer = self._registry[runner_name]
            if hasattr(obj, 'help') and hasattr(obj, 'run'):
                # If it's a class, instantiate it
                if isinstance(obj, type):
                    instance = obj()
                    self._runner_plugins[runner_name] = instance
                    return instance
                else:
                    # Already an instance
                    self._runner_plugins[runner_name] = obj
                    return obj
        
        return None

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
        """Run the main CLI interface using plugin system."""
        # Find any CLI runner (prefer click if available)
        cli_runner = self._get_runner_plugin('click')
        if not cli_runner:
            # Find any CLI-capable runner
            for runner_name, runner in self._runner_plugins.items():
                if hasattr(runner, 'help') and any(word in runner.help().lower() for word in ['cli', 'command', 'click']):
                    cli_runner = runner
                    break
        
        if cli_runner:
            cli_runner.run(self)
        else:
            # Fallback if no CLI runner available
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
        if not self._plugins_discovered:
            # Temporarily enable auto_discover for lazy loading
            original_auto_discover = self._auto_discover
            self._auto_discover = True
            self._auto_discover_plugins()
            self._auto_discover = original_auto_discover
        
        self.run_cli()


# Main entry point moved to main.py to avoid circular imports