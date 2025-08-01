"""
Tests for hierarchical configuration inheritance system.
"""

import pytest
import tempfile
import json
from pathlib import Path

from yaapp.config import YaappConfig
from yaapp.config_node import ConfigNode


class TestConfigNode:
    """Test ConfigNode hierarchical inheritance."""
    
    def test_basic_access(self):
        """Test basic attribute access."""
        data = {
            "storage": {
                "backend": "git",
                "path": "/data"
            },
            "logging": {
                "level": "INFO"
            }
        }
        
        node = ConfigNode(data)
        
        # Test direct access
        assert node.storage.backend == "git"
        assert node.storage.path == "/data"
        assert node.logging.level == "INFO"
    
    def test_inheritance(self):
        """Test parent-child inheritance."""
        root_data = {
            "storage": {
                "backend": "git",
                "repository": "git@github.com:company/data.git",
                "path": "/data"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(message)s"
            }
        }
        
        plugin_data = {
            "enabled": True,
            "storage": {
                "path": "/data/auth"  # Override only path
            }
        }
        
        root = ConfigNode(root_data)
        plugin = ConfigNode(plugin_data, parent=root, path="authorization")
        
        # Test inheritance
        assert plugin.enabled == True
        assert plugin.storage.backend == "git"  # Should inherit from root
        assert plugin.storage.path == "/data/auth"  # Should use override
        assert plugin.storage.repository == "git@github.com:company/data.git"  # Should inherit
        assert plugin.logging.level == "INFO"  # Should inherit
    
    def test_auto_instantiation(self):
        """Test auto-instantiation of missing paths."""
        data = {"existing": "value"}
        node = ConfigNode(data)
        
        # Access non-existent path
        missing = node.missing.deeply.nested.path
        
        # Should create empty ConfigNode
        assert isinstance(missing, ConfigNode)
        assert not missing._data  # Should be empty
        assert missing._path == "missing.deeply.nested.path"
    
    def test_get_method(self):
        """Test safe get method with defaults."""
        data = {
            "storage": {
                "backend": "git"
            }
        }
        
        node = ConfigNode(data)
        
        # Test existing values
        assert node.get("storage").backend == "git"
        
        # Test missing values with defaults
        assert node.get("missing", "default") == "default"
        assert node.storage.get("missing", "default") == "default"


class TestYaappConfigHierarchical:
    """Test YaappConfig with hierarchical configuration."""
    
    def test_root_property(self):
        """Test root property creates ConfigNode."""
        config = YaappConfig()
        
        # Access root should create hierarchical config
        root = config.root
        
        assert isinstance(root, ConfigNode)
        assert root.server.host == "localhost"
        assert root.server.port == 8000
        assert root.logging.level == "INFO"
    
    def test_plugin_config_access(self):
        """Test get_plugin_config method."""
        config = YaappConfig()
        
        # Add some plugin configuration
        config.discovered_sections["authorization"] = {
            "enabled": True,
            "initial_admin_token": "test_token"
        }
        
        # Get plugin config
        auth_config = config.get_plugin_config("authorization")
        
        assert isinstance(auth_config, ConfigNode)
        assert auth_config.enabled == True
        assert auth_config.initial_admin_token == "test_token"
        
        # Should inherit from root
        assert auth_config.server.host == "localhost"
        assert auth_config.logging.level == "INFO"
    
    def test_config_inheritance_from_file(self):
        """Test configuration inheritance when loading from file."""
        config_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 9000
            },
            "storage": {
                "backend": "git",
                "repository": "git@github.com:company/data.git",
                "path": "/data"
            },
            "logging": {
                "level": "DEBUG"
            },
            "authorization": {
                "enabled": True,
                "initial_admin_token": "test_token",
                "storage": {
                    "path": "/data/auth"  # Override only path
                }
            }
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            # Load config
            config = YaappConfig.load(config_file=config_file)
            
            # Test hierarchical access
            root = config.root
            
            # Test root values
            assert root.server.host == "0.0.0.0"
            assert root.server.port == 9000
            assert root.storage.backend == "git"
            assert root.storage.path == "/data"
            assert root.logging.level == "DEBUG"
            
            # Test plugin inheritance
            auth = root.authorization
            assert auth.enabled == True
            assert auth.initial_admin_token == "test_token"
            
            # Test inheritance with override
            assert auth.storage.backend == "git"  # Inherited
            assert auth.storage.repository == "git@github.com:company/data.git"  # Inherited
            assert auth.storage.path == "/data/auth"  # Overridden
            
            # Test other inheritance
            assert auth.server.host == "0.0.0.0"  # Inherited
            assert auth.logging.level == "DEBUG"  # Inherited
            
        finally:
            # Clean up
            Path(config_file).unlink()
    
    def test_partial_override(self):
        """Test partial configuration override."""
        config = YaappConfig()
        
        # Set up root configuration
        config.discovered_sections.update({
            "authorization": {
                "enabled": True,
                "storage": {
                    "path": "/data/auth"  # Override only path
                }
            }
        })
        
        # Access hierarchical config
        auth = config.root.authorization
        
        # Should inherit server config
        assert auth.server.host == "localhost"
        assert auth.server.port == 8000
        
        # Should inherit logging config
        assert auth.logging.level == "INFO"
        
        # Should have plugin-specific config
        assert auth.enabled == True
        assert auth.storage.path == "/data/auth"


if __name__ == "__main__":
    pytest.main([__file__])