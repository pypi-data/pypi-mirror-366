"""
MCP runner for yaapp.
Exposes yaapp functions as MCP (Model Context Protocol) tools.
"""

import asyncio
import inspect
import json
import sys
import os
from typing import Dict, Any, List, Optional, get_type_hints
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def help() -> str:
    """Return MCP runner-specific help text."""
    return """
🔗 MCP RUNNER HELP:
  Exposes yaapp functions as MCP (Model Context Protocol) tools
  
  MCP enables AI applications like Claude Desktop, VS Code, and Cursor
  to discover and execute yaapp functions through a standardized protocol.
  
  Configuration:
    --host TEXT     Server host (not used for STDIO transport)
    --port INTEGER  Server port (not used for STDIO transport)
    
  Environment Variables:
    YAAPP_MCP_SERVER_NAME    Custom server name
    YAAPP_MCP_SERVER_VERSION Custom server version  
    YAAPP_MCP_DEBUG         Enable debug logging (true/false)
    
  Usage:
    python app.py --mcp
    
  MCP Client Configuration (Claude Desktop):
    {
        "mcpServers": {
            "yaapp": {
                "command": "python",
                "args": ["app.py", "--mcp"],
                "cwd": "/path/to/your/yaapp/project"
            }
        }
    }
    """


