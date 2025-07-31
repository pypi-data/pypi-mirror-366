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
        """Find plugin class using multiple naming strategies."""
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
        # Try multiple module path patterns
        module_paths = [
            f"{search_path}.{module_name}.plugin",  # yaapp.plugins.router.plugin
            f"{search_path}.{module_name}",         # yaapp.plugins.router
        ]
        
        for full_module_path in module_paths:
            try:
                module = importlib.import_module(full_module_path)
                
                # Try multiple class name patterns
                class_names = [
                    f"{section_name.title()}Plugin",      # storage -> StoragePlugin
                    f"{section_name.title()}Manager",     # storage -> StorageManager
                    f"{section_name.title()}",            # storage -> Storage, router -> Router
                    "Plugin",                             # Generic Plugin class
                    module_name.title().replace('_', ''), # session_handler -> SessionHandler
                ]
                
                for class_name in class_names:
                    if hasattr(module, class_name):
                        return getattr(module, class_name)
                        
            except ImportError:
                continue
                
        return None