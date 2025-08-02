"""
FIXED: Server runner plugin with CORRECT ARCHITECTURE.
"""

import inspect
from typing import Dict, Any
from yaapp import yaapp


@yaapp.expose("server")
class ServerRunner:  # ✅ FIXED: Renamed from Server to ServerRunner
    """FastAPI server with CORRECT ARCHITECTURE."""
    
    def __init__(self, config=None):
        """Initialize Server runner."""
        self.config = config or {}
    
    def help(self) -> str:
        """Return server help text with parseable options."""
        return """
🌐 SERVER: FastAPI server with CORRECT ARCHITECTURE
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the server runner."""
        host = kwargs.get('host', self.config.get('host', 'localhost'))
        reload = kwargs.get('reload', self.config.get('reload', False))
        
        # Get port from portalloc
        port = self._get_port_from_portalloc(app_instance, kwargs)
        
        self._start_server(app_instance, host, port, reload)
    
    def _get_port_from_portalloc(self, app_instance, kwargs):
        """Get port from portalloc plugin using CORRECT ARCHITECTURE."""
        # Check explicit port first
        if 'port' in kwargs:
            return kwargs['port']
        if 'port' in self.config:
            return self.config['port']
        
        # Try portalloc using CORRECT ARCHITECTURE
        try:
            # ✅ FIXED: Use core.execute_function instead of direct exposer calls
            result = app_instance.execute_function('portalloc', function_name='allocate_port', service_name='server')
            
            if result.is_ok():
                port_info = result.unwrap()
                
                # Handle nested Result objects (double-wrapped)
                if hasattr(port_info, 'is_ok') and port_info.is_ok():
                    port_info = port_info.unwrap()
                
                # Now port_info should be the actual dict
                if isinstance(port_info, dict) and 'port' in port_info and 'error' not in port_info:
                    allocated_port = port_info['port']
                    print(f"🔌 Server: Allocated port {allocated_port} from portalloc")
                    return allocated_port
                else:
                    print(f"⚠️ Server: Portalloc failed: {port_info}")
            else:
                print(f"⚠️ Server: Portalloc execution failed: {result.as_error}")
                
        except Exception as e:
            print(f"⚠️ Server: Error with portalloc: {e}")
        
        return 8000
    
    def _start_server(self, app_instance, host: str, port: int, reload: bool):
        """Start FastAPI server with CORRECT ARCHITECTURE."""
        print(f"🚀 Starting web server on {host}:{port} with CORRECT ARCHITECTURE")
        
        try:
            import uvicorn
            from fastapi import FastAPI
            from pydantic import BaseModel
        except ImportError:
            print("FastAPI required. Install with: pip install fastapi uvicorn pydantic")
            return
        
        # Create FastAPI app
        app = FastAPI(title="YApp API - CORRECT ARCHITECTURE")
        
        # Add RPC endpoint
        class RPCRequest(BaseModel):
            function: str
            args: Dict[str, Any] = {}
        
        @app.get("/_describe_rpc")
        def describe_rpc():
            """Describe available functions."""
            functions = {}
            for name, (obj, exposer) in app_instance._registry.items():
                obj_type = 'unknown'
                if inspect.isclass(obj):
                    obj_type = 'class'
                elif hasattr(obj, 'execute_call'):
                    obj_type = 'custom_exposer'
                elif callable(obj):
                    obj_type = 'function'
                else:
                    obj_type = 'instance'
                
                functions[name] = {
                    'type': obj_type,
                    'obj_type': type(obj).__name__,
                    'exposer_type': type(exposer).__name__,
                    'has_execute_call': hasattr(obj, 'execute_call'),
                    'methods': [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))] if hasattr(obj, '__dict__') else []
                }
            return {"functions": functions}
        
        @app.post("/_rpc")
        async def rpc_endpoint(request: RPCRequest):
            """RPC function execution using CORRECT ARCHITECTURE."""
            function_name = request.function
            arguments = request.args
            
            print(f"🔍 RPC: Received call for '{function_name}' with args {arguments}")
            
            # ✅ FIXED: Use core.execute_function instead of direct exposer calls
            result = app_instance.execute_function(function_name, **arguments)
            
            if result.is_ok():
                print(f"✅ RPC: Successfully executed '{function_name}' via CORRECT ARCHITECTURE")
                return result.unwrap()
            else:
                print(f"❌ RPC: Failed to execute '{function_name}': {result.as_error}")
                return {"error": result.as_error}
        
        # Start server
        uvicorn.run(app, host=host, port=port, reload=reload)


# ✅ FIXED: Add alias for backward compatibility
Server = ServerRunner