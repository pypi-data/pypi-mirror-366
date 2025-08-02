import inspect
import json
import asyncio
import tempfile
import os
import subprocess
from typing import Dict, Any

# Import yaapp for the decorator
from yaapp import yaapp

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


@yaapp.expose("streamlit")
class Streamlit:
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def help(self) -> str:
        return """
📊 STREAMLIT RUNNER HELP:
  --port INTEGER  Server port (default: 8501)
        """
    
    def run(self, app_instance, **kwargs):
        if not HAS_STREAMLIT:
            print("Streamlit not available. Install with: pip install streamlit")
            return
            
        if not yaapp._registry:
            print("No functions exposed. Use @app.expose to expose functions.")
            return
            
        port = kwargs.get('port', self.config.get('port', 8501))
        
        print(f"Starting Streamlit interface on port {port}")
        print(f"Available functions: {list(yaapp._registry.keys())}")
        
        app_content = self._generate_streamlit_app()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(app_content)
            temp_file = f.name
        
        try:
            subprocess.run([
                'streamlit', 'run', temp_file, 
                '--server.port', str(port),
                '--server.headless', 'true'
            ])
        finally:
            os.unlink(temp_file)
    
    def _generate_streamlit_app(self):
        functions_data = {}
        for name, (obj, exposer) in yaapp._registry.items():
            sig = inspect.signature(obj)
            doc = getattr(obj, '__doc__', 'No description')
            functions_data[name] = {
                'signature': str(sig),
                'doc': doc,
                'params': {
                    param.name: {
                        'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'str',
                        'default': param.default if param.default != inspect.Parameter.empty else None
                    }
                    for param in sig.parameters.values()
                    if param.name != 'self'
                }
            }
        
        return f'''
import streamlit as st
import json

FUNCTIONS_DATA = {json.dumps(functions_data, indent=2)}

st.title("yaapp Streamlit Interface")

if not FUNCTIONS_DATA:
    st.error("No functions available")
    st.stop()

st.sidebar.title("Functions")
selected_func = st.sidebar.selectbox("Select Function", list(FUNCTIONS_DATA.keys()))

if selected_func:
    func_info = FUNCTIONS_DATA[selected_func]
    
    st.header(f"Function: {{selected_func}}")
    st.write(f"**Description:** {{func_info['doc']}}")
    st.code(f"Signature: {{func_info['signature']}}")
    
    params = {{}}
    if func_info['params']:
        st.subheader("Parameters")
        for param_name, param_info in func_info['params'].items():
            param_type = param_info['type']
            default_val = param_info['default']
            
            if 'bool' in param_type.lower():
                params[param_name] = st.checkbox(param_name, value=bool(default_val) if default_val else False)
            elif 'int' in param_type.lower():
                params[param_name] = st.number_input(param_name, value=int(default_val) if default_val else 0, step=1)
            elif 'float' in param_type.lower():
                params[param_name] = st.number_input(param_name, value=float(default_val) if default_val else 0.0)
            else:
                params[param_name] = st.text_input(param_name, value=str(default_val) if default_val else "")
    
    if st.button("Execute Function"):
        try:
            st.success("Function would be executed with parameters:")
            st.json(params)
            st.info("Note: This is a prototype. Real execution requires core integration.")
        except Exception as e:
            st.error(f"Error: {{str(e)}}")
'''
    
    async def _call_function_async(self, function_name: str, kwargs: Dict[str, Any]):
        if function_name not in yaapp._registry:
            return {"error": f"Function '{function_name}' not found"}
        
        obj, exposer = yaapp._registry[function_name]
        
        try:
            result = await exposer.run_async(obj, **kwargs)
            
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                if result.is_ok():
                    return result.unwrap()
                else:
                    return {"error": f"Execution failed: {result.error_message}"}
            else:
                return result
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}