"""
Streamlit runner for yaapp.
Provides a web-based interface using Streamlit.
"""

import inspect
import json
import asyncio
import tempfile
import os
import subprocess
from typing import Dict, Any

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def help() -> str:
    """Return Streamlit runner-specific help text."""
    return """
📊 STREAMLIT RUNNER HELP:
  --port INTEGER  Server port (default: 8501)
  --share BOOL    Share publicly (default: False)
    """


def run(app_instance, **kwargs):
    """Execute the Streamlit runner with the app instance."""
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: uv add streamlit")
        return
        
    if not app_instance._registry:
        print("No functions exposed. Use @app.expose to expose functions.")
        return
        
    port = kwargs.get('port', 8501)
    share = kwargs.get('share', False)
    
    print(f"Starting Streamlit interface on port {port}")
    print(f"Available functions: {list(app_instance._registry.keys())}")
    
    app_content = _generate_streamlit_app(app_instance)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(app_content)
        temp_file = f.name
    
    try:
        cmd = [
            'streamlit', 'run', temp_file, 
            '--server.port', str(port),
            '--server.headless', 'true'
        ]
        if share:
            cmd.extend(['--server.enableCORS', 'false'])
        
        subprocess.run(cmd)
    finally:
        os.unlink(temp_file)


def _generate_streamlit_app(app_instance):
    """Generate Streamlit app content."""
    functions_data = {}
    
    for name, (obj, exposer) in app_instance._registry.items():
        # Handle both functions and class instances
        if inspect.isclass(obj) or hasattr(obj, '__dict__'):
            # It's a class or instance - get its methods
            methods = {}
            for method_name in dir(obj):
                if not method_name.startswith('_'):
                    method = getattr(obj, method_name)
                    if callable(method):
                        try:
                            sig = inspect.signature(method)
                            doc = getattr(method, '__doc__', 'No description')
                            methods[method_name] = {
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
                        except (ValueError, TypeError):
                            # Skip methods that can't be inspected
                            continue
            
            functions_data[name] = {
                'type': 'class_instance',
                'signature': f"{name} (class instance)",
                'doc': getattr(obj, '__doc__', 'No description'),
                'methods': methods
            }
        else:
            # It's a regular function
            try:
                sig = inspect.signature(obj)
                doc = getattr(obj, '__doc__', 'No description')
                functions_data[name] = {
                    'type': 'function',
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
            except (ValueError, TypeError):
                # Skip objects that can't be inspected
                continue
    
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
    
    if func_info['type'] == 'class_instance':
        # Handle class instances with methods
        st.subheader("Available Methods")
        
        if func_info['methods']:
            method_names = list(func_info['methods'].keys())
            selected_method = st.selectbox("Select Method", method_names)
            
            if selected_method:
                method_info = func_info['methods'][selected_method]
                st.write(f"**Method Description:** {{method_info['doc']}}")
                st.code(f"Method Signature: {{method_info['signature']}}")
                
                params = {{}}
                if method_info['params']:
                    st.subheader("Parameters")
                    for param_name, param_info in method_info['params'].items():
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
                
                if st.button("Execute Method"):
                    try:
                        st.success(f"Method {{selected_method}} would be executed with parameters:")
                        st.json(params)
                        st.info("Note: This is a prototype. Real execution requires core integration.")
                    except Exception as e:
                        st.error(f"Error: {{str(e)}}")
        else:
            st.info("No public methods available for this class instance.")
    
    else:
        # Handle regular functions
        params = {{}}
        if func_info.get('params'):
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