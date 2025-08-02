"""
Server runner plugin for yaapp with portalloc integration.
Provides FastAPI web server with auto-generated endpoints and dynamic port allocation.
"""

import inspect
from typing import get_type_hints, Dict, Any
# Import will be done dynamically to avoid circular imports

from yaapp import yaapp


@yaapp.expose("server")
class Server:
    """FastAPI-based server runner with dual endpoint structure and portalloc integration."""
    
    def __init__(self, config=None):
        """Initialize Server runner with optional configuration."""
        self.config = config or {}
    
    def help(self) -> str:
        """Return server runner-specific help text."""
        return """
🌐 SERVER RUNNER HELP:
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (uses portalloc if available)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the server runner with the app instance."""
        # Extract server configuration
        host = kwargs.get('host', self.config.get('host', 'localhost'))
        reload = kwargs.get('reload', self.config.get('reload', False))
        workers = kwargs.get('workers', self.config.get('workers', 1))
        
        # Get port from portalloc if available, otherwise use config/default
        port = self._get_port_from_portalloc(app_instance, kwargs)
        
        self._start_server(host, port, reload, workers)
    
    def _get_port_from_portalloc(self, app_instance, kwargs):
        """Get port from portalloc plugin if available, otherwise use config/default."""
        # First check if port is explicitly provided
        if 'port' in kwargs:
            return kwargs['port']
        
        if 'port' in self.config:
            return self.config['port']
        
        # Try to get port from portalloc plugin
        try:
            if hasattr(app_instance, '_registry') and 'portalloc' in app_instance._registry:
                portalloc_obj, portalloc_exposer = app_instance._registry['portalloc']
                
                # Get an instance of portalloc
                if hasattr(portalloc_exposer, 'run'):
                    result = portalloc_exposer.run(portalloc_obj)
                    if hasattr(result, 'is_ok') and result.is_ok():
                        portalloc_instance = result.unwrap()
                        
                        # Request a port allocation
                        if hasattr(portalloc_instance, 'allocate_port'):
                            port_info = portalloc_instance.allocate_port('server')
                            if 'port' in port_info and 'error' not in port_info:
                                allocated_port = port_info['port']
                                print(f"🔌 Server: Allocated port {allocated_port} from portalloc")
                                return allocated_port
                            else:
                                print(f"⚠️ Server: Failed to allocate port from portalloc: {port_info.get('error', port_info)}")
                        else:
                            print("⚠️ Server: Portalloc instance doesn't have allocate_port method")
                    else:
                        print(f"⚠️ Server: Failed to get portalloc instance: {result.as_error if hasattr(result, 'as_error') else result}")
                else:
                    print("⚠️ Server: Portalloc exposer doesn't have run method")
            else:
                print("ℹ️ Server: Portalloc plugin not found, using default port")
        except Exception as e:
            print(f"⚠️ Server: Error accessing portalloc: {e}")
        
        # Fallback to default port
        return 8000
    
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

        # Add RPC endpoints (simplified for testing)
        self._add_rpc_endpoints(fastapi_app)

        # Start the server
        uvicorn.run(fastapi_app, host=host, port=port, reload=reload)

    def _add_rpc_endpoints(self, app):
        """Add RPC-style endpoints."""
        try:
            from pydantic import BaseModel
        except ImportError:
            print("Error: pydantic is required for FastAPI runner")
            return
        from typing import Optional
        
        class RPCRequest(BaseModel):
            function: str
            args: Dict[str, Any] = {}
            arguments: Optional[Dict[str, Any]] = None
        
        @app.get("/_describe_rpc")
        def describe_rpc():
            """Describe all available functions for RPC interface."""
            functions = {}
            for name, (obj, exposer) in yaapp._registry.items():
                functions[name] = {
                    'type': 'class' if inspect.isclass(obj) else 'function',
                    'description': getattr(obj, '__doc__', f"Function {name}")
                }
            return {"functions": functions}
        
        @app.post("/_rpc")
        async def rpc_endpoint(request: RPCRequest):
            """RPC-style function execution."""
            function_name = request.function
            # Support both 'args' and 'arguments' for compatibility
            arguments = request.args if request.args else (request.arguments or {})
            
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