"""
Plugin discovery and loading system for yaapp.
Automatically discovers and loads plugins based on configuration sections.
"""

import importlib
import pkgutil
from typing import Dict, List, Any, Optional, Type
from pathlib import Path


class PluginDiscovery:
    """Plugin discovery and loading system."""
    
    def __init__(self):
        self._plugin_cache: Dict[str, Type] = {}
        self._search_paths = [
            'yaapp.plugins',
            'yaapp_plugins',  # External plugin namespace
        ]
    
    def discover_runners(self) -> Dict[str, Type]:
        """Discover all runner plugins by scanning the runners directory."""
        discovered = {}
        
        # Scan the runners directory
        try:
            import yaapp.plugins.runners as runners_package
            runners_path = Path(runners_package.__file__).parent
            
            # Find all subdirectories in the runners directory
            for item in runners_path.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    runner_name = item.name
                    plugin_class = self._try_load_runner(runner_name)
                    if plugin_class:
                        discovered[runner_name] = plugin_class
                        
        except Exception as e:
            print(f"Warning: Failed to scan runners directory: {e}")
            
        return discovered
    
    def _try_load_runner(self, runner_name: str) -> Optional[Type]:
        """Try to load a runner plugin from the runners directory."""
        module_path = f"yaapp.plugins.runners.{runner_name}.plugin"
        
        try:
            # Import the module - the @yaapp.expose() decorator will handle registration
            importlib.import_module(module_path)
            # Return a dummy marker to indicate successful import
            return True  # Runner was imported and registered via decorator
        except ImportError as e:
            print(f"Warning: Failed to import runner '{runner_name}': {e}")
            return None
    
    def discover_plugins(self, config_sections: List[str]) -> Dict[str, Type]:
        """Discover plugins based on configuration section names."""
        discovered = {}
        
        for section in config_sections:
            if section in self._plugin_cache:
                discovered[section] = self._plugin_cache[section]
                continue
                
            plugin_class = self._find_plugin_class(section)
            if plugin_class:
                self._plugin_cache[section] = plugin_class
                discovered[section] = plugin_class
                
        return discovered
    
    def _find_plugin_class(self, section_name: str) -> Optional[Type]:
        """Find plugin class using simple naming strategies."""
        strategies = [
            # Direct name match: storage -> yaapp.plugins.storage
            lambda name: f"{name}",
            # Underscore to hyphen: session_handler -> session-handler
            lambda name: name.replace('_', '-'),
            # Hyphen to underscore: session-handler -> session_handler
            lambda name: name.replace('-', '_'),
        ]
        
        for search_path in self._search_paths:
            for strategy in strategies:
                module_name = strategy(section_name)
                plugin_class = self._try_load_plugin(search_path, module_name, section_name)
                if plugin_class:
                    return plugin_class
                    
        return None
    
    def _try_load_plugin(self, search_path: str, module_name: str, section_name: str) -> Optional[Type]:
        """Try to load plugin from specific path and module name."""
        # Try the standard plugin.py pattern first
        module_paths = [
            f"{search_path}.{module_name}.plugin",  # yaapp.plugins.session.plugin
            f"{search_path}.{module_name}",         # yaapp.plugins.session (fallback)
        ]
        
        for full_module_path in module_paths:
            try:
                # Import the module - the @yaapp.expose() decorator will handle registration
                module = importlib.import_module(full_module_path)
                
                # Try to find a plugin class in the module
                plugin_class = self._find_plugin_class_in_module(module, section_name)
                if plugin_class:
                    return plugin_class
                
                # Fallback: return True to indicate successful import
                return True
                        
            except ImportError as e:
                continue
                
        return None