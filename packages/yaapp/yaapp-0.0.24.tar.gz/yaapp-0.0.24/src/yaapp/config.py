"""
Enterprise-grade configuration system for yaapp with environment variables and secrets support.
"""

import os
import json
import re
HAS_YAML = False
yaml = None

# Try to import yaml from the system
try:
    import yaml
    HAS_YAML = True
except ImportError:
    # PyYAML not available - JSON-only mode
    pass
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
from .config_node import ConfigNode


class ConfigSource(Enum):
    """Configuration source priority order."""
    ENVIRONMENT = "environment"
    CONFIG_FILE = "config_file"
    SECRETS_FILE = "secrets_file"
    DEFAULT = "default"


def substitute_env_variables(data: Union[Dict, List, str, Any]) -> Any:
    """
    Recursively substitute environment variables in configuration data.
    Supports ${VAR:default} syntax.
    """
    if isinstance(data, str):
        # Pattern to match ${VAR:default} or ${VAR}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)
        
        return re.sub(pattern, replace_var, data)
    
    elif isinstance(data, dict):
        return {key: substitute_env_variables(value) for key, value in data.items()}
    
    elif isinstance(data, list):
        return [substitute_env_variables(item) for item in data]
    
    else:
        return data


@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "localhost"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    timeout: int = 30
    
    @classmethod
    def from_env(cls, prefix: str = "YAAPP_SERVER_") -> 'ServerConfig':
        """Load server config from environment variables."""
        return cls(
            host=os.getenv(f"{prefix}HOST", cls.host),
            port=int(os.getenv(f"{prefix}PORT", cls.port)),
            reload=os.getenv(f"{prefix}RELOAD", "false").lower() == "true",
            workers=int(os.getenv(f"{prefix}WORKERS", cls.workers)),
            timeout=int(os.getenv(f"{prefix}TIMEOUT", cls.timeout))
        )


@dataclass 
class SecurityConfig:
    """Security configuration settings."""
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    allowed_origins: list = field(default_factory=lambda: ["*"])
    rate_limit: int = 1000
    enable_cors: bool = True
    
    @classmethod
    def from_env(cls, prefix: str = "YAAPP_SECURITY_") -> 'SecurityConfig':
        """Load security config from environment variables."""
        allowed_origins = os.getenv(f"{prefix}ALLOWED_ORIGINS", "*")
        if allowed_origins != "*":
            allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]
        else:
            allowed_origins = ["*"]
            
        return cls(
            api_key=os.getenv(f"{prefix}API_KEY"),
            secret_key=os.getenv(f"{prefix}SECRET_KEY"),
            allowed_origins=allowed_origins,
            rate_limit=int(os.getenv(f"{prefix}RATE_LIMIT", cls.rate_limit)),
            enable_cors=os.getenv(f"{prefix}ENABLE_CORS", "true").lower() == "true"
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls, prefix: str = "YAAPP_LOG_") -> 'LoggingConfig':
        """Load logging config from environment variables."""
        return cls(
            level=os.getenv(f"{prefix}LEVEL", cls.level),
            format=os.getenv(f"{prefix}FORMAT", cls.format),
            file=os.getenv(f"{prefix}FILE"),
            max_size=int(os.getenv(f"{prefix}MAX_SIZE", cls.max_size)),
            backup_count=int(os.getenv(f"{prefix}BACKUP_COUNT", cls.backup_count))
        )


