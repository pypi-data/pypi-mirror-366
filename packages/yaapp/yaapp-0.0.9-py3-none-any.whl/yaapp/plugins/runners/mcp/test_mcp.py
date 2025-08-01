"""
Test script for MCP runner.
"""

import sys
import os
import asyncio
import json

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from yaapp import Yaapp
from yaapp.plugins.runners.mcp.plugin import Mcp


def test_mcp_runner_basic():
    """Test basic MCP runner functionality."""
    print("Testing MCP Runner...")
    
    # Create yaapp instance
    app = Yaapp(auto_discover=False)
    
    # Add some test functions
    @app.expose
    def greet(name: str, formal: bool = False) -> str:
        """Greet someone with optional formality."""
        return f"{'Good day' if formal else 'Hello'}, {name}!"
    
    @app.expose
    class Calculator:
        """Simple calculator class."""
        
        def add(self, x: int, y: int) -> int:
            """Add two numbers."""
            return x + y
        
        def subtract(self, x: int, y: int) -> int:
            """Subtract two numbers."""
            return x - y
    
    # Create MCP runner
    mcp_runner = Mcp()
    
    # Test help
    print("Help text:")
    print(mcp_runner.help())
    print()
    
    # Test tool generation
    print("Testing tool generation...")
    mcp_runner.yaapp = app
    tools = mcp_runner._generate_mcp_tools_dict()
    
    print(f"Generated {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    print()
    
    # Test tool execution
    print("Testing tool execution...")
    
    async def test_execution():
        # Test simple function
        result = await mcp_runner._execute_tool("yaapp.greet", {"name": "World"})
        print(f"greet('World') = {result}")
        
        # Test class method
        result = await mcp_runner._execute_tool("yaapp.Calculator.add", {"x": 5, "y": 3})
        print(f"Calculator.add(5, 3) = {result}")
        
        # Test discovery tool
        result = await mcp_runner._execute_tool("yaapp.Calculator.__list_tools", {})
        print(f"Calculator.__list_tools() = {result}")
    
    asyncio.run(test_execution())
    
    print("✅ MCP Runner test completed successfully!")


def test_json_rpc_protocol():
    """Test JSON-RPC protocol handling."""
    print("Testing JSON-RPC protocol...")
    
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def echo(message: str) -> str:
        """Echo a message."""
        return f"Echo: {message}"
    
    mcp_runner = MCPRunner()
    mcp_runner.yaapp = app
    
    async def test_requests():
        # Test initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = await mcp_runner._handle_json_rpc_request(init_request)
        print("Initialize response:")
        print(json.dumps(response, indent=2))
        print()
        
        # Test tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await mcp_runner._handle_json_rpc_request(list_request)
        print("Tools list response:")
        print(json.dumps(response, indent=2))
        print()
        
        # Test tools/call request
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "yaapp.echo",
                "arguments": {"message": "Hello MCP!"}
            }
        }
        
        response = await mcp_runner._handle_json_rpc_request(call_request)
        print("Tool call response:")
        print(json.dumps(response, indent=2))
    
    asyncio.run(test_requests())
    
    print("✅ JSON-RPC protocol test completed successfully!")


if __name__ == "__main__":
    test_mcp_runner_basic()
    print()
    test_json_rpc_protocol()