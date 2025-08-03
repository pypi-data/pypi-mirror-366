"""
Streamlit runner for yaapp.
Provides a web-based interface using Streamlit with dynamic function discovery.
"""

import inspect
import json
import tempfile
import os
import subprocess
import sys
import pickle
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
    
    # Serialize the app instance data for the Streamlit app
    app_data = _serialize_app_instance(app_instance)
    app_content = _generate_dynamic_streamlit_app(app_data)
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(app_content)
        temp_file = f.name
    
    # Create data file for app instance
    data_file = temp_file.replace('.py', '_data.pkl')
    with open(data_file, 'wb') as f:
        pickle.dump(app_data, f)
    
    try:
        cmd = [
            'streamlit', 'run', temp_file, 
            '--server.port', str(port)
        ]
        if share:
            cmd.extend(['--server.enableCORS', 'false'])
        
        # Set environment variable for data file
        env = os.environ.copy()
        env['YAAPP_DATA_FILE'] = data_file
        
        print(f"🌐 Streamlit will be available at: http://localhost:{port}")
        subprocess.run(cmd, env=env)
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        if os.path.exists(data_file):
            os.unlink(data_file)


def _serialize_app_instance(app_instance):
    """Serialize app instance data for the Streamlit app."""
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
                                'params': _extract_params(sig)
                            }
                        except (ValueError, TypeError):
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
                    'params': _extract_params(sig)
                }
            except (ValueError, TypeError):
                continue
    
    return {
        'functions': functions_data,
        'plugins_loaded': list(app_instance._registry.keys())
    }


def _extract_params(sig):
    """Extract parameter information from function signature."""
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


