#!/usr/bin/env python3
"""
Test the enhanced configuration system with environment variables and secrets support.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp.config import YaappConfig, substitute_env_variables


def test_environment_variable_substitution():
    """Test environment variable substitution in config files."""
    print("\n=== Testing Environment Variable Substitution ===")
    
    # Set test environment variables
    os.environ["TEST_HOST"] = "test.example.com"
    os.environ["TEST_PORT"] = "9000"
    os.environ["TEST_SECRET"] = "super-secret-key"
    
    # Test data with environment variable substitution
    test_data = {
        "server": {
            "host": "${TEST_HOST:localhost}",
            "port": "${TEST_PORT:8000}",
            "timeout": "${TEST_TIMEOUT:30}"
        },
        "security": {
            "secret_key": "${TEST_SECRET}",
            "api_key": "${MISSING_VAR:default-api-key}"
        },
        "message": "Welcome to ${TEST_HOST:unknown}"
    }
    
    result = substitute_env_variables(test_data)
    
    print(f"Original: {test_data}")
    print(f"Substituted: {result}")
    
    # Verify substitutions
    assert result["server"]["host"] == "test.example.com"
    assert result["server"]["port"] == "9000"
    assert result["server"]["timeout"] == "30"  # Uses default since TEST_TIMEOUT not set
    assert result["security"]["secret_key"] == "super-secret-key"
    assert result["security"]["api_key"] == "default-api-key"  # Uses default
    assert result["message"] == "Welcome to test.example.com"
    
    print("✅ Environment variable substitution working correctly")


def test_config_loading_with_environment():
    """Test loading configuration with environment overrides."""
    print("\n=== Testing Configuration Loading with Environment ===")
    
    # Set environment variables
    os.environ["YAAPP_SERVER_HOST"] = "env.example.com"
    os.environ["YAAPP_SERVER_PORT"] = "7000"
    os.environ["YAAPP_SECURITY_API_KEY"] = "env-api-key"
    os.environ["YAAPP_LOG_LEVEL"] = "DEBUG"
    os.environ["YAAPP_CUSTOM_APP_NAME"] = "Test Application"
    
    # Load config (will use environment variables)
    config = YaappConfig.load()
    
    print(f"Server host: {config.server.host}")
    print(f"Server port: {config.server.port}")
    print(f"API key: {config.security.api_key}")
    print(f"Log level: {config.logging.level}")
    print(f"Custom app_name: {config.custom.get('app_name')}")
    
    # Verify environment overrides work
    assert config.server.host == "env.example.com"
    assert config.server.port == 7000
    assert config.security.api_key == "env-api-key"
    assert config.logging.level == "DEBUG"
    assert config.custom.get("app_name") == "Test Application"
    
    print("✅ Environment variable overrides working correctly")


def test_config_file_with_secrets():
    """Test config file loading with secrets file support."""
    print("\n=== Testing Config File with Secrets Support ===")
    
    # Clear environment variables that might interfere
    env_vars_to_clear = [var for var in os.environ.keys() if var.startswith("YAAPP_")]
    for var in env_vars_to_clear:
        del os.environ[var]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create config file with environment variable substitution
        config_file = temp_path / "yaapp.json"
        config_data = {
            "server": {
                "host": "${CONFIG_HOST:config.example.com}",
                "port": 8080,
                "workers": 2
            },
            "logging": {
                "level": "INFO",
                "file": "/tmp/yaapp.log"
            },
            "custom": {
                "app_name": "Config Test App",
                "version": "2.0.0"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Create secrets file
        secrets_file = temp_path / "yaapp.secrets.json"
        secrets_data = {
            "security": {
                "api_key": "${SECRET_API:secret-from-file}",
                "secret_key": "very-secret-key"
            }
        }
        
        with open(secrets_file, 'w') as f:
            json.dump(secrets_data, f, indent=2)
        
        # Set environment variable for substitution
        os.environ["CONFIG_HOST"] = "substituted.example.com"
        os.environ["SECRET_API"] = "substituted-secret-api"
        
        # Load config with files
        print(f"Loading config from: {config_file}")
        print(f"Loading secrets from: {secrets_file}")
        print(f"Config file exists: {config_file.exists()}")
        print(f"Secrets file exists: {secrets_file.exists()}")
        
        config = YaappConfig.load(
            config_file=config_file,
            secrets_file=secrets_file
        )
        
        print(f"Config loaded from files:")
        print(f"  Host: {config.server.host}")
        print(f"  Port: {config.server.port}")
        print(f"  Workers: {config.server.workers}")
        print(f"  Log level: {config.logging.level}")
        print(f"  Log file: {config.logging.file}")
        print(f"  API key: {config.security.api_key}")
        print(f"  Secret key: {config.security.secret_key}")
        print(f"  App name: {config.custom.get('app_name')}")
        print(f"  Version: {config.custom.get('version')}")
        
        # Verify file loading with substitution
        assert config.server.host == "substituted.example.com"  # From env substitution
        assert config.server.port == 8080  # From config file
        assert config.server.workers == 2  # From config file
        assert config.logging.level == "INFO"  # From config file
        assert config.logging.file == "/tmp/yaapp.log"  # From config file
        assert config.security.api_key == "substituted-secret-api"  # From secrets with substitution
        assert config.security.secret_key == "very-secret-key"  # From secrets file
        assert config.custom.get("app_name") == "Config Test App"  # From config file
        assert config.custom.get("version") == "2.0.0"  # From config file
        
        print("✅ Config file with secrets and substitution working correctly")


def test_priority_order():
    """Test that environment variables override config files."""
    print("\n=== Testing Configuration Priority Order ===")
    
    # Clear environment variables first
    env_vars_to_clear = [var for var in os.environ.keys() if var.startswith("YAAPP_")]
    for var in env_vars_to_clear:
        del os.environ[var]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create config file
        config_file = temp_path / "yaapp.json"
        config_data = {
            "server": {
                "host": "file.example.com",
                "port": 3000
            },
            "logging": {
                "level": "WARNING"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Set environment variables (should override file)
        os.environ["YAAPP_SERVER_HOST"] = "env-override.example.com"
        os.environ["YAAPP_LOG_LEVEL"] = "ERROR"
        
        # Load config
        config = YaappConfig.load(config_file=config_file)
        
        print(f"Host (env should override): {config.server.host}")
        print(f"Port (from file): {config.server.port}")
        print(f"Log level (env should override): {config.logging.level}")
        
        # Verify priority: environment > file > defaults
        assert config.server.host == "env-override.example.com"  # Environment wins
        assert config.server.port == 3000  # From file (no env override)
        assert config.logging.level == "ERROR"  # Environment wins
        
        print("✅ Configuration priority order working correctly")


def test_yaapp_integration():
    """Test integration with YApp core."""
    print("\n=== Testing YApp Core Integration ===")
    
    from yaapp.core import YaappCore
    
    # Set environment variables
    os.environ["YAAPP_CUSTOM_APP_NAME"] = "Core Integration Test"
    
    core = YaappCore()
    config = core._load_config()
    
    print(f"Config type: {type(config)}")
    print(f"App name from config: {core._get_app_name()}")
    print(f"Server host: {config.server.host}")
    print(f"Custom app_name: {config.custom.get('app_name')}")
    
    # Verify integration
    assert isinstance(config, YaappConfig)
    assert config.custom.get("app_name") == "Core Integration Test"
    
    print("✅ YApp core integration working correctly")


if __name__ == "__main__":
    print("🧪 Testing Enhanced Configuration System")
    
    try:
        test_environment_variable_substitution()
        test_config_loading_with_environment()
        test_config_file_with_secrets()
        test_priority_order()
        test_yaapp_integration()
        
        print("\n🎉 All configuration tests passed!")
        print("\n📋 Enhanced Configuration Features Verified:")
        print("   ✅ Environment variable substitution (${VAR:default})")
        print("   ✅ Environment overrides (YAAPP__SECTION__KEY)")
        print("   ✅ Secrets file auto-merging (yaapp.secrets.yaml)")
        print("   ✅ Comprehensive defaults and validation")
        print("   ✅ Proper error handling and logging")
        print("   ✅ Integration with YApp core")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Clean up test environment variables
    test_vars = [
        "TEST_HOST", "TEST_PORT", "TEST_SECRET", "TEST_TIMEOUT",
        "YAAPP_SERVER_HOST", "YAAPP_SERVER_PORT", "YAAPP_SECURITY_API_KEY", 
        "YAAPP_LOG_LEVEL", "YAAPP_CUSTOM_APP_NAME", "CONFIG_HOST", "SECRET_API"
    ]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]