"""
Runner discovery system for yaapp.
Scans runner directories and discovers help() and run() functions.
"""

import os
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Tuple, Callable


class RunnerDiscovery:
    """Discovers and manages runner modules."""
    
    def __init__(self):
        """Initialize runner discovery."""
        self._discovered_runners = {}
        self._runner_cache = {}
    
    def discover_runners(self) -> Dict[str, Tuple[Callable, Callable]]:
        """
        Discover all runners by scanning runner directories (lazy loading).
        
        Returns:
            Dict mapping runner_name -> (help_func, run_func)
        """
        if self._discovered_runners:
            return self._discovered_runners
        
        # Get the yaapp package directory
        yaapp_dir = Path(__file__).parent
        runners_dir = yaapp_dir / "runners"
        
        if not runners_dir.exists():
            print(f"⚠️ Runners directory not found: {runners_dir}")
            return {}
        
        # Scan each subdirectory for runner.py files (but don't load them yet)
        available_runners = {}
        for runner_path in runners_dir.iterdir():
            if not runner_path.is_dir():
                continue
            
            runner_name = runner_path.name
            runner_file = runner_path / "runner.py"
            
            if runner_file.exists():
                # Store the path for lazy loading, don't load the module yet
                available_runners[runner_name] = runner_file
        
        # Only load the click runner immediately (it's lightweight and always needed)
        if 'click' in available_runners:
            try:
                help_func, run_func = self._load_runner_module('click', available_runners['click'])
                if help_func and run_func:
                    self._discovered_runners['click'] = (help_func, run_func)
                    print(f"✅ Discovered runner: click")
            except Exception as e:
                print(f"⚠️ Failed to load runner 'click': {e}")
        
        # Store available runners for lazy loading
        self._available_runner_paths = available_runners
        
        return self._discovered_runners
    
    def _load_runner_module(self, runner_name: str, runner_file: Path) -> Tuple[Callable, Callable]:
        """
        Load a runner module and extract help() and run() functions.
        
        Returns:
            Tuple of (help_func, run_func) or (None, None) if invalid
        """
        try:
            # Create module spec
            spec = importlib.util.spec_from_file_location(f"yaapp.runners.{runner_name}", runner_file)
            if not spec or not spec.loader:
                return None, None
            
            # Load the module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required functions
            help_func = getattr(module, 'help', None)
            run_func = getattr(module, 'run', None)
            
            # Validate functions exist and are callable (silently)
            if help_func is None or run_func is None:
                return None, None
                
            if not callable(help_func) or not callable(run_func):
                return None, None
            
            # Validate function signatures
            help_sig = inspect.signature(help_func)
            if len(help_sig.parameters) != 0:
                print(f"⚠️ Runner '{runner_name}': help() should take no parameters")
                return None, None
            
            run_sig = inspect.signature(run_func)
            if len(run_sig.parameters) < 1:
                print(f"⚠️ Runner '{runner_name}': run() should take at least app_instance parameter")
                return None, None
            
            return help_func, run_func
            
        except Exception as e:
            print(f"⚠️ Error loading runner '{runner_name}': {e}")
            return None, None
    
    def get_runner_help(self, runner_name: str) -> str:
        """Get help text for a specific runner."""
        if runner_name not in self._discovered_runners:
            return f"Runner '{runner_name}' not found"
        
        help_func, _ = self._discovered_runners[runner_name]
        try:
            return help_func()
        except Exception as e:
            return f"Error getting help for '{runner_name}': {e}"
    
    def run_runner(self, runner_name: str, app_instance, **kwargs):
        """Execute a specific runner (with lazy loading)."""
        # Try to load the runner if not already loaded
        if runner_name not in self._discovered_runners:
            self._lazy_load_runner(runner_name)
        
        if runner_name not in self._discovered_runners:
            print(f"⚠️ Runner '{runner_name}' not found")
            return
        
        _, run_func = self._discovered_runners[runner_name]
        try:
            return run_func(app_instance, **kwargs)
        except Exception as e:
            print(f"❌ Error running '{runner_name}': {e}")
    
    def _lazy_load_runner(self, runner_name: str):
        """Lazy load a runner when it's actually needed."""
        if not hasattr(self, '_available_runner_paths'):
            return
        
        if runner_name not in self._available_runner_paths:
            return
        
        runner_file = self._available_runner_paths[runner_name]
        try:
            help_func, run_func = self._load_runner_module(runner_name, runner_file)
            if help_func and run_func:
                self._discovered_runners[runner_name] = (help_func, run_func)
                print(f"✅ Discovered runner: {runner_name}")
        except Exception as e:
            print(f"⚠️ Failed to load runner '{runner_name}': {e}")
    
    def get_available_runners(self) -> Dict[str, str]:
        """
        Get available runners with their help text.
        
        Returns:
            Dict mapping runner_name -> help_text
        """
        runners = {}
        for runner_name in self._discovered_runners.keys():
            runners[runner_name] = self.get_runner_help(runner_name)
        return runners