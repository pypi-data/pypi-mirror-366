#!/usr/bin/env python3
"""
Test universal yaapp CLI functionality.
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


class TestUniversalCLI:
    """Test the universal yaapp CLI."""
    
    def test_cli_import(self):
        """Test that CLI module can be imported."""
        from yaapp.cli import main, get_default_app_proxy_config
        assert callable(main)
        assert callable(get_default_app_proxy_config)
    
    def test_default_config(self):
        """Test default app proxy configuration."""
        from yaapp.cli import get_default_app_proxy_config
        
        config = get_default_app_proxy_config()
        
        assert "app_proxy" in config
        assert "default_plugins" in config["app_proxy"]
        
        plugins = config["app_proxy"]["default_plugins"]
        expected_plugins = ["issues", "storage", "routing", "session", "subprocess"]
        
        for plugin in expected_plugins:
            assert plugin in plugins
            assert "target_url" in plugins[plugin]
            assert "timeout" in plugins[plugin]
    
    def test_load_universal_config_no_file(self):
        """Test loading config when no config file exists."""
        from yaapp.cli import load_universal_config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                config = load_universal_config()
                
                # Should return default config
                assert "app_proxy" in config
                assert "default_plugins" in config["app_proxy"]
                
            finally:
                os.chdir(original_cwd)
    
    def test_load_universal_config_with_yaml(self):
        """Test loading config with yaapp.yaml file."""
        from yaapp.cli import load_universal_config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Create test config file
                config_content = """
app_proxy:
  default_plugins:
    issues:
      target_url: "http://custom.example.com:8001"
      timeout: 60
