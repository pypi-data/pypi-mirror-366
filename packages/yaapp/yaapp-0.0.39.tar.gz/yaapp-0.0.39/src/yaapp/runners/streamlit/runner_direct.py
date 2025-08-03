"""
Streamlit runner for yaapp - DIRECT INTEGRATION approach.
Uses app_instance directly instead of subprocess calls.
"""

import inspect
import json
import tempfile
import os
from typing import Dict, Any

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def help() -> str:
    """Return Streamlit runner-specific help text."""
    return """
📊 STREAMLIT RUNNER (Direct Integration):
  --port INTEGER  Server port (default: 8501)
  --share BOOL    Share publicly (default: False)
    """


def run(app_instance, **kwargs):
    """Execute the Streamlit runner with DIRECT integration."""
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
    
    # Create Streamlit app with DIRECT access to app_instance
    app_content = _generate_direct_streamlit_app()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(app_content)
        temp_file = f.name
    
    # Pass app_instance via environment (pickle it)
    import pickle
    data_file = temp_file.replace('.py', '_app.pkl')
    with open(data_file, 'wb') as f:
        pickle.dump(app_instance, f)
    
    try:
        import subprocess
        cmd = [
            'streamlit', 'run', temp_file, 
            '--server.port', str(port)
        ]
        if share:
            cmd.extend(['--server.enableCORS', 'false'])
        
        # Set environment variable for app instance
        env = os.environ.copy()
        env['YAAPP_APP_INSTANCE'] = data_file
        
        print(f"🌐 Streamlit will be available at: http://localhost:{port}")
        subprocess.run(cmd, env=env)
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        if os.path.exists(data_file):
            os.unlink(data_file)


def _generate_direct_streamlit_app():
    """Generate Streamlit app that uses app_instance DIRECTLY."""
    return '''
import streamlit as st
import pickle
import os
import inspect
from typing import Dict, Any

# Load app instance directly
app_file = os.environ.get('YAAPP_APP_INSTANCE')
if app_file and os.path.exists(app_file):
    with open(app_file, 'rb') as f:
        app_instance = pickle.load(f)
else:
    st.error("App instance not available")
    st.stop()

def execute_function_directly(function_name, method_name=None, **params):
    """Execute function DIRECTLY using app_instance - no subprocess!"""
    try:
        if method_name:
            # For class methods: get object and call method
            if function_name in app_instance._registry:
                obj, exposer = app_instance._registry[function_name]
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    return method(**params)
                else:
                    return {"error": f"Method '{method_name}' not found on {function_name}"}
            else:
                return {"error": f"Function '{function_name}' not found"}
        else:
            # Direct function call
            result = app_instance.execute_function(function_name, **params)
            if result.is_ok():
                return result.unwrap()
            else:
                return {"error": result.as_error}
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}

def get_function_info():
    """Get function information from app_instance registry."""
    functions_data = {}
    
    for name, (obj, exposer) in app_instance._registry.items():
        if inspect.isclass(obj) or hasattr(obj, '__dict__'):
            # Class or instance - get methods
            methods = {}
            for method_name in dir(obj):
                if not method_name.startswith('_'):
                    method = getattr(obj, method_name)
                    if callable(method):
                        try:
                            sig = inspect.signature(method)
                            methods[method_name] = {
                                'signature': str(sig),
                                'doc': getattr(method, '__doc__', 'No description'),
                                'params': _extract_params(sig)
                            }
                        except (ValueError, TypeError):
                            continue
            
            functions_data[name] = {
                'type': 'class_instance',
                'doc': getattr(obj, '__doc__', 'No description'),
                'methods': methods
            }
        else:
            # Regular function
            try:
                sig = inspect.signature(obj)
                functions_data[name] = {
                    'type': 'function',
                    'doc': getattr(obj, '__doc__', 'No description'),
                    'params': _extract_params(sig)
                }
            except (ValueError, TypeError):
                continue
    
    return functions_data

def _extract_params(sig):
    """Extract parameter info from signature."""
    params = {}
    for param in sig.parameters.values():
        if param.name == 'self':
            continue
        
        param_type = 'text'
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                param_type = 'number'
            elif param.annotation == float:
                param_type = 'number'
            elif param.annotation == bool:
                param_type = 'checkbox'
        
        params[param.name] = {
            'type': param_type,
            'required': param.default == inspect.Parameter.empty,
            'default': param.default if param.default != inspect.Parameter.empty else None,
            'annotation': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any'
        }
    
    return params

# Streamlit App
st.set_page_config(
    page_title="yaapp Direct Interface",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ yaapp Direct Interface")
st.markdown("*Direct execution - no subprocess overhead!*")

# Get function info
functions_data = get_function_info()

if not functions_data:
    st.error("No functions available")
    st.stop()

# Function selection
st.sidebar.title("📋 Available Functions")
function_names = list(functions_data.keys())
selected_function = st.sidebar.selectbox("Select Function", function_names)

if selected_function:
    func_info = functions_data[selected_function]
    
    st.header(f"⚡ {selected_function}")
    st.write(f"**Type:** {func_info['type']}")
    st.write(f"**Description:** {func_info['doc']}")
    
    if func_info['type'] == 'class_instance':
        # Handle methods
        methods = func_info.get('methods', {})
        if methods:
            method_names = list(methods.keys())
            selected_method = st.selectbox("Select Method", method_names)
            
            if selected_method:
                method_info = methods[selected_method]
                st.write(f"**Method:** `{selected_method}`")
                st.write(f"**Description:** {method_info['doc']}")
                
                # Parameters
                params = {}
                method_params = method_info.get('params', {})
                
                if method_params:
                    st.subheader("⚙️ Parameters")
                    for param_name, param_info in method_params.items():
                        param_type = param_info.get('type', 'text')
                        required = param_info.get('required', False)
                        default = param_info.get('default')
                        
                        label = param_name
                        if required:
                            label += " *"
                        
                        if param_type == 'number':
                            params[param_name] = st.number_input(label, value=int(default) if default else 0)
                        elif param_type == 'checkbox':
                            params[param_name] = st.checkbox(label, value=bool(default) if default else False)
                        else:
                            params[param_name] = st.text_input(label, value=str(default) if default else "")
                
                # Execute button
                if st.button("⚡ Execute Method", type="primary"):
                    with st.spinner("Executing..."):
                        # Filter empty params
                        filtered_params = {k: v for k, v in params.items() if v is not None and str(v).strip()}
                        
                        # DIRECT execution - no subprocess!
                        result = execute_function_directly(selected_function, selected_method, **filtered_params)
                        
                        st.subheader("📋 Result")
                        if isinstance(result, dict) and 'error' in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ Success!")
                            if isinstance(result, (dict, list)):
                                st.json(result)
                            else:
                                st.code(str(result))

# Show registry info
st.sidebar.markdown("---")
st.sidebar.markdown("⚡ **Direct Integration**")
st.sidebar.markdown("No subprocess overhead!")
st.sidebar.markdown(f"Registry items: {len(app_instance._registry)}")
'''