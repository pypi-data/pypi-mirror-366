"""
Streaming-enhanced FastAPI runner for yaapp.

Extends the standard FastAPI runner with Server-Sent Events (SSE) support
and automatic streaming endpoint generation.
"""

import inspect
from typing import Dict, Any, List
from .fastapi_runner import FastAPIRunner
from ..streaming import StreamDetector, StreamExecutor


class StreamingFastAPIRunner(FastAPIRunner):
    """FastAPI runner with streaming/SSE capabilities."""
    
    def run(self, host: str = "localhost", port: int = 8000, reload: bool = False):
        """Start FastAPI web server with streaming support."""
        print(f"Starting web server with streaming support on {host}:{port}")
        print(f"Available functions: {list(self.core._registry.keys())}")

        if not self.core._registry:
            print("No functions exposed. Use @app.expose to expose functions.")
            return

        try:
            import uvicorn
            from fastapi import FastAPI, HTTPException
            from fastapi.responses import JSONResponse, StreamingResponse
            from pydantic import BaseModel
        except ImportError:
            print("FastAPI, uvicorn, and pydantic required for web server. Install with: pip install fastapi uvicorn pydantic")
            return

        # Create FastAPI app
        fastapi_app = FastAPI(
            title="YApp Streaming API", 
            description="Auto-generated API from exposed functions with streaming support"
        )

        # Build command hierarchy for usual endpoints
        command_tree = self._build_command_tree()
        
        # Add usual endpoints (hierarchical POST)
        self._add_usual_endpoints(fastapi_app, command_tree)
        
        # Add streaming endpoints (hierarchical GET with SSE)
        self._add_streaming_endpoints(fastapi_app, command_tree)
        
        # Add RPC endpoints
        self._add_rpc_endpoints(fastapi_app)
        
        # Add streaming RPC endpoints
        self._add_streaming_rpc_endpoints(fastapi_app)
        
        # Add streaming info endpoint
        self._add_streaming_info_endpoint(fastapi_app)

        # Start the server
        uvicorn.run(fastapi_app, host=host, port=port, reload=reload)

    def _add_streaming_endpoints(self, app, command_tree: Dict[str, Any], path_prefix: str = ""):
        """Add streaming endpoints (hierarchical GET with SSE)."""
        try:
            from fastapi.responses import StreamingResponse
            from pydantic import BaseModel
        except ImportError:
            print("Error: FastAPI is required for streaming runner")
            return
        
        # Add endpoints for each streamable item in current tree level
        for name, item in command_tree.items():
            current_path = f"{path_prefix}/{name}"
            
            if item['type'] == 'function':
                func = item['func']
                full_name = item['full_name']
                
                # Check if function should be exposed as stream
                if StreamDetector.should_stream(func):
                    stream_path = f"{current_path}/stream"
                    
                    def make_streaming_endpoint(func_obj, func_name):
                        async def streaming_endpoint():
                            """Stream function output as SSE."""
                            try:
                                # Get function from registry
                                if func_name not in self.core._registry:
                                    return StreamingResponse(
                                        self._error_stream(f"Function '{func_name}' not found"),
                                        media_type="text/event-stream"
                                    )
                                
                                func, exposer = self.core._registry[func_name]
                                
                                # Execute streaming function
                                return StreamingResponse(
                                    StreamExecutor.execute_stream(func, {}),
                                    media_type="text/event-stream",
                                    headers={
                                        "Cache-Control": "no-cache",
                                        "Connection": "keep-alive",
                                        "Access-Control-Allow-Origin": "*",
                                        "Access-Control-Allow-Headers": "Cache-Control"
                                    }
                                )
                            except Exception as e:
                                return StreamingResponse(
                                    self._error_stream(f"Streaming error: {str(e)}"),
                                    media_type="text/event-stream"
                                )
                        return streaming_endpoint
                    
                    endpoint_func = make_streaming_endpoint(func, full_name)
                    app.get(
                        stream_path,
                        summary=f"Stream {full_name}",
                        description=f"Stream output from {full_name} as Server-Sent Events"
                    )(endpoint_func)
                    
                    # Also add POST version that accepts parameters
                    def make_streaming_post_endpoint(func_obj, func_name):
                        async def streaming_post_endpoint(request: dict):
                            """Stream function output as SSE with parameters."""
                            try:
                                # Get function from registry
                                if func_name not in self.core._registry:
                                    return StreamingResponse(
                                        self._error_stream(f"Function '{func_name}' not found"),
                                        media_type="text/event-stream"
                                    )
                                
                                func, exposer = self.core._registry[func_name]
                                
                                # Execute streaming function with parameters
                                return StreamingResponse(
                                    StreamExecutor.execute_stream(func, request),
                                    media_type="text/event-stream",
                                    headers={
                                        "Cache-Control": "no-cache",
                                        "Connection": "keep-alive",
                                        "Access-Control-Allow-Origin": "*",
                                        "Access-Control-Allow-Headers": "Cache-Control"
                                    }
                                )
                            except Exception as e:
                                return StreamingResponse(
                                    self._error_stream(f"Streaming error: {str(e)}"),
                                    media_type="text/event-stream"
                                )
                        return streaming_post_endpoint
                    
                    post_endpoint_func = make_streaming_post_endpoint(func, full_name)
                    app.post(
                        stream_path,
                        summary=f"Stream {full_name} with parameters",
                        description=f"Stream output from {full_name} as Server-Sent Events with parameters"
                    )(post_endpoint_func)
                    
            elif item['type'] == 'namespace':
                # Recursively add streaming endpoints for namespace
                self._add_streaming_endpoints(app, item['children'], current_path)

    def _add_streaming_rpc_endpoints(self, app):
        """Add streaming RPC-style endpoints."""
        try:
            from fastapi.responses import StreamingResponse
            from pydantic import BaseModel
        except ImportError:
            print("Error: FastAPI is required for streaming runner")
            return
        from typing import Optional
        
        class StreamingRPCRequest(BaseModel):
            function: str
            args: Dict[str, Any] = {}
            arguments: Optional[Dict[str, Any]] = None
        
        @app.get("/_stream_describe")
        def describe_streaming():
            """Describe all streamable functions."""
            streamable_functions = {}
            
            for full_name, (obj, exposer) in self.core._registry.items():
                if callable(obj) and StreamDetector.should_stream(obj):
                    streamable_functions[full_name] = {
                        'type': 'streamable_function',
                        'signature': self._get_function_signature(obj),
                        'description': getattr(obj, '__doc__', f"Streamable function {full_name}"),
                        'stream_format': StreamDetector.get_stream_format(obj),
                        'endpoints': {
                            'stream_get': f"/{full_name.replace('.', '/')}/stream",
                            'stream_post': f"/{full_name.replace('.', '/')}/stream",
                            'stream_rpc': f"/_stream_rpc"
                        }
                    }
            
            return {"streamable_functions": streamable_functions}

        @app.post("/_stream_rpc")
        async def streaming_rpc_endpoint(request: StreamingRPCRequest):
            """Streaming RPC-style function execution."""
            function_name = request.function
            # Support both 'args' and 'arguments' for compatibility
            arguments = request.args if request.args else (request.arguments or {})
            
            # Check if function exists and is streamable
            if function_name not in self.core._registry:
                return StreamingResponse(
                    self._error_stream(f"Function '{function_name}' not found"),
                    media_type="text/event-stream"
                )
            
            func, exposer = self.core._registry[function_name]
            
            if not StreamDetector.should_stream(func):
                return StreamingResponse(
                    self._error_stream(f"Function '{function_name}' is not streamable"),
                    media_type="text/event-stream"
                )
            
            try:
                return StreamingResponse(
                    StreamExecutor.execute_stream(func, arguments),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Cache-Control"
                    }
                )
            except Exception as e:
                return StreamingResponse(
                    self._error_stream(f"Streaming execution error: {str(e)}"),
                    media_type="text/event-stream"
                )

    def _add_streaming_info_endpoint(self, app):
        """Add endpoint that provides streaming capabilities info."""
        @app.get("/_streaming_info")
        def streaming_info():
            """Get information about streaming capabilities."""
            streamable_count = 0
            regular_count = 0
            streaming_functions = []
            
            for full_name, (obj, exposer) in self.core._registry.items():
                if callable(obj):
                    if StreamDetector.should_stream(obj):
                        streamable_count += 1
                        streaming_functions.append({
                            'name': full_name,
                            'format': StreamDetector.get_stream_format(obj),
                            'detection_reason': self._get_detection_reason(obj),
                            'endpoints': {
                                'get': f"/{full_name.replace('.', '/')}/stream",
                                'post': f"/{full_name.replace('.', '/')}/stream",
                                'rpc': "/_stream_rpc"
                            }
                        })
                    else:
                        regular_count += 1
            
            return {
                'streaming_enabled': True,
                'total_functions': streamable_count + regular_count,
                'streamable_functions': streamable_count,
                'regular_functions': regular_count,
                'streaming_functions': streaming_functions,
                'supported_formats': ['sse', 'json-lines', 'raw'],
                'detection_criteria': [
                    'Functions with @stream decorator',
                    'Generator/AsyncGenerator functions',
                    'Functions with streaming return type annotations',
                    'Functions with "_stream" in name'
                ]
            }

    async def _error_stream(self, error_message: str):
        """Generate error stream for SSE."""
        yield f"event: error\ndata: {error_message}\n\n"

    def _get_detection_reason(self, func) -> str:
        """Get reason why function was detected as streamable."""
        if hasattr(func, '_yaapp_stream') and func._yaapp_stream:
            return "Explicit @stream decorator"
        elif inspect.isgeneratorfunction(func):
            return "Sync generator function"
        elif inspect.isasyncgenfunction(func):
            return "Async generator function"
        elif '_stream' in func.__name__ or func.__name__.startswith('stream_'):
            return "Function name contains 'stream'"
        else:
            return "Return type annotation indicates streaming"

    def _add_usual_endpoints(self, app, command_tree: Dict[str, Any], path_prefix: str = ""):
        """Override to add streaming detection info to regular endpoints."""
        super()._add_usual_endpoints(app, command_tree, path_prefix)
        
        # Also add streaming availability info to _describe endpoints
        describe_path = f"{path_prefix}/_describe"
        
        def make_enhanced_describe_endpoint(tree):
            def enhanced_describe_endpoint():
                """Describe available commands with streaming info."""
                commands = []
                for name, item in tree.items():
                    if not name.startswith('_'):  # Skip internal items
                        command_info = {"name": name}
                        
                        if item['type'] == 'function':
                            func = item['func']
                            command_info['streamable'] = StreamDetector.should_stream(func)
                            if command_info['streamable']:
                                command_info['stream_format'] = StreamDetector.get_stream_format(func)
                                command_info['stream_endpoint'] = f"{path_prefix}/{name}/stream"
                        
                        commands.append(command_info)
                
                return {"commands": commands}
            return enhanced_describe_endpoint
        
        # Override the describe endpoint with enhanced version
        app.get(describe_path, summary="Describe commands with streaming info")(
            make_enhanced_describe_endpoint(command_tree)
        )