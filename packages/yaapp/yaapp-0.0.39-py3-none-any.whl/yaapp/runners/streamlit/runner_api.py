"""
Streamlit runner for yaapp - HTTP API approach.
Uses yaapp's built-in server and makes HTTP requests.
"""

import requests
import json
import time
import threading
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
📊 STREAMLIT RUNNER (HTTP API):
  --port INTEGER       Streamlit port (default: 8501)
  --api-port INTEGER   yaapp API port (default: 8000)
  --share BOOL         Share publicly (default: False)
    """


def run(app_instance, **kwargs):
    """Execute the Streamlit runner with HTTP API integration."""
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: uv add streamlit")
        return
        
    if not app_instance._registry:
        print("No functions exposed. Use @app.expose to expose functions.")
        return
        
    port = kwargs.get('port', 8501)
    api_port = kwargs.get('api_port', 8000)
    share = kwargs.get('share', False)
    
    print(f"Starting yaapp API server on port {api_port}")
    print(f"Starting Streamlit interface on port {port}")
    
    # Start yaapp server in background thread
    server_thread = threading.Thread(
        target=_start_yaapp_server,
        args=(app_instance, api_port),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Create Streamlit app that uses HTTP API
    app_content = _generate_api_streamlit_app(api_port)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(app_content)
        temp_file = f.name
    
    try:
        import subprocess
        cmd = [
            'streamlit', 'run', temp_file, 
            '--server.port', str(port)
        ]
        if share:
            cmd.extend(['--server.enableCORS', 'false'])
        
        print(f"🌐 Streamlit will be available at: http://localhost:{port}")
        print(f"🔗 yaapp API available at: http://localhost:{api_port}")
        subprocess.run(cmd)
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def _start_yaapp_server(app_instance, port):
    """Start yaapp server in background."""
    try:
        # Use yaapp's built-in server runner
        from yaapp.runners.server.runner import _start_server
        _start_server(app_instance, 'localhost', port, False)
    except Exception as e:
        print(f"Failed to start yaapp server: {e}")


def _generate_api_streamlit_app(api_port):
    """Generate Streamlit app that uses HTTP API."""
    return f'''
import streamlit as st
import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:{api_port}"

def call_api(endpoint, method="GET", data=None):
    """Make HTTP request to yaapp API."""
    try:
        url = f"{{API_BASE_URL}}/{{endpoint}}"
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {{"error": f"API request failed: {{str(e)}}"}}
    except json.JSONDecodeError as e:
        return {{"error": f"Invalid JSON response: {{str(e)}}"}}

def get_api_functions():
    """Get available functions from yaapp API."""
    return call_api("_describe_rpc")

def execute_rpc_call(function_name, args):
    """Execute RPC call via HTTP API."""
    data = {{
        "function": function_name,
        "args": args
    }}
    return call_api("_rpc", "POST", data)

# Streamlit App
st.set_page_config(
    page_title="yaapp API Interface",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 yaapp API Interface")
st.markdown("*HTTP API integration - clean REST interface*")

# Test API connection
with st.spinner("Connecting to yaapp API..."):
    api_info = get_api_functions()

if isinstance(api_info, dict) and 'error' in api_info:
    st.error(f"❌ Cannot connect to yaapp API: {{api_info['error']}}")
    st.info(f"Make sure yaapp server is running on {{API_BASE_URL}}")
    st.stop()

functions_data = api_info.get('functions', {{}})

if not functions_data:
    st.error("No functions available from API")
    st.stop()

# Function selection
st.sidebar.title("📋 Available Functions")
st.sidebar.success(f"✅ Connected to {{API_BASE_URL}}")

function_names = list(functions_data.keys())
selected_function = st.sidebar.selectbox("Select Function", function_names)

if selected_function:
    func_info = functions_data[selected_function]
    
    st.header(f"🌐 {{selected_function}}")
    st.write(f"**Type:** {{func_info.get('type', 'unknown')}}")
    st.write(f"**Object Type:** {{func_info.get('obj_type', 'unknown')}}")
    
    # Show available methods if it's a class/instance
    methods = func_info.get('methods', [])
    if methods:
        st.write(f"**Available Methods:** {{', '.join(methods)}}")
        
        selected_method = st.selectbox("Select Method", methods)
        
        if selected_method:
            st.subheader(f"🎯 {{selected_method}}")
            
            # Simple parameter input (could be enhanced with API introspection)
            st.write("**Parameters:**")
            param_input = st.text_area(
                "Enter parameters as JSON",
                value='{{}}',
                help="Enter parameters as JSON object, e.g. {{\\"key\\": \\"value\\", \\"number\\": 42}}"
            )
            
            if st.button("🌐 Execute via API", type="primary"):
                try:
                    # Parse parameters
                    params = json.loads(param_input) if param_input.strip() else {{}}
                    
                    with st.spinner("Calling API..."):
                        # Make RPC call
                        function_call = f"{{selected_function}}.{{selected_method}}" if selected_method else selected_function
                        result = execute_rpc_call(function_call, params)
                        
                        st.subheader("📋 API Response")
                        if isinstance(result, dict) and 'error' in result:
                            st.error(f"❌ {{result['error']}}")
                        else:
                            st.success("✅ API call successful!")
                            st.json(result)
                            
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON in parameters: {{e}}")
    else:
        # Direct function call
        st.subheader("🎯 Direct Function Call")
        
        param_input = st.text_area(
            "Enter parameters as JSON",
            value='{{}}',
            help="Enter parameters as JSON object"
        )
        
        if st.button("🌐 Execute via API", type="primary"):
            try:
                params = json.loads(param_input) if param_input.strip() else {{}}
                
                with st.spinner("Calling API..."):
                    result = execute_rpc_call(selected_function, params)
                    
                    st.subheader("📋 API Response")
                    if isinstance(result, dict) and 'error' in result:
                        st.error(f"❌ {{result['error']}}")
                    else:
                        st.success("✅ API call successful!")
                        st.json(result)
                        
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON in parameters: {{e}}")

# API Info
st.sidebar.markdown("---")
st.sidebar.markdown("🌐 **HTTP API Integration**")
st.sidebar.markdown("Clean REST interface")
st.sidebar.markdown(f"Functions: {{len(functions_data)}}")

# Show raw API info
with st.expander("🔍 Raw API Info", expanded=False):
    st.json(api_info)
'''