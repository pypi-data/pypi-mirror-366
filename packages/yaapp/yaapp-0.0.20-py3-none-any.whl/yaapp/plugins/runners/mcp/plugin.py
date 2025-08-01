"""
MCP runner plugin for yaapp.
Exposes yaapp functions as MCP (Model Context Protocol) tools.
"""

import asyncio
import inspect
import json
import sys
import os
from typing import Dict, Any, List, Optional, get_type_hints
import logging

# Import yaapp for the decorator
from yaapp import yaapp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@yaapp.expose("mcp")
class Mcp:
    """MCP server runner that exposes yaapp functions as MCP tools."""
    
    def __init__(self, config=None):
        """Initialize MCP runner with optional configuration."""
        self.config = config or {}
        self.server_name = self.config.get('server_name', 'yaapp MCP Server')
        self.server_version = self.config.get('server_version', '1.0.0')
        self.tool_prefix = self.config.get('tool_prefix', 'yaapp')
        self.max_tools_per_namespace = self.config.get('max_tools_per_namespace', 50)
        self.enable_discovery_tools = self.config.get('enable_discovery_tools', True)
        
        # Check for environment variables
        self.server_name = os.getenv('YAAPP_MCP_SERVER_NAME', self.server_name)
        self.server_version = os.getenv('YAAPP_MCP_SERVER_VERSION', self.server_version)
        self.debug = os.getenv('YAAPP_MCP_DEBUG', 'false').lower() == 'true'
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
    
    def help(self) -> str:
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
    
    def run(self, app_instance, **kwargs):
        """Execute the MCP runner with the app instance."""
        logger.info(f"Starting {self.server_name} v{self.server_version}")
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
                self._run_with_mcp_sdk()
            except ImportError:
                logger.info("MCP SDK not found, using built-in JSON-RPC implementation")
                self._run_builtin_server()
                
        except KeyboardInterrupt:
            logger.info("MCP server stopped by user")
        except Exception as e:
            logger.error(f"MCP server error: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
    
    def _run_with_mcp_sdk(self):
        """Run MCP server using official MCP SDK."""
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        
        # Create MCP server
        server = Server(self.server_name)
        
        # Generate and register tools
        tools = self._generate_mcp_tools()
        
        @server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available MCP tools."""
            return tools
        
        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute an MCP tool."""
            try:
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                error_msg = f"Error executing tool '{name}': {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]
        
        # Run the server
        asyncio.run(stdio_server(server))
    
    def _run_builtin_server(self):
        """Run MCP server using built-in JSON-RPC implementation."""
        logger.info("Starting built-in MCP JSON-RPC server")
        
        # Run the JSON-RPC server loop
        asyncio.run(self._json_rpc_server_loop())
    
    async def _json_rpc_server_loop(self):
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
                response = await self._handle_json_rpc_request(request)
                
                if response:
                    response_json = json.dumps(response)
                    logger.debug(f"Sending: {response_json}")
                    print(response_json, flush=True)
                    
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Server loop error: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
    
    async def _handle_json_rpc_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a JSON-RPC request according to MCP protocol."""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        try:
            if method == 'initialize':
                return await self._handle_initialize(request_id, params)
            elif method == 'tools/list':
                return await self._handle_tools_list(request_id, params)
            elif method == 'tools/call':
                return await self._handle_tools_call(request_id, params)
            elif method == 'notifications/initialized':
                # Notification - no response needed
                logger.debug("Client initialized")
                return None
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
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
                    "name": self.server_name,
                    "version": self.server_version
                }
            }
        }
    
    async def _handle_tools_list(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/list request."""
        tools = self._generate_mcp_tools_dict()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/call request."""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if not tool_name:
            return self._error_response(request_id, -32602, "Missing tool name")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
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
            return self._error_response(request_id, -32603, error_msg)
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Generate JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    def _generate_mcp_tools(self) -> List:
        """Generate MCP tools using official SDK types."""
        from mcp.types import Tool
        
        tools = []
        tool_dicts = self._generate_mcp_tools_dict()
        
        for tool_dict in tool_dicts:
            tool = Tool(
                name=tool_dict['name'],
                description=tool_dict['description'],
                inputSchema=tool_dict['inputSchema']
            )
            tools.append(tool)
        
        return tools
    
    def _generate_mcp_tools_dict(self) -> List[Dict[str, Any]]:
        """Generate MCP tools as dictionaries."""
        tools = []
        
        # Group registry items by namespace/class
        namespaces = self._group_registry_items()
        
        if self.enable_discovery_tools:
            # Add namespace discovery tools
            for namespace_name in namespaces.keys():
                if namespace_name != '__root__':
                    discovery_tool = {
                        "name": f"{self.tool_prefix}.{namespace_name}.__list_tools",
                        "description": f"List available tools in {namespace_name} namespace",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                    tools.append(discovery_tool)
        
        # Add root-level functions directly
        if '__root__' in namespaces:
            for item_name, (obj, exposer) in namespaces['__root__'].items():
                if callable(obj) and not inspect.isclass(obj):
                    tool = self._create_tool_schema(f"{self.tool_prefix}.{item_name}", obj)
                    if tool:
                        tools.append(tool)
        
        # Limit tools to prevent overwhelming clients
        if len(tools) > self.max_tools_per_namespace:
            logger.warning(f"Too many tools ({len(tools)}), limiting to {self.max_tools_per_namespace}")
            tools = tools[:self.max_tools_per_namespace]
        
        return tools
    
    def _group_registry_items(self) -> Dict[str, Dict[str, Any]]:
        """Group registry items by namespace or class."""
        namespaces = {}
        
        for full_name, (obj, exposer) in yaapp._registry.items():
            if '.' in full_name:
                # Namespaced item
                parts = full_name.split('.')
                namespace = '.'.join(parts[:-1])
                item_name = parts[-1]
            else:
                # Root level item
                namespace = '__root__'
                item_name = full_name
            
            if namespace not in namespaces:
                namespaces[namespace] = {}
            
            namespaces[namespace][item_name] = (obj, exposer)
        
        return namespaces
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with given arguments."""
        logger.debug(f"Executing tool: {tool_name} with args: {arguments}")
        
        # Handle discovery tools
        if tool_name.endswith('.__list_tools'):
            return await self._handle_discovery_tool(tool_name)
        
        # Remove tool prefix
        if tool_name.startswith(f"{self.tool_prefix}."):
            tool_name = tool_name[len(f"{self.tool_prefix}."):]
        
        # Handle class methods
        if '.' in tool_name:
            parts = tool_name.split('.')
            if len(parts) >= 2:
                class_or_namespace = '.'.join(parts[:-1])
                method_name = parts[-1]
                
                # Try to find class in registry
                if class_or_namespace in yaapp._registry:
                    cls, exposer = yaapp._registry[class_or_namespace]
                    if inspect.isclass(cls):
                        # Execute class method
                        return await self._execute_class_method(cls, exposer, method_name, arguments)
                
                # Try full path in registry
                if tool_name in yaapp._registry:
                    func, exposer = yaapp._registry[tool_name]
                    return await self._execute_function(func, exposer, arguments)
        
        # Try direct lookup in registry
        if tool_name in yaapp._registry:
            func, exposer = yaapp._registry[tool_name]
            return await self._execute_function(func, exposer, arguments)
        
        raise ValueError(f"Tool not found: {tool_name}")
    
    async def _handle_discovery_tool(self, tool_name: str) -> str:
        """Handle namespace discovery tool."""
        # Extract namespace from tool name
        if tool_name.startswith(f"{self.tool_prefix}."):
            tool_name = tool_name[len(f"{self.tool_prefix}."):]
        
        namespace = tool_name.replace('.__list_tools', '')
        
        # Get items in namespace
        namespaces = self._group_registry_items()
        
        if namespace not in namespaces:
            return f"Namespace '{namespace}' not found"
        
        items = namespaces[namespace]
        tool_list = []
        
        for item_name, (obj, exposer) in items.items():
            if inspect.isclass(obj):
                # List class methods
                methods = []
                for method_name in dir(obj):
                    if not method_name.startswith('_'):
                        method = getattr(obj, method_name)
                        if callable(method):
                            methods.append(method_name)
                
                if methods:
                    tool_list.append(f"**{item_name}** (class): {', '.join(methods)}")
            elif callable(obj):
                # Function
                doc = getattr(obj, '__doc__', '') or 'No description'
                tool_list.append(f"**{item_name}**: {doc.split('.')[0]}")
        
        if not tool_list:
            return f"No tools found in namespace '{namespace}'"
        
        result = f"✅ **{namespace} Tools Available** ({len(tool_list)} tools)\n\n"
        result += '\n'.join(f"• {tool}" for tool in tool_list)
        result += f"\n\n**Next Step:** Call tools directly using {self.tool_prefix}.{namespace}.tool_name"
        
        return result
    
    async def _execute_function(self, func, exposer, arguments: Dict[str, Any]) -> Any:
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
    
    async def _execute_class_method(self, cls, exposer, method_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a class method using the exposer system."""
        try:
            # Use exposer to get instance
            result = await exposer.run_async(cls)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                if result.is_ok():
                    instance = result.unwrap()
                else:
                    raise Exception(f"Failed to instantiate class: {result.error_message}")
            else:
                instance = result
            
            # Get method from instance
            if not hasattr(instance, method_name):
                raise Exception(f"Method '{method_name}' not found in class {cls.__name__}")
            
            method = getattr(instance, method_name)
            if not callable(method):
                raise Exception(f"'{method_name}' is not callable")
            
            # Execute method using function exposer
            from yaapp.exposers import FunctionExposer
            temp_exposer = FunctionExposer()
            
            result = await temp_exposer.run_async(method, **arguments)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                if result.is_ok():
                    return result.unwrap()
                else:
                    raise Exception(f"Method execution failed: {result.error_message}")
            else:
                return result
                
        except Exception as e:
            raise Exception(f"Class method execution error: {str(e)}")
    
    def _create_tool_schema(self, tool_name: str, func) -> Optional[Dict[str, Any]]:
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
                schema_type = self._python_type_to_json_schema(param_type)
                
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
    
    def _python_type_to_json_schema(self, python_type) -> Dict[str, Any]:
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
                item_schema = self._python_type_to_json_schema(args[0])
                return {"type": "array", "items": item_schema}
            return {"type": "array"}
        
        elif origin is dict:
            return {"type": "object"}
        
        elif origin is Union:  # Optional[T] is Union[T, None]
            # Find non-None type
            non_none_types = [arg for arg in args if arg != type(None)]
            if non_none_types:
                return self._python_type_to_json_schema(non_none_types[0])
        
        # Default to string for unknown types
        return {"type": "string"}


# Handle Union import for older Python versions
try:
    from typing import Union
except ImportError:
    Union = None