def run(app_instance, **kwargs):
    """Execute the MCP runner with the app instance."""
    config = kwargs.get('config', {})
    server_name = config.get('server_name', 'yaapp MCP Server')
    server_version = config.get('server_version', '1.0.0')
    tool_prefix = config.get('tool_prefix', 'yaapp')
    max_tools_per_namespace = config.get('max_tools_per_namespace', 50)
    enable_discovery_tools = config.get('enable_discovery_tools', True)
    
    # Check for environment variables
    server_name = os.getenv('YAAPP_MCP_SERVER_NAME', server_name)
    server_version = os.getenv('YAAPP_MCP_SERVER_VERSION', server_version)
    debug = os.getenv('YAAPP_MCP_DEBUG', 'false').lower() == 'true'
    
    if debug:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Starting {server_name} v{server_version}")
    logger.info(f"Available functions: {list(app_instance._registry.keys())}")
    
    if not app_instance._registry:
        logger.warning("No functions exposed. Use @app.expose to expose functions.")
        return
    
    try:
        # Check if MCP SDK is available
        try:
            from mcp.server import Server
            from mcp.server.stdio import stdio_server
            from mcp.types import Tool, TextContent
            logger.debug("MCP SDK found, using official implementation")
            _run_with_mcp_sdk(app_instance, server_name, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
        except ImportError:
            logger.info("MCP SDK not found, using built-in JSON-RPC implementation")
            _run_builtin_server(app_instance, server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools, debug)
            
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        if debug:
            import traceback
            traceback.print_exc()


def _run_with_mcp_sdk(app_instance, server_name, tool_prefix, max_tools_per_namespace, enable_discovery_tools):
    """Run MCP server using official MCP SDK."""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    
    # Create MCP server
    server = Server(server_name)
    
    # Generate and register tools
    tools = _generate_mcp_tools(app_instance, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available MCP tools."""
        return tools
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute an MCP tool."""
        try:
            result = await _execute_tool(app_instance, name, arguments, tool_prefix)
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            error_msg = f"Error executing tool '{name}': {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
    
    # Run the server
    asyncio.run(stdio_server(server))


def _run_builtin_server(app_instance, server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools, debug):
    """Run MCP server using built-in JSON-RPC implementation."""
    logger.info("Starting built-in MCP JSON-RPC server")
    
    # Run the JSON-RPC server loop
    asyncio.run(_json_rpc_server_loop(app_instance, server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools, debug))


async def _json_rpc_server_loop(app_instance, server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools, debug):
    """Main JSON-RPC server loop for MCP protocol."""
    while True:
        try:
            # Read JSON-RPC message from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            logger.debug(f"Received: {line}")
            
            # Parse JSON-RPC request
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                continue
            
            # Handle request
            response = await _handle_json_rpc_request(app_instance, request, server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
            
            if response:
                response_json = json.dumps(response)
                logger.debug(f"Sending: {response_json}")
                print(response_json, flush=True)
                
        except EOFError:
            break
        except Exception as e:
            logger.error(f"Server loop error: {e}")
            if debug:
                import traceback
                traceback.print_exc()


async def _handle_json_rpc_request(app_instance, request: Dict[str, Any], server_name, server_version, tool_prefix, max_tools_per_namespace, enable_discovery_tools) -> Optional[Dict[str, Any]]:
    """Handle a JSON-RPC request according to MCP protocol."""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'initialize':
            return await _handle_initialize(request_id, params, server_name, server_version)
        elif method == 'tools/list':
            return await _handle_tools_list(app_instance, request_id, params, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
        elif method == 'tools/call':
            return await _handle_tools_call(app_instance, request_id, params, tool_prefix)
        elif method == 'notifications/initialized':
            # Notification - no response needed
            logger.debug("Client initialized")
            return None
        else:
            return _error_response(request_id, -32601, f"Method not found: {method}")
            
    except Exception as e:
        logger.error(f"Error handling {method}: {e}")
        return _error_response(request_id, -32603, f"Internal error: {str(e)}")


async def _handle_initialize(request_id: Any, params: Dict[str, Any], server_name, server_version) -> Dict[str, Any]:
    """Handle MCP initialize request."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "logging": {}
            },
            "serverInfo": {
                "name": server_name,
                "version": server_version
            }
        }
    }


async def _handle_tools_list(app_instance, request_id: Any, params: Dict[str, Any], tool_prefix, max_tools_per_namespace, enable_discovery_tools) -> Dict[str, Any]:
    """Handle MCP tools/list request."""
    tools = _generate_mcp_tools_dict(app_instance, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }


async def _handle_tools_call(app_instance, request_id: Any, params: Dict[str, Any], tool_prefix) -> Dict[str, Any]:
    """Handle MCP tools/call request."""
    tool_name = params.get('name')
    arguments = params.get('arguments', {})
    
    if not tool_name:
        return _error_response(request_id, -32602, "Missing tool name")
    
    try:
        result = await _execute_tool(app_instance, tool_name, arguments, tool_prefix)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
        }
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {str(e)}"
        logger.error(error_msg)
        return _error_response(request_id, -32603, error_msg)


def _error_response(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    """Generate JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }


def _generate_mcp_tools(app_instance, tool_prefix, max_tools_per_namespace, enable_discovery_tools) -> List:
    """Generate MCP tools using official SDK types."""
    from mcp.types import Tool
    
    tools = []
    tool_dicts = _generate_mcp_tools_dict(app_instance, tool_prefix, max_tools_per_namespace, enable_discovery_tools)
    
    for tool_dict in tool_dicts:
        tool = Tool(
            name=tool_dict['name'],
            description=tool_dict['description'],
            inputSchema=tool_dict['inputSchema']
        )
        tools.append(tool)
    
    return tools


def _generate_mcp_tools_dict(app_instance, tool_prefix, max_tools_per_namespace, enable_discovery_tools) -> List[Dict[str, Any]]:
    """Generate MCP tools as dictionaries."""
    tools = []
    
    # Add root-level functions directly
    for item_name, (obj, exposer) in app_instance._registry.items():
        if callable(obj) and not inspect.isclass(obj):
            tool = _create_tool_schema(f"{tool_prefix}.{item_name}", obj)
            if tool:
                tools.append(tool)
    
    # Limit tools to prevent overwhelming clients
    if len(tools) > max_tools_per_namespace:
        logger.warning(f"Too many tools ({len(tools)}), limiting to {max_tools_per_namespace}")
        tools = tools[:max_tools_per_namespace]
    
    return tools


async def _execute_tool(app_instance, tool_name: str, arguments: Dict[str, Any], tool_prefix) -> Any:
    """Execute a tool by name with given arguments."""
    logger.debug(f"Executing tool: {tool_name} with args: {arguments}")
    
    # Remove tool prefix
    if tool_name.startswith(f"{tool_prefix}."):
        tool_name = tool_name[len(f"{tool_prefix}."):]
    
    # Try direct lookup in registry
    if tool_name in app_instance._registry:
        func, exposer = app_instance._registry[tool_name]
        return await _execute_function(func, exposer, arguments)
    
    raise ValueError(f"Tool not found: {tool_name}")


async def _execute_function(func, exposer, arguments: Dict[str, Any]) -> Any:
    """Execute a function using its exposer."""
    try:
        # Use exposer to execute function with proper async handling
        result = await exposer.run_async(func, **arguments)
        
        if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
            # It's a Result object
            if result.is_ok():
                return result.unwrap()
            else:
                raise Exception(f"Function execution failed: {result.error_message}")
        else:
            return result
    except Exception as e:
        raise Exception(f"Execution error: {str(e)}")


def _create_tool_schema(tool_name: str, func) -> Optional[Dict[str, Any]]:
    """Create MCP tool schema from function."""
    try:
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        
        # Build input schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get parameter type
            param_type = type_hints.get(param_name, str)
            schema_type = _python_type_to_json_schema(param_type)
            
            properties[param_name] = schema_type
            
            # Check if required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Get description from docstring
        description = getattr(func, '__doc__', '') or f"Execute {tool_name}"
        description = description.strip().split('\n')[0]  # First line only
        
        return {
            "name": tool_name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating schema for {tool_name}: {e}")
        return None


def _python_type_to_json_schema(python_type) -> Dict[str, Any]:
    """Convert Python type to JSON Schema."""
    # Handle basic types
    if python_type == str:
        return {"type": "string"}
    elif python_type == int:
        return {"type": "integer"}
    elif python_type == float:
        return {"type": "number"}
    elif python_type == bool:
        return {"type": "boolean"}
    elif python_type == list:
        return {"type": "array"}
    elif python_type == dict:
        return {"type": "object"}
    
    # Handle typing module types
    origin = getattr(python_type, '__origin__', None)
    args = getattr(python_type, '__args__', ())
    
    if origin is list:
        if args:
            item_schema = _python_type_to_json_schema(args[0])
            return {"type": "array", "items": item_schema}
        return {"type": "array"}
    
    elif origin is dict:
        return {"type": "object"}
    
    # Handle Union import for older Python versions
    try:
        from typing import Union
        if origin is Union:  # Optional[T] is Union[T, None]
            # Find non-None type
            non_none_types = [arg for arg in args if arg != type(None)]
            if non_none_types:
                return _python_type_to_json_schema(non_none_types[0])
    except ImportError:
        pass
    
    # Default to string for unknown types
    return {"type": "string"}