"""
Server runner for yaapp.
Provides FastAPI web server functionality.
"""

import inspect
from typing import Dict, Any


def help() -> str:
    """Return server help text with parseable options."""
    return """
🌐 SERVER: FastAPI server
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
    """


def run(app_instance, **kwargs):
    """Execute the server runner."""
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', 8000)
    reload = kwargs.get('reload', False)
    
    _start_server(app_instance, host, port, reload)


def _start_server(app_instance, host: str, port: int, reload: bool):
    """Start FastAPI server."""
    print(f"🚀 Starting web server on {host}:{port}")
    
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
        """RPC function execution."""
        function_name = request.function
        arguments = request.args
        
        print(f"🔍 RPC: Received call for '{function_name}' with args {arguments}")
        
        # Use core.execute_function
        result = app_instance.execute_function(function_name, **arguments)
        
        if result.is_ok():
            print(f"✅ RPC: Successfully executed '{function_name}'")
            return result.unwrap()
        else:
            print(f"❌ RPC: Failed to execute '{function_name}': {result.as_error}")
            return {"error": result.as_error}
    
    # Start server
    uvicorn.run(app, host=host, port=port, reload=reload)