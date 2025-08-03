"""
Main Yaapp class that combines core functionality with plugin-based runners.
"""

import sys
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