@dataclass
class YaappConfig:
    """Main yaapp configuration container."""
    server: ServerConfig = field(default_factory=ServerConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    custom: Dict[str, Any] = field(default_factory=dict)
    
    # Plugin configurations (discovered dynamically)
    plugins: Dict[str, Any] = field(default_factory=dict)
    discovered_sections: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize hierarchical configuration after dataclass creation."""
        self._root_node: Optional[ConfigNode] = None
        self._raw_config_data: Dict[str, Any] = {}
    
    @classmethod
    def load(cls, 
             config_file: Optional[Union[str, Path]] = None,
             secrets_file: Optional[Union[str, Path]] = None,
             env_prefix: str = "YAAPP_") -> 'YaappConfig':
        """
        Load configuration from multiple sources with priority order:
        1. Environment variables (highest priority)
        2. Config file
        3. Secrets file
        4. Defaults (lowest priority)
        """
        
        config = cls()
        
        # Load from files first (lower priority)
        if config_file:
            config._load_from_file(config_file)
        
        if secrets_file:
            config._load_secrets_from_file(secrets_file)
        
        # Load from environment (higher priority)
        config._load_from_environment(env_prefix)
        
        return config
    
    @property
    def root(self) -> ConfigNode:
        """Get the hierarchical configuration root node."""
        if self._root_node is None:
            self._create_hierarchical_config()
        return self._root_node
    
    def get_plugin_config(self, plugin_name: str) -> ConfigNode:
        """Get plugin configuration with inheritance."""
        return getattr(self.root, plugin_name)
    
    def _create_hierarchical_config(self) -> None:
        """Create hierarchical configuration from current state."""
        # Build complete config data including all sections
        config_data = {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'reload': self.server.reload,
                'workers': self.server.workers,
                'timeout': self.server.timeout
            },
            'security': {
                'allowed_origins': self.security.allowed_origins,
                'rate_limit': self.security.rate_limit,
                'enable_cors': self.security.enable_cors,
                # Include secrets if available
                **({
                    'api_key': self.security.api_key,
                    'secret_key': self.security.secret_key
                } if self.security.api_key or self.security.secret_key else {})
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count
            },
            **self.custom,
            **self.discovered_sections
        }
        
        # Store raw data and create root node
        self._raw_config_data = config_data
        self._root_node = ConfigNode(config_data)
    
    def _load_from_file(self, config_file: Union[str, Path]) -> None:
        """Load configuration from YAML or JSON file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            return
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        print("Warning: YAML config file found but PyYAML not installed")
                        return
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Apply environment variable substitution
            data = substitute_env_variables(data)
            
            # Update configuration sections (merge, don't replace)
            if 'server' in data:
                for key, value in data['server'].items():
                    if hasattr(self.server, key):
                        setattr(self.server, key, value)
            if 'security' in data:
                # Don't load secrets from regular config file
                security_data = {k: v for k, v in data['security'].items() 
                               if k not in ['api_key', 'secret_key']}
                for key, value in security_data.items():
                    if hasattr(self.security, key):
                        setattr(self.security, key, value)
            if 'logging' in data:
                for key, value in data['logging'].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)
            if 'custom' in data:
                self.custom.update(data['custom'])
            
            # Discover and configure plugins
            self._discover_and_configure_plugins(data)
                
        except (json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
    
    def _discover_and_configure_plugins(self, config_data: Dict[str, Any]) -> None:
        """Discover and configure plugins based on configuration sections."""
        # Reserved sections that are not plugins
        reserved_sections = {
            'server', 'security', 'logging', 'custom', 'app',
            'execution_mode', 'auto_sampling', 'execution_engine', 
            'cli', 'environment'
        }
        
        # Find potential plugin sections
        plugin_sections = [
            key for key in config_data.keys() 
            if key not in reserved_sections
        ]
        
        if not plugin_sections:
            return
        
        # Import discovery system
        from .discovery import PluginDiscovery
        discovery = PluginDiscovery()
        
        # Discover available plugins
        discovered_plugins = discovery.discover_plugins(plugin_sections)
        
        # Configure discovered plugins
        for section_name, plugin_imported in discovered_plugins.items():
            if section_name in config_data:
                try:
                    # Store plugin configuration
                    plugin_config = config_data[section_name]
                    self.discovered_sections[section_name] = plugin_config
                    
                    # Plugin is already registered via @yaapp.expose decorator during import
                    # Just store the config for reference
                    self.plugins[section_name] = {
                        'imported': plugin_imported,
                        'config': plugin_config
                    }
                    
                    print(f"✅ Loaded plugin: {section_name}")
                    
                except Exception as e:
                    # Log warning but continue with other plugins
                    print(f"Warning: Failed to configure plugin '{section_name}': {e}")
                    continue
        
        # Warn about sections that couldn't be matched to plugins
        unmatched = set(plugin_sections) - set(discovered_plugins.keys())
        for section in unmatched:
            # Store unmatched sections in discovered_sections so they're available in hierarchical config
            if section in config_data:
                self.discovered_sections[section] = config_data[section]
            print(f"Warning: No plugin found for configuration section '{section}'")
            print(f"  Consider installing plugin or removing section from config")
    
    def register_discovered_plugins(self, app_instance):
        """Register discovered plugins with the app instance."""
        # Plugins are registered via @yaapp.expose decorator during import as classes
        # We need to instantiate them with their configuration
        for section_name, plugin_info in self.plugins.items():
            if isinstance(plugin_info, dict) and plugin_info.get('imported'):
                try:
                    # Get the plugin class from the registry
                    plugin_result = app_instance.get_registry_item(section_name)
                    if plugin_result.is_ok():
                        plugin_class = plugin_result.unwrap()
                        
                        # Check if it's already an instance or still a class
                        if isinstance(plugin_class, type):
                            # It's a class, instantiate it with configuration
                            plugin_config = plugin_info.get('config', {})
                            plugin_instance = plugin_class(plugin_config)
                            
                            # Set the yaapp reference
                            plugin_instance.yaapp = app_instance
                            
                            # Replace the class with the instance in the registry
                            exposer = app_instance._registry[section_name][1]
                            app_instance._registry[section_name] = (plugin_instance, exposer)
                            
                            # Call the exposer's expose method on the new instance to trigger expose_to_registry
                            if hasattr(exposer, 'expose'):
                                exposer.expose(plugin_instance, section_name, custom=True)
                            
                            print(f"🔗 Plugin ready: {section_name} (instantiated with config)")
                        else:
                            # Already an instance
                            print(f"🔗 Plugin ready: {section_name} (already instantiated)")
                    else:
                        print(f"Warning: Plugin '{section_name}' not found in registry")
                except Exception as e:
                    print(f"Warning: Failed to instantiate plugin '{section_name}': {e}")
            else:
                print(f"Warning: Plugin '{section_name}' was not properly imported")
    
    # Plugin methods are exposed by @yaapp.expose decorator, instances created in register_discovered_plugins
    
    def _load_secrets_from_file(self, secrets_file: Union[str, Path]) -> None:
        """Load secrets from encrypted/secure file."""
        secrets_path = Path(secrets_file)
        
        if not secrets_path.exists():
            return
        
        try:
            with open(secrets_path, 'r') as f:
                if secrets_path.suffix.lower() in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        print("Warning: YAML secrets file found but PyYAML not installed")
                        return
                    secrets = yaml.safe_load(f)
                else:
                    secrets = json.load(f)
            
            # Apply environment variable substitution to secrets
            secrets = substitute_env_variables(secrets)
            
            # Load only secret values
            if 'security' in secrets:
                if 'api_key' in secrets['security']:
                    self.security.api_key = secrets['security']['api_key']
                if 'secret_key' in secrets['security']:
                    self.security.secret_key = secrets['security']['secret_key']
                    
        except (json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Failed to load secrets file {secrets_file}: {e}")
    
    def _load_from_environment(self, prefix: str = "YAAPP_") -> None:
        """Load configuration from environment variables (only overrides existing values)."""
        # Apply environment overrides to existing config (don't replace with defaults)
        server_prefix = f"{prefix}SERVER_"
        security_prefix = f"{prefix}SECURITY_"
        log_prefix = f"{prefix}LOG_"
        
        # Override server config if environment variables exist
        for env_var, attr_name in [
            (f"{server_prefix}HOST", "host"),
            (f"{server_prefix}PORT", "port"),
            (f"{server_prefix}RELOAD", "reload"),
            (f"{server_prefix}WORKERS", "workers"),
            (f"{server_prefix}TIMEOUT", "timeout")
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name in ["port", "workers", "timeout"]:
                    value = int(value)
                elif attr_name == "reload":
                    value = value.lower() == "true"
                setattr(self.server, attr_name, value)
        
        # Override security config if environment variables exist
        for env_var, attr_name in [
            (f"{security_prefix}API_KEY", "api_key"),
            (f"{security_prefix}SECRET_KEY", "secret_key"),
            (f"{security_prefix}ALLOWED_ORIGINS", "allowed_origins"),
            (f"{security_prefix}RATE_LIMIT", "rate_limit"),
            (f"{security_prefix}ENABLE_CORS", "enable_cors")
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name == "allowed_origins":
                    value = [origin.strip() for origin in value.split(",")] if value != "*" else ["*"]
                elif attr_name == "rate_limit":
                    value = int(value)
                elif attr_name == "enable_cors":
                    value = value.lower() == "true"
                setattr(self.security, attr_name, value)
        
        # Override logging config if environment variables exist
        for env_var, attr_name in [
            (f"{log_prefix}LEVEL", "level"),
            (f"{log_prefix}FORMAT", "format"),
            (f"{log_prefix}FILE", "file"),
            (f"{log_prefix}MAX_SIZE", "max_size"),
            (f"{log_prefix}BACKUP_COUNT", "backup_count")
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name in ["max_size", "backup_count"]:
                    value = int(value)
                setattr(self.logging, attr_name, value)
        
        # Load custom environment variables
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}CUSTOM_"):
                custom_key = key[len(f"{prefix}CUSTOM_"):].lower()
                self.custom[custom_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        parts = key.split('.')
        obj = self
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return default
        
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)."""
        return {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'reload': self.server.reload,
                'workers': self.server.workers,
                'timeout': self.server.timeout
            },
            'security': {
                'allowed_origins': self.security.allowed_origins,
                'rate_limit': self.security.rate_limit,
                'enable_cors': self.security.enable_cors,
                # Secrets intentionally excluded
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count
            },
            'custom': self.custom,
            'discovered_plugins': list(self.plugins.keys())
        }


class ConfigManager:
    """Singleton configuration manager for global access."""
    
    _instance: Optional[YaappConfig] = None
    
    @classmethod
    def get_config(cls) -> YaappConfig:
        """Get the global configuration instance."""
        if cls._instance is None:
            cls._instance = YaappConfig.load()
        return cls._instance
    
    @classmethod
    def set_config(cls, config: YaappConfig) -> None:
        """Set the global configuration instance."""
        cls._instance = config
    
    @classmethod
    def load_config(cls, 
                   config_file: Optional[Union[str, Path]] = None,
                   secrets_file: Optional[Union[str, Path]] = None) -> YaappConfig:
        """Load and set global configuration."""
        cls._instance = YaappConfig.load(config_file, secrets_file)
        return cls._instance


# Convenience function for common usage
def get_config() -> YaappConfig:
    """Get the global yaapp configuration."""
    return ConfigManager.get_config()


# Example usage and defaults
if __name__ == "__main__":
    # Example configuration file structure
    example_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 4
        },
        "security": {
            "allowed_origins": ["https://myaapp.com", "https://api.myaapp.com"],
            "rate_limit": 500
        },
        "logging": {
            "level": "DEBUG",
            "file": "/var/log/yaapp.log"
        },
        "custom": {
            "app_name": "My yaapp Application",
            "version": "1.0.0"
        }
    }
    
    print("Example config structure:")
    print(json.dumps(example_config, indent=2))