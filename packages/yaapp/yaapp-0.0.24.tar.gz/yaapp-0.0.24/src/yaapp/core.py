"""
Core functionality for yaapp - exposure and reflection.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .config import ConfigManager, YaappConfig
from .context_tree import ContextTree
from .execution_strategy import ExecutionHint, ExecutionStrategy
from .exposers import (
    BaseExposer,
    ClassExposer,
    CustomExposer,
    FunctionExposer,
    ObjectExposer,
)
from .result import Err, Ok, Result


class YaappCore:
    """Core functionality for yaapp - function exposure and reflection."""

    def __init__(self):
        """Initialize the core yaapp functionality."""
        self._config: Optional[YaappConfig] = None
        self._config_file_override: Optional[str] = None

        # Context tree for navigation (replaces fragile string manipulation)
        self._context_tree = ContextTree()

        # Initialize exposer system with registry for reflection
        self._function_exposer = FunctionExposer()
        self._class_exposer = ClassExposer()
        self._object_exposer = ObjectExposer()
        self._custom_exposer = CustomExposer()

        # Registry stores (object, exposer) pairs for proper execution
        self._registry: Dict[str, Tuple[Any, BaseExposer]] = {}
    
    def set_config_file_override(self, config_file: Optional[str]) -> None:
        """Set a config file that overrides the standard search paths.
        
        Args:
            config_file: Path to config file that should take precedence over
                        current directory and other standard locations
        """
        self._config_file_override = config_file
        # Clear cached config so it gets reloaded with the override
        self._config = None

    def expose(
        self,
        obj: Union[Callable, Dict[str, Any], object] = None,
        name: Optional[str] = None,
        custom: bool = False,
        execution: Optional[str] = None,
    ) -> Union[Result[Union[Callable, object]], Callable]:
        """
        Expose a function, class, or dictionary of functions to the CLI/web interface.

        Args:
            obj: Function, class, or dictionary to expose
            name: Optional name to use (defaults to function/class name)
            custom: Whether to use custom exposure workflow
            execution: Execution strategy for sync functions in async context
                      Options: "direct", "thread", "process", "auto"
                      Default: None (preserves existing hints, uses "thread" if none)

        Returns:
            The original object (for use as decorator)
        """
        # Handle decorator usage: @app.expose or @app.expose(execution="thread") or @app.expose('name')
        if obj is None or (isinstance(obj, str) and name is None):
            # This is decorator usage with parameters - return decorator function
            # Handle case where name is passed as first argument: @app.expose('name')
            decorator_name = obj if isinstance(obj, str) else name
            
            def decorator(func):
                result = self._expose_object_internal(func, decorator_name, custom, execution, execution is not None)
                if result.is_ok():
                    return func  # Return the original function for decorator usage
                else:
                    # For decorator usage, we need to raise since decorators can't return Result
                    raise ValueError(result.as_error)
            return decorator
        
        # Check if this is direct decorator usage: @app.expose (without parentheses)
        if callable(obj) and name is None and not custom and execution is None:
            # This is @app.expose usage - expose the function and return it
            result = self._expose_object_internal(obj, None, False, "thread", False)
            if result.is_ok():
                return obj  # Return the original function for decorator usage
            else:
                # For decorator usage, we need to raise since decorators can't return Result
                raise ValueError(result.as_error)

        # Handle regular expose calls
        result = self._expose_object_internal(obj, name, custom, execution, execution is not None)
        if result.is_ok():
            return obj  # Return the original object
        else:
            return result  # Return the error Result
    
    def _expose_object_internal(self, obj: Any, name: Optional[str], custom: bool, execution: str, execution_was_provided: bool) -> Result[Any]:
        """Internal method to expose an object and return Result."""
        if isinstance(obj, dict):
            # Handle nested dictionaries
            result = self._register_dict(obj)
            if not result.is_ok():
                return result
        else:
            # Use exposer system to handle the object
            if name is None:
                register_name = getattr(obj, "__name__", str(obj))
            else:
                register_name = name

            # Validate name
            if not register_name or not register_name.strip():
                return Result.error("Cannot expose object with empty or whitespace-only name")

            # Process and store the object with proper async compatibility and execution hint
            # Use "thread" as default if no execution strategy provided
            effective_execution = execution if execution is not None else "thread"

            processed_obj = self._process_object_for_registry(
                obj, custom, effective_execution, execution_was_provided
            )
            result = self._expose_with_system(processed_obj, register_name, custom)
            if not result.is_ok():
                return result

        return Ok(obj)

    def _process_object_for_registry(
        self,
        obj: Any,
        custom: bool = False,
        execution: str = "thread",
        execution_was_provided: bool = False,
    ) -> Any:
        """Process object for registry storage, applying execution hints and async compatibility if needed."""
        # Add execution hint to callable objects (functions and methods)
        if callable(obj) and not inspect.isclass(obj) and not custom:
            # Set execution hint - preserve existing ones unless explicitly overridden
            should_set_hint = (
                not hasattr(obj, "__execution_hint__")  # No existing hint
                or execution_was_provided  # Explicitly provided by user
            )

            if should_set_hint:
                try:
                    # Create and attach execution hint
                    strategy = ExecutionStrategy(execution)
                    hint = ExecutionHint(strategy=strategy)
                    obj.__execution_hint__ = hint
                except (ValueError, AttributeError):
                    # Invalid execution strategy or can't set attribute (e.g., bound methods)
                    # For bound methods, skip setting execution hint
                    if hasattr(obj, "__self__"):
                        pass  # Bound method, can't set attributes
                    else:
                        # Try with default strategy
                        try:
                            hint = ExecutionHint(strategy=ExecutionStrategy.THREAD)
                            obj.__execution_hint__ = hint
                        except AttributeError:
                            pass  # Can't set attribute, skip

            # Apply async compatibility if it's not a bound method
            if not hasattr(obj, "__self__"):
                try:
                    from .async_compat import async_compatible

                    return async_compatible(obj)
                except (ImportError, TypeError, AttributeError):
                    # If async_compatible fails, store original object with hint
                    return obj

        return obj

    def _expose_with_system(self, obj: Any, name: str, custom: bool = False) -> Result[None]:
        """Expose an object using the exposer system."""
        import inspect

        # Determine which exposer to use based on type
        if custom:
            exposer = self._custom_exposer
        elif inspect.isclass(obj):
            exposer = self._class_exposer
        elif callable(obj):
            exposer = self._function_exposer
        else:
            exposer = self._object_exposer

        # Expose using the selected exposer and add to registry
        result = exposer.expose(obj, name, custom)
        if not result.is_ok():
            # For custom objects, return error for strict validation
            if custom:
                return Result.error(f"Failed to expose {name}: {result.as_error}")
            else:
                # For internal use, log error and continue gracefully
                print(f"Warning: Failed to expose {name}: {result.as_error}")
                return Ok(None)

        # For CustomExposer with classes, store the instance instead of the class
        registry_obj = obj
        if custom and isinstance(exposer, CustomExposer) and inspect.isclass(obj):
            # Get the instance that CustomExposer created
            if obj in exposer._instance_cache:
                registry_obj = exposer._instance_cache[obj]

        # Store (object, exposer) pair in registry for proper execution
        self._registry[name] = (registry_obj, exposer)

        # Add to context tree for efficient navigation
        self._context_tree.add_item(name, obj)
        return Ok(None)

    def _register_dict(
        self, obj_dict: Dict[str, Any], prefix: str = "", _depth: int = 0, _seen: Optional[set] = None
    ) -> Result[None]:
        """Register a dictionary of objects recursively."""
        # Initialize seen set for circular reference detection
        if _seen is None:
            _seen = set()
        
        # Check for circular references
        dict_id = id(obj_dict)
        if dict_id in _seen:
            return Result.error("Circular reference detected in dictionary structure")
        
        _seen.add(dict_id)
        
        try:
            # Prevent infinite recursion
            if _depth > 10:
                return Result.error("Dictionary nesting too deep (max 10 levels)")

            for key, value in obj_dict.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    # Nested dictionary - recurse
                    result = self._register_dict(value, full_key, _depth + 1, _seen)
                    if not result.is_ok():
                        return result
                else:
                    # Process and expose the value using exposer system
                    processed_value = self._process_object_for_registry(value, custom=False)
                    result = self._expose_with_system(processed_value, full_key)
                    if not result.is_ok():
                        return result
            return Ok(None)
        finally:
            # Remove from seen set when done with this level
            _seen.discard(dict_id)

    def _load_config(self) -> YaappConfig:
        """Load configuration using enhanced configuration system with environment variables and secrets support."""
        if self._config is not None:
            return self._config

        # Auto-detect config and secrets files in multiple locations
        config_file = None
        secrets_file = None

        # Check for config file override first (highest priority)
        if self._config_file_override:
            config_path = Path(self._config_file_override)
            if config_path.exists():
                config_file = str(config_path)
                print(f"Using config override: {config_file}")
            else:
                print(f"Warning: Config override file not found: {self._config_file_override}")
        
        # If no override or override file doesn't exist, use standard search paths
        if not config_file:
            # Search paths: current directory, script directory
            search_paths = self._get_config_search_paths()

            # Look for main config files in all search paths
            for search_path in search_paths:
                for config_name in ["yaapp.yaml", "yaapp.yml", "yaapp.json"]:
                    config_path = search_path / config_name
                    if config_path.exists():
                        config_file = str(config_path)
                        break
                if config_file:
                    break

        # Look for secrets files in all search paths
        search_paths = self._get_config_search_paths()
        for search_path in search_paths:
            for secrets_name in [
                "yaapp.secrets.yaml",
                "yaapp.secrets.yml", 
                "yaapp.secrets.json",
            ]:
                secrets_path = search_path / secrets_name
                if secrets_path.exists():
                    secrets_file = str(secrets_path)
                    break
            if secrets_file:
                break

        # Load configuration with full feature support:
        # - Environment variables (YAAPP_*)
        # - Config file with variable substitution
        # - Secrets file auto-merging
        # - Comprehensive defaults and validation
        self._config = YaappConfig.load(
            config_file=config_file, secrets_file=secrets_file, env_prefix="YAAPP_"
        )

        return self._config
    
    def _get_config_search_paths(self) -> List[Path]:
        """Get list of paths to search for configuration files.
        
        Search order:
        1. Current working directory
        2. Directory containing the main script
        3. Directory containing the calling script (if different)
        """
        import sys
        
        search_paths = []
        
        # 1. Current working directory
        search_paths.append(Path.cwd())
        
        # 2. Directory containing the main script
        if len(sys.argv) > 0 and sys.argv[0]:
            main_script = Path(sys.argv[0]).resolve()
            if main_script.exists():
                main_script_dir = main_script.parent
                if main_script_dir not in search_paths:
                    search_paths.append(main_script_dir)
        
        # 3. Directory containing the calling script (for imported modules)
        import inspect
        try:
            # Get the frame that called into yaapp
            frame = inspect.currentframe()
            while frame:
                frame_file = frame.f_code.co_filename
                if frame_file and not frame_file.endswith(('core.py', 'app.py', '__init__.py')):
                    caller_script = Path(frame_file).resolve()
                    if caller_script.exists():
                        caller_script_dir = caller_script.parent
                        if caller_script_dir not in search_paths:
                            search_paths.append(caller_script_dir)
                        break
                frame = frame.f_back
        except Exception:
            # If frame inspection fails, continue with what we have
            pass
        
        return search_paths

    def _get_app_name(self) -> str:
        """Get the application name from config or default."""
        config = self._load_config()

        # Check custom config for app name first
        app_name = config.get("app.name") or config.custom.get("app_name")

        if app_name:
            return app_name

        # Try to infer from the calling script
        import sys

        if len(sys.argv) > 0:
            script_name = Path(sys.argv[0]).stem
            if script_name and script_name != "python":
                return script_name

        return "yaapp"  # Fallback

    def _get_current_context_commands(self) -> Dict[str, Any]:
        """Get available commands in the current context using context tree."""
        return self._context_tree.get_current_context_items()

    def _get_prompt_string(self) -> str:
        """Get the current prompt string based on context."""
        app_name = self._get_app_name()
        context_path = self._context_tree.get_current_context_path()
        if context_path:
            context_str = ":".join(context_path)
            return f"{app_name}:{context_str}> "
        return f"{app_name}> "

    def _is_leaf_command(self, command_name: str) -> bool:
        """Check if a command is a leaf (executable) or has subcommands using context tree."""
        return self._context_tree.is_leaf_command(command_name)

    def _enter_context(self, context_name: str) -> bool:
        """Enter a command context using context tree. Returns True if successful."""
        return self._context_tree.enter_context(context_name)

    def _exit_context(self) -> bool:
        """Exit current context using context tree. Returns True if successful."""
        return self._context_tree.exit_context()

    def _merge_config(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def execute_function(self, name: str, *args, **kwargs) -> Result[Any]:
        """
        Execute a function by name synchronously.

        Args:
            name: Function name or path
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result containing function result or error
        """
        return self._execute_from_registry(name, **kwargs)

    def _execute_from_registry(self, name: str, **kwargs) -> Result[Any]:
        """
        Execute function from registry using its associated exposer.

        Args:
            name: Name of function in registry
            **kwargs: Arguments to pass to function

        Returns:
            Result containing function result or error
        """
        if name not in self._registry:
            return Result.error(f"Function '{name}' not found in registry")

        obj, exposer = self._registry[name]

        # Use exposer to execute the function
        if hasattr(exposer, "run"):
            result = exposer.run(obj, **kwargs)
            if hasattr(result, "is_ok") and hasattr(result, "unwrap"):
                # It's already a Result object
                return result
            else:
                # Wrap result in Ok
                return Ok(result)
        else:
            # Fallback to direct execution
            try:
                result = obj(**kwargs)
                return Ok(result)
            except Exception as e:
                return Result.error(f"Execution failed: {str(e)}")

    def get_registry_item(self, name: str) -> Result[Any]:
        """
        Get raw object from registry.

        Args:
            name: Name of item in registry

        Returns:
            Result containing raw object from registry or error
        """
        if name not in self._registry:
            return Result.error(f"Item '{name}' not found in registry")

        obj, exposer = self._registry[name]
        return Ok(obj)

    def get_registry_exposer(self, name: str) -> Result[BaseExposer]:
        """
        Get exposer for item from registry.

        Args:
            name: Name of item in registry

        Returns:
            Result containing exposer object from registry or error
        """
        if name not in self._registry:
            return Result.error(f"Item '{name}' not found in registry")

        obj, exposer = self._registry[name]
        return Ok(exposer)

    def get_registry_items(self) -> Dict[str, Any]:
        """
        Get all raw objects from registry (backward compatibility).

        Returns:
            Dictionary of name -> raw object
        """
        return {name: obj for name, (obj, exposer) in self._registry.items()}

    def _detect_execution_mode(self) -> str:
        """Detect the execution mode (cli, server, tui)."""
        # Simple implementation - defaults to CLI
        # In a real implementation, this might check environment variables,
        # command line arguments, or configuration files
        return "cli"

    def _call_function_with_args(self, func: Callable, args: list) -> Any:
        """Call a function with string arguments, attempting to parse them."""
        # Get function signature for parameter type inference
        sig = inspect.signature(func)
        param_info = {param.name: param for param in sig.parameters.values()}

        parsed_args = []
        kwargs = {}

        for arg in args:
            if arg.startswith("--"):
                if "=" in arg:
                    # Keyword argument: --key=value
                    key, value = arg[2:].split("=", 1)
                else:
                    # Boolean flag: --key (without value)
                    key = arg[2:]
                    value = "true"

                # Convert hyphenated key to underscore (click style -> python style)
                python_key = key.replace("-", "_")

                # Try to infer type from function signature
                if python_key in param_info:
                    param = param_info[python_key]
                    if param.annotation == bool or (
                        param.default is not None and isinstance(param.default, bool)
                    ):
                        # Boolean parameter
                        kwargs[python_key] = value.lower() in ("true", "1", "yes", "on")
                    elif param.annotation == int or (
                        param.default is not None and isinstance(param.default, int)
                    ):
                        # Integer parameter
                        try:
                            kwargs[python_key] = int(value)
                        except ValueError:
                            # Graceful fallback to string
                            kwargs[python_key] = value
                    elif param.annotation == float or (
                        param.default is not None and isinstance(param.default, float)
                    ):
                        # Float parameter
                        try:
                            kwargs[python_key] = float(value)
                        except ValueError:
                            # Graceful fallback to string
                            kwargs[python_key] = value
                    else:
                        # String or other parameter
                        kwargs[python_key] = value
                else:
                    # Unknown parameter - try JSON parsing
                    try:
                        kwargs[python_key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        # JSON parsing failed, use as string
                        kwargs[python_key] = value
            else:
                # Positional argument - try to parse as JSON, fallback to string
                try:
                    parsed_args.append(json.loads(arg))
                except (json.JSONDecodeError, TypeError):
                    # JSON parsing failed, use as string
                    parsed_args.append(arg)

        # Call the function
        if kwargs:
            return func(*parsed_args, **kwargs)
        else:
            return func(*parsed_args)

