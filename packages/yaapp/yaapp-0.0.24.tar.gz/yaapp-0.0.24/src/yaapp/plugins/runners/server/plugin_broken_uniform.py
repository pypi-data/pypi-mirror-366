"""
FINAL server runner plugin with UNIFORM EXPOSER INTERFACE.
"""

import inspect
from typing import Dict, Any
from yaapp import yaapp


@yaapp.expose("server")
class Server:
    """FastAPI server with uniform exposer interface."""
    
    def __init__(self, config=None):
        """Initialize Server runner."""
        self.config = config or {}
    
    def help(self) -> str:
        """Return server help text."""
        return "🌐 SERVER: FastAPI server with uniform exposer interface"
    
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
                
                # Handle nested Result objects (double-wrapped)
                port_info = result
                if hasattr(result, 'is_ok') and result.is_ok():
                    port_info = result.unwrap()
                    
                    # Check if it's still wrapped
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
                    'has_execute_call': hasattr(obj, 'execute_call'),
                    'methods': [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))] if hasattr(obj, '__dict__') else []
                }
            return {"functions": functions}
        
        @app.post("/_rpc")
        async def rpc_endpoint(request: RPCRequest):
            """RPC function execution with UNIFORM EXPOSER INTERFACE."""
            function_name = request.function
            arguments = request.args
            
            print(f"🔍 RPC: Received call for '{function_name}' with args {arguments}")
            
            # First try direct function lookup
            if function_name in yaapp._registry:
                try:
                    obj, exposer = yaapp._registry[function_name]
                    result = await exposer.run_async(obj, **arguments)
                    
                    if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                        if result.is_ok():
                            return result.unwrap()
                        else:
                            return {"error": f"Execution failed: {getattr(result, 'error_message', str(result))}"}
                    else:
                        return result
                except Exception as e:
                    return {"error": str(e)}
            
            # UNIFORM INTERFACE: Try all plugins with function_name parameter
            for plugin_name, (obj, exposer) in yaapp._registry.items():
                try:
                    print(f"🔍 Trying plugin '{plugin_name}' for function '{function_name}'")
                    
                    # UNIFORM CALL: All exposers support function_name parameter
                    result = await exposer.run_async(obj, function_name=function_name, **arguments)
                    
                    if hasattr(result, 'is_ok'):
                        if result.is_ok():
                            unwrapped = result.unwrap()
                            print(f"✅ Plugin '{plugin_name}' successfully handled '{function_name}'")
                            return unwrapped
                        else:
                            # This plugin couldn't handle the function, try next
                            error_msg = getattr(result, 'as_error', str(result))
                            print(f"🔍 Plugin '{plugin_name}' failed: {error_msg}")
                            continue
                    else:
                        # Non-Result return, assume success
                        print(f"✅ Plugin '{plugin_name}' successfully handled '{function_name}' (non-Result)")
                        return result
                        
                except Exception as e:
                    print(f"🔍 Plugin '{plugin_name}' exception: {e}")
                    continue
            
            # Function not found in any plugin
            return {"error": f"Function '{function_name}' not found in any plugin"}
        
        # Start server
        uvicorn.run(app, host=host, port=port, reload=reload)