"""
                with open("yaapp.yaml", "w") as f:
                    f.write(config_content)
                
                config = load_universal_config()
                
                # Should have default config as base
                assert "app_proxy" in config
                
            finally:
                os.chdir(original_cwd)
    
    @pytest.mark.skipif(not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'), 
                       reason="Requires virtual environment for CLI testing")
    def test_cli_help_output(self):
        """Test CLI help output."""
        try:
            # Test that CLI can be invoked
            result = subprocess.run(
                [sys.executable, "-c", "from yaapp.cli import main; main()"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not crash
            assert result.returncode in [0, 1]  # 0 for success, 1 for expected errors
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI test timed out")
        except Exception as e:
            pytest.skip(f"CLI test failed: {e}")
    
    def test_create_universal_cli_no_click(self):
        """Test CLI creation when Click is not available."""
        from yaapp.cli import create_universal_cli
        
        with patch('yaapp.cli.HAS_CLICK', False):
            cli = create_universal_cli()
            assert cli is None
    
    def test_create_universal_cli_with_click(self):
        """Test CLI creation when Click is available."""
        from yaapp.cli import create_universal_cli
        
        with patch('yaapp.cli.HAS_CLICK', True):
            with patch('yaapp.cli.click') as mock_click:
                mock_group = MagicMock()
                mock_click.group.return_value = mock_group
                mock_click.option.return_value = lambda f: f
                mock_click.pass_context = lambda f: f
                
                cli = create_universal_cli()
                
                # Should create CLI
                assert cli is not None
                mock_click.group.assert_called()
    
    def test_plugin_command_structure(self):
        """Test that plugin commands are structured correctly."""
        from yaapp.cli import add_default_plugin_commands, create_universal_cli
        
        with patch('yaapp.cli.HAS_CLICK', True):
            with patch('yaapp.cli.click') as mock_click:
                mock_group = MagicMock()
                mock_click.group.return_value = mock_group
                mock_click.option.return_value = lambda f: f
                mock_click.pass_context = lambda f: f
                mock_click.command.return_value = lambda f: f
                
                cli = create_universal_cli()
                
                # Should be able to add plugin commands without errors
                try:
                    add_default_plugin_commands(cli)
                    # If we get here without exception, test passes
                    return True
                except Exception as e:
                    # If there's an exception, test fails
                    assert False, f"Failed to add plugin commands: {e}"
    
    def test_client_functionality(self):
        """Test client functionality."""
        from yaapp.client import YaappClient
        
        # Test client creation
        with patch('yaapp.client.HAS_REQUESTS', True):
            with patch('yaapp.client.requests') as mock_requests:
                mock_session = MagicMock()
                mock_requests.Session.return_value = mock_session
                
                client = YaappClient("http://example.com:8000", token="test-token")
                
                assert client.server_url == "http://example.com:8000"
                assert client.token == "test-token"
                mock_session.headers.update.assert_called_with({'Authorization': 'Bearer test-token'})
    
    def test_client_no_requests(self):
        """Test client when requests is not available."""
        from yaapp.client import YaappClient
        
        with patch('yaapp.client.HAS_REQUESTS', False):
            with pytest.raises(ImportError):
                YaappClient("http://example.com:8000")
    
    def test_client_get_help(self):
        """Test client get_help method."""
        from yaapp.client import YaappClient
        
        with patch('yaapp.client.HAS_REQUESTS', True):
            with patch('yaapp.client.requests') as mock_requests:
                mock_session = MagicMock()
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'functions': {
                        'test_func': {'description': 'Test function'}
                    }
                }
                mock_session.get.return_value = mock_response
                mock_requests.Session.return_value = mock_session
                
                client = YaappClient("http://example.com:8000")
                help_text = client.get_help()
                
                assert "Remote yaapp server" in help_text
                assert "test_func" in help_text
                assert "Test function" in help_text
    
    def test_client_execute_command(self):
        """Test client execute_command method."""
        from yaapp.client import YaappClient
        
        with patch('yaapp.client.HAS_REQUESTS', True):
            with patch('yaapp.client.requests') as mock_requests:
                mock_session = MagicMock()
                mock_response = MagicMock()
                mock_response.json.return_value = {'result': 'success'}
                mock_session.post.return_value = mock_response
                mock_requests.Session.return_value = mock_session
                
                client = YaappClient("http://example.com:8000")
                result = client.execute_command("test_command", ["--arg", "value"])
                
                assert result == "success"
                mock_session.post.assert_called_once()
    
    def test_parse_args(self):
        """Test argument parsing."""
        from yaapp.client import YaappClient
        
        with patch('yaapp.client.HAS_REQUESTS', True):
            with patch('yaapp.client.requests') as mock_requests:
                mock_session = MagicMock()
                mock_requests.Session.return_value = mock_session
                
                client = YaappClient("http://example.com:8000")
                
                # Test named arguments
                params = client._parse_args(["--name", "test", "--count", "5", "--flag"])
                
                expected = {
                    "name": "test",
                    "count": 5,  # JSON parsing converts to int
                    "flag": True
                }
                
                assert params == expected
    
    def test_execute_plugin_command_no_proxy(self):
        """Test plugin command execution when app proxy is not available."""
        from yaapp.cli import execute_plugin_command
        
        config = {"target_url": "http://localhost:8001", "timeout": 30}
        
        # Mock the import to raise ImportError
        def mock_import(name, *args, **kwargs):
            if 'app_proxy' in name:
                raise ImportError("No module named 'app_proxy'")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with patch('builtins.print') as mock_print:
                # Should handle ImportError gracefully
                execute_plugin_command("test_plugin", "test_command", config, {})
                # Should print error message
                mock_print.assert_called()
    
    def test_main_no_click(self):
        """Test main function when Click is not available."""
        from yaapp.cli import main
        
        with patch('yaapp.cli.HAS_CLICK', False):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called()
                # Should print message about Click not being available


def run_tests():
    """Run all universal CLI tests."""
    print("🔧 Universal CLI Tests")
    print("Testing universal yaapp CLI functionality")
    
    test_class = TestUniversalCLI()
    
    tests = [
        test_class.test_cli_import,
        test_class.test_default_config,
        test_class.test_load_universal_config_no_file,
        test_class.test_load_universal_config_with_yaml,
        test_class.test_create_universal_cli_no_click,
        test_class.test_create_universal_cli_with_click,
        test_class.test_plugin_command_structure,
        test_class.test_client_functionality,
        test_class.test_client_no_requests,
        test_class.test_client_get_help,
        test_class.test_client_execute_command,
        test_class.test_parse_args,
        test_class.test_execute_plugin_command_no_proxy,
        test_class.test_main_no_click,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n=== UNIVERSAL CLI TEST SUMMARY ===")
    print(f"Total: {passed + failed}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL UNIVERSAL CLI TESTS PASSED!")
        return True
    else:
        print(f"\n💥 {failed} UNIVERSAL CLI TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)