def _generate_dynamic_streamlit_app(app_data):
    """Generate a dynamic Streamlit app that works with any yaapp functions."""
    return f'''
import streamlit as st
import subprocess
import sys
import json
import os
import pickle

# Load app data
data_file = os.environ.get('YAAPP_DATA_FILE')
if data_file and os.path.exists(data_file):
    with open(data_file, 'rb') as f:
        APP_DATA = pickle.load(f)
else:
    APP_DATA = {json.dumps(app_data)}

def execute_yaapp_function(function_name, method_name=None, **params):
    """Execute a yaapp function using the actual yaapp CLI."""
    try:
        # Build the command dynamically
        cmd = [sys.executable, '-m', 'yaapp']
        
        # Add plugin loading if needed (detect from loaded plugins)
        plugins_loaded = APP_DATA.get('plugins_loaded', [])
        if plugins_loaded:
            # For now, assume first plugin is the main one
            # This could be made smarter by detecting which plugin the function belongs to
            main_plugin = plugins_loaded[0]
            cmd.extend(['--plugin', main_plugin])
        
        # Add function and method
        if method_name:
            cmd.extend([function_name, method_name])
        else:
            cmd.append(function_name)
        
        # Add parameters
        for param_name, param_value in params.items():
            if param_value is not None and str(param_value).strip():
                cmd.extend([f'--{{param_name.replace("_", "-")}}', str(param_value)])
        
        # Execute the command
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            # Parse the output to extract the result
            output_lines = result.stdout.strip().split('\\n')
            # Look for the "Result:" line
            for line in output_lines:
                if line.startswith('Result: '):
                    result_text = line[8:]  # Remove "Result: " prefix
                    try:
                        # Try to parse as JSON
                        return json.loads(result_text)
                    except json.JSONDecodeError:
                        # Return as string if not JSON
                        return result_text
            
            # If no "Result:" line found, return the last non-empty line
            non_empty_lines = [line for line in output_lines if line.strip()]
            if non_empty_lines:
                return non_empty_lines[-1]
            return "Command executed successfully"
        else:
            return {{"error": f"Command failed: {{result.stderr}}"}}
    
    except subprocess.TimeoutExpired:
        return {{"error": "Command timed out"}}
    except Exception as e:
        return {{"error": f"Execution error: {{str(e)}}"}}

# Streamlit App Configuration
st.set_page_config(
    page_title="yaapp Dynamic Interface",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🚀 yaapp Dynamic Interface")
st.markdown("*Real-time execution of any yaapp functions*")

functions_data = APP_DATA.get('functions', {{}})

if not functions_data:
    st.error("No functions available")
    st.stop()

# Sidebar for function selection
st.sidebar.title("📋 Available Functions")
function_names = list(functions_data.keys())
selected_function = st.sidebar.selectbox("Select Function", function_names)

if selected_function:
    func_info = functions_data[selected_function]
    
    # Display function info
    st.header(f"🔧 {{selected_function}}")
    st.write(f"**Type:** {{func_info['type']}}")
    st.write(f"**Description:** {{func_info['doc']}}")
    
    with st.expander("📖 Function Details", expanded=False):
        st.code(f"Signature: {{func_info['signature']}}")
    
    if func_info['type'] == 'class_instance':
        # Handle class instances with methods
        st.subheader("🎯 Available Methods")
        
        methods = func_info.get('methods', {{}})
        if methods:
            method_names = list(methods.keys())
            selected_method = st.selectbox("Select Method", method_names)
            
            if selected_method:
                method_info = methods[selected_method]
                
                st.write(f"**Method:** `{{selected_method}}`")
                st.write(f"**Description:** {{method_info['doc']}}")
                
                with st.expander("📋 Method Signature"):
                    st.code(method_info['signature'])
                
                # Parameters form for method
                params = {{}}
                method_params = method_info.get('params', {{}})
                
                if method_params:
                    st.subheader("⚙️ Method Parameters")
                    
                    with st.form(f"form_{{selected_function}}_{{selected_method}}"):
                        for param_name, param_info in method_params.items():
                            _render_parameter(param_name, param_info, params)
                        
                        # Submit button
                        submitted = st.form_submit_button("🚀 Execute Method", type="primary")
                        
                        if submitted:
                            _execute_and_display(selected_function, selected_method, params)
                else:
                    # No parameters needed
                    if st.button("🚀 Execute Method", type="primary"):
                        _execute_and_display(selected_function, selected_method, {{}})
        else:
            st.info("No public methods available for this class instance.")
    
    else:
        # Handle regular functions
        func_params = func_info.get('params', {{}})
        params = {{}}
        
        if func_params:
            st.subheader("⚙️ Function Parameters")
            
            with st.form(f"form_{{selected_function}}"):
                for param_name, param_info in func_params.items():
                    _render_parameter(param_name, param_info, params)
                
                # Submit button
                submitted = st.form_submit_button("🚀 Execute Function", type="primary")
                
                if submitted:
                    _execute_and_display(selected_function, None, params)
        else:
            # No parameters needed
            if st.button("🚀 Execute Function", type="primary"):
                _execute_and_display(selected_function, None, {{}})

def _render_parameter(param_name, param_info, params):
    """Render a parameter input widget."""
    param_type = param_info.get('type', 'text')
    required = param_info.get('required', False)
    default = param_info.get('default')
    annotation = param_info.get('annotation', 'Any')
    
    label = f"{{param_name}}"
    if required:
        label += " *"
    
    help_text = f"Type: {{annotation}}"
    if default is not None:
        help_text += f", Default: {{default}}"
    
    if param_type == 'number':
        params[param_name] = st.number_input(
            label, 
            value=int(default) if default and isinstance(default, (int, float)) else 0, 
            step=1, 
            help=help_text
        )
    elif param_type == 'checkbox':
        params[param_name] = st.checkbox(
            label, 
            value=bool(default) if default else False,
            help=help_text
        )
    else:
        params[param_name] = st.text_input(
            label, 
            value=str(default) if default else "",
            help=help_text
        )

def _execute_and_display(function_name, method_name, params):
    """Execute function and display results."""
    with st.spinner("Executing..."):
        # Filter out empty parameters
        filtered_params = {{k: v for k, v in params.items() if v is not None and str(v).strip()}}
        
        # Execute the function
        result = execute_yaapp_function(function_name, method_name, **filtered_params)
        
        # Display result
        st.subheader("📋 Result")
        if isinstance(result, dict) and 'error' in result:
            st.error(f"❌ Error: {{result['error']}}")
        else:
            st.success("✅ Execution completed successfully!")
            
            # Display result based on type
            if isinstance(result, (dict, list)):
                st.json(result)
            elif isinstance(result, bool):
                st.write(f"**Result:** {{result}}")
                if result:
                    st.success("✅ True")
                else:
                    st.warning("❌ False")
            else:
                st.code(str(result))

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("🔗 **yaapp Dynamic Runner**")
st.sidebar.markdown("Works with any yaapp functions!")

# Show loaded plugins
plugins = APP_DATA.get('plugins_loaded', [])
if plugins:
    st.sidebar.markdown("### 📦 Loaded Plugins")
    for plugin in plugins:
        st.sidebar.markdown(f"• {{plugin}}")
'''