"""
Simple server runner plugin with working portalloc integration.
"""

import inspect
from typing import Dict, Any
from yaapp import yaapp


@yaapp.expose("server")
class Server:
    """Simple FastAPI server with portalloc integration."""
    
    def __init__(self, config=None):
        """Initialize Server runner."""
        self.config = config or {}
    
    def help(self) -> str:
        """Return server help text."""
        return "🌐 SERVER: FastAPI server with portalloc integration"
    
    def run(self, app_instance, **kwargs):
        """Execute the server runner."""
        host = kwargs.get('host', self.config.get('host', 'localhost'))
        reload = kwargs.get('reload', self.config.get('reload', False))
        
        # Get port from portalloc
        port = self._get_port_from_portalloc(app_instance, kwargs)
        
        self._start_server(host, port, reload)
    
    def _get_port_from_portalloc(self, app_instance, kwargs):
        """Get port from portalloc plugin."""
        # Check explicit port first
        if 'port' in kwargs:
            return kwargs['port']
        if 'port' in self.config:
            return self.config['port']
        
        # Try portalloc
        try:
            if hasattr(app_instance, '_registry') and 'portalloc' in app_instance._registry:
                portalloc_obj, portalloc_exposer = app_instance._registry['portalloc']
                
                # Call allocate_port through the exposer
                result = portalloc_exposer.run(portalloc_obj, function_name='allocate_port', service_name='server')
                
                if hasattr(result, 'is_ok') and result.is_ok():
                    port_info = result.unwrap()
                    if isinstance(port_info, dict) and 'port' in port_info and 'error' not in port_info:
                        allocated_port = port_info['port']
                        print(f"🔌 Server: Allocated port {allocated_port} from portalloc")
                        return allocated_port
                    else:
                        print(f"⚠️ Server: Invalid portalloc response: {port_info}")
                else:
                    print(f"⚠️ Server: Portalloc call failed: {result.as_error if hasattr(result, 'as_error') else result}")
            else:
                print("ℹ️ Server: Portalloc not available, using default port")
        except Exception as e:
            print(f"⚠️ Server: Error with portalloc: {e}")
        
        return 8000
    
    def _start_server(self, host: str, port: int, reload: bool):
        """Start FastAPI server."""
        print(f"Starting web server on {host}:{port}")
        
        try:
            import uvicorn
            from fastapi import FastAPI
            from pydantic import BaseModel
        except ImportError:
            print("FastAPI required. Install with: pip install fastapi uvicorn pydantic")
            return
        
        # Create FastAPI app
        app = FastAPI(title="YApp API")
        
        # Add RPC endpoint
        class RPCRequest(BaseModel):
            function: str
            args: Dict[str, Any] = {}
        
        @app.get("/_describe_rpc")
        def describe_rpc():
            """Describe available functions."""
            functions = {}
            for name, (obj, exposer) in yaapp._registry.items():
                functions[name] = {
                    'type': 'class' if inspect.isclass(obj) else 'function'
                }
            return {"functions": functions}
        
        @app.post("/_rpc")
        async def rpc_endpoint(request: RPCRequest):
            """RPC function execution."""
            function_name = request.function
            arguments = request.args
            
            if function_name not in yaapp._registry:
                return {"error": f"Function '{function_name}' not found"}
            
            try:
                obj, exposer = yaapp._registry[function_name]
                result = await exposer.run_async(obj, **arguments)
                
                if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                    if result.is_ok():
                        return result.unwrap()
                    else:
                        return {"error": f"Execution failed: {result.error_message}"}
                else:
                    return result
            except Exception as e:
                return {"error": str(e)}
        
        # Start server
        uvicorn.run(app, host=host, port=port, reload=reload)