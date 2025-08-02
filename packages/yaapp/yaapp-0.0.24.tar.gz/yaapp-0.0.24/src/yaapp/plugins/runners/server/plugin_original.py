"""
Server runner plugin for yaapp.
Provides FastAPI web server with auto-generated endpoints.
"""

import inspect
from typing import get_type_hints, Dict, Any
# Import will be done dynamically to avoid circular imports

from yaapp import yaapp


@yaapp.expose("server")
class Server:
    """FastAPI-based server runner with dual endpoint structure."""
    
    def __init__(self, config=None):
        """Initialize Server runner with optional configuration."""
        self.config = config or {}
    
    def help(self) -> str:
        """Return server runner-specific help text."""
        return """
🌐 SERVER RUNNER HELP:
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the server runner with the app instance."""
        # Extract server configuration
        host = kwargs.get('host', self.config.get('host', 'localhost'))
        port = kwargs.get('port', self.config.get('port', 8000))
        reload = kwargs.get('reload', self.config.get('reload', False))
        workers = kwargs.get('workers', self.config.get('workers', 1))
        
        self._start_server(host, port, reload, workers)
    
    def _start_server(self, host: str, port: int, reload: bool, workers: int):
        """Start FastAPI web server."""
        print(f"Starting web server on {host}:{port}")
        print(f"Available functions: {list(yaapp._registry.keys())}")

        if not yaapp._registry:
            print("No functions exposed. Use @app.expose to expose functions.")
            return

        try:
            import uvicorn
            from fastapi import FastAPI, HTTPException
            from fastapi.responses import JSONResponse
            from pydantic import BaseModel
        except ImportError:
            print("FastAPI, uvicorn, and pydantic required for web server. Install with: pip install fastapi uvicorn pydantic")
            return

        # Create FastAPI app
        fastapi_app = FastAPI(
            title="YApp API", 
            description="Auto-generated API from exposed functions with dual endpoint structure"
        )

        # Build command hierarchy for usual endpoints
        command_tree = self._build_command_tree()
        
        # Add usual endpoints (hierarchical POST)
        self._add_usual_endpoints(fastapi_app, command_tree)
        
        # Add RPC endpoints
        self._add_rpc_endpoints(fastapi_app)

        # Add streaming endpoints
        self._add_streaming_endpoints(fastapi_app, command_tree)

        # Start the server
        uvicorn.run(fastapi_app, host=host, port=port, reload=reload)

    def _build_command_tree(self) -> Dict[str, Any]:
        """Build hierarchical command tree from registry."""
        tree = {}
        
        for full_name, (obj, exposer) in yaapp._registry.items():
            parts = full_name.split('.')
            current = tree
            
            # Navigate/create nested structure
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # This is the final item
                    if inspect.isclass(obj):
                        # Handle class - create namespace with methods
                        current[part] = {
                            'type': 'namespace',
                            'children': self._get_class_methods(obj),
                            'class': obj
                        }
                    elif callable(obj):
                        # Handle function
                        current[part] = {
                            'type': 'function',
                            'func': obj,
                            'full_name': full_name
                        }
                else:
                    # This is a namespace
                    if part not in current:
                        current[part] = {'type': 'namespace', 'children': {}}
                    current = current[part]['children']
        
        return tree
    
    def _get_class_methods(self, cls) -> Dict[str, Any]:
        """Get methods from a class as a tree structure - inspect class without instantiation."""
        methods = {}
        
        for method_name in dir(cls):
            if not method_name.startswith('_'):
                method = getattr(cls, method_name)
                if callable(method) and not isinstance(method, type):
                    # Store the unbound method - we'll handle instantiation at execution time
                    methods[method_name] = {
                        'type': 'function',
                        'func': method,
                        'class': cls,  # Store class for later instantiation
                        'full_name': f"{cls.__name__}.{method_name}"
                    }
        
        return methods

    def _build_rpc_tree(self) -> Dict[str, Any]:
        """Build RPC tree structure showing commands and subcommands."""
        tree = {}
        
        for full_name, (obj, exposer) in yaapp._registry.items():
            parts = full_name.split('.')
            current = tree
            
            # Navigate/create nested structure
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # Final item
                    if inspect.isclass(obj):
                        # Class - create namespace with methods
                        current[part] = {
                            'type': 'class',
                            'description': getattr(obj, '__doc__', f"Class {obj.__name__}"),
                            'methods': self._get_class_methods_rpc(obj)
                        }
                    elif callable(obj):
                        # Function - include signature
                        current[part] = {
                            'type': 'function',
                            'signature': self._get_function_signature(obj),
                            'description': getattr(obj, '__doc__', f"Function {part}")
                        }
                else:
                    # Namespace
                    if part not in current:
                        current[part] = {'type': 'namespace', 'commands': {}}
                    current = current[part]['commands']
        
        return tree
    
    def _get_class_methods_rpc(self, cls) -> Dict[str, Any]:
        """Get class methods for RPC tree - inspect class without instantiation."""
        methods = {}
        
        for method_name in dir(cls):
            if not method_name.startswith('_'):
                method = getattr(cls, method_name)
                if callable(method) and not isinstance(method, type):
                    methods[method_name] = {
                        'type': 'function',
                        'signature': self._get_function_signature(method),
                        'description': getattr(method, '__doc__', f"Method {method_name}"),
                        'class': cls  # Store class for later instantiation
                    }
        
        return methods
    
    def _get_function_signature(self, func) -> Dict[str, str]:
        """Get function signature as name:type dictionary."""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        signature = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get parameter type
            param_type = type_hints.get(param_name, str)
            type_name = getattr(param_type, '__name__', 'Any')
            
            # Handle defaults
            if param.default != inspect.Parameter.empty:
                signature[param_name] = f"{type_name} = {param.default}"
            else:
                signature[param_name] = type_name
        
        return signature

    def _add_usual_endpoints(self, app, command_tree: Dict[str, Any], path_prefix: str = ""):
        """Add usual endpoints (hierarchical POST with _describe)."""
        try:
            from pydantic import BaseModel
        except ImportError:
            # This should not happen if we reach this point, but just in case
            print("Error: pydantic is required for FastAPI runner")
            return
        
        # Create dynamic model for JSON body
        class DynamicRequest(BaseModel):
            class Config:
                extra = "allow"
        
        # Add _describe endpoint for current level
        describe_path = f"{path_prefix}/_describe"
        
        def make_describe_endpoint(tree):
            def describe_endpoint():
                """Describe available commands at this level."""
                commands = []
                for name, item in tree.items():
                    if not name.startswith('_'):  # Skip internal items
                        commands.append(name)
                return {"commands": commands}
            return describe_endpoint
        
        app.get(describe_path)(make_describe_endpoint(command_tree))
        
        # Add endpoints for each item in current tree level
        for name, item in command_tree.items():
            current_path = f"{path_prefix}/{name}"
            
            if item['type'] == 'function':
                # Add POST endpoint for function execution
                func = item['func']
                full_name = item['full_name']
                
                def make_endpoint(func_obj, func_name):
                    async def endpoint(request: DynamicRequest):
                        try:
                            # Convert request to dict and call function using exposer system
                            kwargs = request.dict()
                            result = await self._call_function_async(func_name, kwargs)
                            return result
                        except Exception as e:
                            return {"error": str(e)}
                    return endpoint
                
                endpoint_func = make_endpoint(func, full_name)
                app.post(
                    current_path,
                    summary=f"Execute {full_name}",
                    description=getattr(func, '__doc__', f"Execute function {full_name}")
                )(endpoint_func)
                
            elif item['type'] == 'namespace':
                # Recursively add endpoints for namespace
                self._add_usual_endpoints(app, item['children'], current_path)

    def _add_rpc_endpoints(self, app):
        """Add RPC-style endpoints."""
        try:
            from pydantic import BaseModel
        except ImportError:
            # This should not happen if we reach this point, but just in case
            print("Error: pydantic is required for FastAPI runner")
            return
        from typing import Optional
        
        class RPCRequest(BaseModel):
            function: str
            args: Dict[str, Any] = {}
            arguments: Optional[Dict[str, Any]] = None
        
        @app.get("/_describe_rpc")
        def describe_rpc():
            """Describe all available functions for RPC interface in tree structure."""
            return {"functions": self._build_rpc_tree()}
        
        @app.post("/_rpc")
        async def rpc_endpoint(request: RPCRequest):
            """RPC-style function execution."""
            function_name = request.function
            # Support both 'args' and 'arguments' for compatibility
            arguments = request.args if request.args else (request.arguments or {})
            
            # Handle class method calls (e.g., "ClassName.method")
            if '.' in function_name and function_name not in yaapp._registry:
                parts = function_name.split('.')
                if len(parts) == 2:
                    class_name, method_name = parts
                    if class_name in yaapp._registry:
                        cls, exposer = yaapp._registry[class_name]
                        if inspect.isclass(cls):
                            try:
                                # Use the exposer to get cached instance (async-compatible)
                                result = await exposer.run_async(cls)
                                if result.is_ok():
                                    instance = result.unwrap()
                                    if hasattr(instance, method_name):
                                        method = getattr(instance, method_name)
                                        if callable(method):
                                            # Call method through temporary registry to get proper execution
                                            result = await self._call_function_async_method(method, arguments)
                                            return result
                                else:
                                    return {"error": f"Failed to instantiate {class_name}: {result.error_message}"}
                            except Exception as e:
                                return {"error": f"Error calling {function_name}: {str(e)}"}
                
                return {"error": f"Function '{function_name}' not found"}
            
            if function_name not in yaapp._registry:
                return {"error": f"Function '{function_name}' not found"}
            
            try:
                result = await self._call_function_async(function_name, arguments)
                return result
            except Exception as e:
                return {"error": str(e)}

    async def _call_function_async(self, function_name: str, kwargs: Dict[str, Any]):
        """Call function using exposer system with proper async execution."""
        if function_name not in yaapp._registry:
            return {"error": f"Function '{function_name}' not found in registry"}
        
        func, exposer = yaapp._registry[function_name]
        
        try:
            # Use exposer to execute function with proper async handling
            result = await exposer.run_async(func, **kwargs)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                # It's a Result object
                if result.is_ok():
                    return result.unwrap()
                else:
                    return {"error": f"Function execution failed: {result.error_message}"}
            else:
                return result
        except Exception as e:
            return {"error": f"Execution error in {function_name}: {str(e)}"}
    
    async def _call_function_async_method(self, method, kwargs: Dict[str, Any]):
        """Call a method using a temporary function exposer for proper async execution."""
        from yaapp.exposers import FunctionExposer
        
        try:
            # Create temporary exposer for the method
            temp_exposer = FunctionExposer()
            
            # Use exposer to execute method with proper async handling
            result = await temp_exposer.run_async(method, **kwargs)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                # It's a Result object
                if result.is_ok():
                    return result.unwrap()
                else:
                    return {"error": f"Method execution failed: {result.error_message}"}
            else:
                return result
        except Exception as e:
            return {"error": f"Method execution error: {str(e)}"}
    
    def _add_streaming_endpoints(self, app, command_tree: Dict[str, Any], path_prefix: str = ""):
        """Add streaming endpoints for generator functions."""
        try:
            from fastapi.responses import StreamingResponse
        except ImportError:
            # StreamingResponse not available, skip streaming endpoints
            return

        # Import streaming utilities
        try:
            from yaapp.streaming import StreamDetector, StreamExecutor
        except ImportError:
            print("Warning: Streaming utilities not available. Install required dependencies.")
            return

        # Add streaming endpoints for each streamable item
        for name, item in command_tree.items():
            current_path = f"{path_prefix}/{name}"
            
            if item['type'] == 'function':
                func = item['func']
                full_name = item['full_name']
                
                # Check if function should be exposed as stream
                if StreamDetector.should_stream(func):
                    stream_path = f"{current_path}/stream"
                    
                    def make_streaming_endpoint(func_obj, func_name):
                        from pydantic import BaseModel
                        
                        class DynamicRequest(BaseModel):
                            class Config:
                                extra = "allow"
                        
                        async def streaming_endpoint(request: DynamicRequest):
                            """Stream function output as SSE."""
                            try:
                                # Get function from registry
                                if func_name not in yaapp._registry:
                                    async def error_stream():
                                        yield f"event: error\\ndata: Function '{func_name}' not found\\n\\n"
                                    return StreamingResponse(
                                        error_stream(),
                                        media_type="text/event-stream"
                                    )
                                
                                func, exposer = yaapp._registry[func_name]
                                
                                # Get parameters from JSON body
                                kwargs = request.dict()
                                
                                # Execute streaming function using exposer system
                                return StreamingResponse(
                                    self._call_streaming_function_async(func_name, kwargs),
                                    media_type="text/event-stream",
                                    headers={
                                        "Cache-Control": "no-cache",
                                        "Connection": "keep-alive",
                                        "Access-Control-Allow-Origin": "*",
                                        "Access-Control-Allow-Headers": "Cache-Control"
                                    }
                                )
                            except Exception as e:
                                async def error_stream():
                                    yield f"event: error\\ndata: Streaming error: {str(e)}\\n\\n"
                                return StreamingResponse(
                                    error_stream(),
                                    media_type="text/event-stream"
                                )
                        return streaming_endpoint
                    
                    endpoint_func = make_streaming_endpoint(func, full_name)
                    app.post(
                        stream_path,
                        summary=f"Stream {full_name}",
                        description=f"Stream output from {full_name} as Server-Sent Events"
                    )(endpoint_func)
                    
            elif item['type'] == 'namespace':
                # Recursively add streaming endpoints for namespace
                self._add_streaming_endpoints(app, item['children'], current_path)

    async def _call_streaming_function_async(self, function_name: str, kwargs: Dict[str, Any]):
        """Call streaming function using exposer system and yield SSE formatted output."""
        from yaapp.streaming import StreamFormatter
        
        if function_name not in yaapp._registry:
            yield f"event: error\\ndata: Function '{function_name}' not found\\n\\n"
            return
        
        func, exposer = yaapp._registry[function_name]
        formatter = StreamFormatter()
        
        try:
            # Use exposer to execute function with proper async handling
            result = await exposer.run_async(func, **kwargs)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                # It's a Result object
                if result.is_ok():
                    stream_result = result.unwrap()
                    # Check if result is an async generator
                    if hasattr(stream_result, '__aiter__'):
                        async for item in stream_result:
                            yield formatter.format_data(item, "sse")
                    else:
                        # Single result
                        yield formatter.format_data(stream_result, "sse")
                else:
                    yield f"event: error\\ndata: Function execution failed: {result.error_message}\\n\\n"
            else:
                # Direct result - check if it's an async generator
                if hasattr(result, '__aiter__'):
                    async for item in result:
                        yield formatter.format_data(item, "sse")
                else:
                    # Single result
                    yield formatter.format_data(result, "sse")
                    
        except Exception as e:
            yield f"event: error\\ndata: Execution error in {function_name}: {str(e)}\\n\\n"