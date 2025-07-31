"""
Main Yaapp class that combines core functionality with runners.
"""

from .core import YaappCore
from .runners import ClickRunner, PromptRunner, RichRunner, TyperRunner, FastAPIRunner


class Yaapp(YaappCore):
    """
    Main yaapp application class that bridges CLI and web interfaces.
    """

    def __init__(self, auto_discover: bool = True):
        """Initialize the yaapp application."""
        super().__init__()
        self._auto_discover = auto_discover
        self._plugins_discovered = False
        
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
            
            self._plugins_discovered = True
            
        except Exception as e:
            # Don't fail if config loading fails - just warn
            print(f"Warning: Failed to auto-discover plugins: {e}")
            self._plugins_discovered = True  # Mark as attempted to avoid retries

    def _run_server(self, host: str = "localhost", port: int = 8000, reload: bool = False) -> None:
        """Start FastAPI web server."""
        runner = FastAPIRunner(self)
        runner.run(host, port, reload)

    def _run_tui(self, backend: str = "prompt") -> None:
        """Start interactive TUI with specified backend."""
        print(f"Starting TUI with {backend} backend")
        print(f"Available functions: {list(self._registry.keys())}")

        if backend == "prompt":
            runner = PromptRunner(self)
        elif backend == "typer":
            runner = TyperRunner(self)
        elif backend == "rich":
            runner = RichRunner(self)
        elif backend == "click":
            runner = ClickRunner(self)
        else:
            print(f"Unknown backend: {backend}. Available: prompt, typer, rich, click")
            return

        runner.run()

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
        from .reflection import ClickReflection
        
        reflection = ClickReflection(self)
        cli = reflection.create_reflective_cli()
        if cli:
            cli()
        else:
            # Fallback if Click is not available
            print("YApp CLI not available - install click package")
            print("\nAvailable functions:")
            for name, obj in self._registry.items():
                print(f"  - {name}")
            print("\nTo use functions, install click: pip install click")

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