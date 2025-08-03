"""
Main Yaapp class that combines core functionality with plugin-based runners.
"""

import sys
from .core import YaappCore


class Yaapp(YaappCore):
    """
    Main yaapp application class that bridges CLI and web interfaces.
    """

    def __init__(self, auto_discover: bool = True):
        """Initialize the yaapp application."""
        super().__init__()
        self._auto_discover = auto_discover
        self._plugins_discovered = False
        self._runner_plugins = {}  # Cache for discovered runner plugins
        
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
        """Discover runner plugins through the plugin system."""
        try:
            # Import runner plugins to trigger @yaapp.expose() registration
            from .plugins.runners.click.plugin import ClickRunner
            from .plugins.runners.server.plugin import ServerRunner
            from .plugins.runners.rich.plugin import RichRunner
            from .plugins.runners.prompt.plugin import PromptRunner
            from .plugins.runners.typer.plugin import TyperRunner
            
            # Get runner plugins from registry (they should be auto-registered by @yaapp.expose)
            runner_names = ['click', 'server', 'rich', 'prompt', 'typer']
            for runner_name in runner_names:
                if runner_name in self._registry:
                    obj, exposer = self._registry[runner_name]
                    if hasattr(obj, 'help') and hasattr(obj, 'run'):
                        self._runner_plugins[runner_name] = obj
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
                self._runner_plugins[runner_name] = obj
                return obj
        
        return None

    def _run_server(self, host: str = "localhost", port: int = 8000, reload: bool = False) -> None:
        """Start FastAPI web server using plugin system."""
        server_runner = self._get_runner_plugin('server')
        if server_runner:
            server_runner.run(self, host=host, port=port, reload=reload)
        else:
            print("Error: Server runner plugin not found")
            print("Available runners:", list(self._runner_plugins.keys()))

    def _run_tui(self, backend: str = "prompt") -> None:
        """Start interactive TUI with specified backend using plugin system."""
        print(f"Starting TUI with {backend} backend")
        print(f"Available functions: {list(self._registry.keys())}")

        tui_runner = self._get_runner_plugin(backend)
        if tui_runner:
            tui_runner.run(self)
        else:
            print(f"Unknown backend: {backend}")
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
        """Run the main CLI interface."""
        try:
            import click
            # Use the unified CLI builder that shows both commands and runners
            from .unified_cli_builder import UnifiedCLIBuilder
            cli_builder = UnifiedCLIBuilder(self)
            cli = cli_builder.build_cli()
        except ImportError:
            cli = None
        if cli:
            cli()
        else:
            # Fallback if Click is not available
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
    
    def run(self):
        """Run the main CLI interface (alias for run_cli)."""
        # Lazy plugin discovery - always try to discover plugins when run() is called
        # This ensures we're in the correct working directory context
        if not self._plugins_discovered:
            # Temporarily enable auto_discover for lazy loading
            original_auto_discover = self._auto_discover
            self._auto_discover = True
            self._auto_discover_plugins()
            self._auto_discover = original_auto_discover
        
        self.run_cli()