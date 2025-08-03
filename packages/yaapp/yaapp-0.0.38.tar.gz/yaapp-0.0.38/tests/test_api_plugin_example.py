#!/usr/bin/env python3
"""
Standard pytest tests for the Universal API Plugin example.

This test suite follows pytest conventions and can be run with:
    uv run pytest tests/test_api_plugin_example.py
    uv run pytest tests/test_api_plugin_example.py -v
    uv run pytest tests/test_api_plugin_example.py::test_docker_api_discovery
    uv run pytest tests/test_api_plugin_example.py::test_api_plugin_docker_discovery
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestAPIPluginExample:
    """Standard pytest tests for the Universal API Plugin example."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.repo_root = Path(__file__).parent.parent
        cls.example_dir = cls.repo_root / "examples" / "plugins" / "api"
        cls.simple_test_script = cls.example_dir / "simple-test.py"
        
        # Verify the example directory exists
        assert cls.example_dir.exists(), f"Example directory not found: {cls.example_dir}"
        assert cls.simple_test_script.exists(), f"Simple test script not found: {cls.simple_test_script}"
    
    def run_simple_test_script(self, config_file="yaapp.yaml", timeout=60):
        """Run the simple-test.py script and return the result."""
        # Run from repo root to test portability
        result = subprocess.run(
            [sys.executable, str(self.simple_test_script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.repo_root
        )
        return result
    
    def test_simple_test_script_runs_successfully(self):
        """Test that simple-test.py runs without errors."""
        result = self.run_simple_test_script()
        
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"
        assert "🚀 Universal API Plugin - Simple Test" in result.stdout
        assert "✅ Discovered" in result.stdout
        assert "endpoints" in result.stdout
    
    def test_docker_api_discovery(self):
        """Test Docker API discovery with default config."""
        result = self.run_simple_test_script()
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        output = result.stdout
        
        # Verify Docker API specific output
        assert "📡 API Type: openapi" in output
        assert "🌐 Base URL: http://localhost/v1.42" in output
        assert "Docker Engine API" in output
        
        # Verify endpoints are discovered
        assert "containers/json" in output
        assert "containers/create" in output
        assert "containers/inspect" in output
        
        # Verify HTTP methods and paths
        assert "GET" in output
        assert "POST" in output
        assert "/containers/" in output
    
    def test_endpoint_count_reasonable(self):
        """Test that a reasonable number of endpoints are discovered."""
        result = self.run_simple_test_script()
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        # Extract endpoint count
        import re
        match = re.search(r'✅ Discovered (\d+) endpoints', result.stdout)
        assert match, "Could not find endpoint count in output"
        
        endpoint_count = int(match.group(1))
        
        # Docker API should have 50-150 endpoints
        assert 50 <= endpoint_count <= 150, f"Unexpected endpoint count: {endpoint_count}"
    
    def test_config_files_exist_and_valid(self):
        """Test that all config files exist and are valid YAML."""
        config_files = [
            "yaapp.yaml",
            "yaapp-httpbin.yaml", 
            "yaapp-petstore.yaml"
        ]
        
        for config_file in config_files:
            config_path = self.example_dir / config_file
            assert config_path.exists(), f"Config file missing: {config_file}"
            
            # Verify it's valid YAML with required structure
            import yaml
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            assert 'api' in config_data, f"Missing 'api' section in {config_file}"
            assert 'type' in config_data['api'], f"Missing 'type' in {config_file}"
            assert config_data['api']['type'] == 'openapi', f"Invalid type in {config_file}"
            assert 'spec_url' in config_data['api'], f"Missing 'spec_url' in {config_file}"
            assert 'base_url' in config_data['api'], f"Missing 'base_url' in {config_file}"
    
    def test_plugin_import_works(self):
        """Test that the API plugin can be imported correctly."""
        from yaapp.plugins.api.api import Api
        
        # Test basic instantiation
        plugin = Api({})
        assert hasattr(plugin, 'expose_to_registry')
        assert hasattr(plugin, 'execute_call')
        assert hasattr(plugin, '_discovered_methods')
    
    def test_script_works_from_different_directory(self):
        """Test that the script works when run from a different directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Run from temporary directory
            result = subprocess.run(
                [sys.executable, str(self.simple_test_script)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir
            )
            
            assert result.returncode == 0, f"Script failed from different directory: {result.stderr}"
            assert "✅ Discovered" in result.stdout
    
    def test_httpbin_api_config_switch(self):
        """Test switching to HTTPBin API config."""
        # Create a temporary copy of the example directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_example_dir = Path(temp_dir) / "api"
            shutil.copytree(self.example_dir, temp_example_dir)
            
            # Switch to HTTPBin config
            httpbin_config = temp_example_dir / "yaapp-httpbin.yaml"
            main_config = temp_example_dir / "yaapp.yaml"
            shutil.copy(httpbin_config, main_config)
            
            # Update the simple-test script path
            temp_script = temp_example_dir / "simple-test.py"
            
            # Run the test
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.repo_root
            )
            
            assert result.returncode == 0, f"HTTPBin test failed: {result.stderr}"
            output = result.stdout
            
            # Verify HTTPBin specific output
            assert "🌐 Base URL: https://httpbin.org" in output
            assert "HTTPBin API" in output
    
    def test_petstore_api_config_switch(self):
        """Test switching to Petstore API config."""
        # Create a temporary copy of the example directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_example_dir = Path(temp_dir) / "api"
            shutil.copytree(self.example_dir, temp_example_dir)
            
            # Switch to Petstore config
            petstore_config = temp_example_dir / "yaapp-petstore.yaml"
            main_config = temp_example_dir / "yaapp.yaml"
            shutil.copy(petstore_config, main_config)
            
            # Update the simple-test script path
            temp_script = temp_example_dir / "simple-test.py"
            
            # Run the test
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.repo_root
            )
            
            assert result.returncode == 0, f"Petstore test failed: {result.stderr}"
            output = result.stdout
            
            # Verify Petstore specific output
            assert "🌐 Base URL: https://petstore3.swagger.io" in output
            assert "Swagger Petstore" in output
    
    def test_error_handling_missing_config(self):
        """Test error handling when config file is missing."""
        # Create a temporary directory without config
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy only the script, not the config
            temp_script = Path(temp_dir) / "simple-test.py"
            shutil.copy(self.simple_test_script, temp_script)
            
            # Run the test (should fail gracefully)
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repo_root
            )
            
            # Should fail but not crash
            assert result.returncode != 0 or "No API config found" in result.stdout


# Standalone test functions for pytest discovery
def test_api_plugin_example_basic():
    """Basic test that the API plugin example works."""
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    test_instance.test_simple_test_script_runs_successfully()


def test_api_plugin_docker_discovery():
    """Test Docker API discovery."""
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    test_instance.test_docker_api_discovery()


def test_api_plugin_config_files():
    """Test config files are valid."""
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    test_instance.test_config_files_exist_and_valid()


def test_api_plugin_import():
    """Test plugin import works."""
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    test_instance.test_plugin_import_works()


def test_api_plugin_portability():
    """Test script works from different directories."""
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    test_instance.test_script_works_from_different_directory()


if __name__ == "__main__":
    # Allow running directly for debugging
    pytest.main([__file__, "-v"])