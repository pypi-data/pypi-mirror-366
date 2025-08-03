"""
NiceGUI runner for yaapp.
Provides a web-based interface using NiceGUI.
"""

import inspect
import json
import os
from typing import Dict, Any

try:
    from nicegui import ui, app
    HAS_NICEGUI = True
except ImportError:
    HAS_NICEGUI = False


def help() -> str:
    """Return NiceGUI runner-specific help text."""
    return """
🎨 NICEGUI RUNNER HELP:
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8080)
    """


def run(app_instance, **kwargs):
    """Execute the NiceGUI runner with the app instance."""
    if not HAS_NICEGUI:
        print("NiceGUI not available. Install with: uv add nicegui")
        return
        
    if not app_instance._registry:
        print("No functions exposed. Use @app.expose to expose functions.")
        return
        
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', 8081)
    
    print(f"Starting NiceGUI interface on {host}:{port}")
    print(f"Available functions: {list(app_instance._registry.keys())}")
    
    # Set up the UI
    _setup_ui(app_instance)
    
    # Run NiceGUI
    ui.run(host=host, port=port, title="yaapp Interface", show=False, reload=False)


def _setup_ui(app_instance):
    """Set up the NiceGUI interface."""
    @ui.page('/')
    def main_page():
        ui.label('yaapp Function Interface').classes('text-h4 q-mb-md')
        
        functions = list(app_instance._registry.keys())
        if not functions:
            ui.label('No functions available')
            return
            
        with ui.card().classes('w-full max-w-2xl'):
            selected_func = ui.select(functions, label='Select Function').classes('w-full')
            
            params_input = ui.textarea(
                label='Parameters (JSON)', 
                placeholder='{"param1": "value1", "param2": 123}'
            ).classes('w-full')
            
            result_area = ui.textarea(
                label='Result', 
                value='Results will appear here...'
            ).props('readonly').classes('w-full')
            
            async def execute_function():
                if not selected_func.value:
                    result_area.value = 'Error: No function selected'
                    return
                    
                try:
                    params = json.loads(params_input.value or '{}')
                    result = await _call_function_async(app_instance, selected_func.value, params)
                    result_area.value = json.dumps(result, indent=2)
                except json.JSONDecodeError:
                    result_area.value = 'Error: Invalid JSON in parameters'
                except Exception as e:
                    result_area.value = f'Error: {str(e)}'
            
            ui.button('Execute', on_click=execute_function).classes('q-mt-md')
            
            with ui.expansion('Function Info', icon='info').classes('q-mt-md'):
                info_area = ui.html()
                
                def update_info():
                    if selected_func.value and selected_func.value in app_instance._registry:
                        obj, exposer = app_instance._registry[selected_func.value]
                        sig = inspect.signature(obj)
                        doc = getattr(obj, '__doc__', 'No description')
                        
                        info_html = f"""
                        <div>
                            <p><strong>Description:</strong> {doc or 'No description'}</p>
                            <p><strong>Signature:</strong> <code>{sig}</code></p>
                        </div>
                        """
                        info_area.content = info_html
                
                selected_func.on('update:model-value', lambda: update_info())


async def _call_function_async(app_instance, function_name: str, kwargs: Dict[str, Any]):
    """Execute a yaapp function asynchronously."""
    if function_name not in app_instance._registry:
        return {"error": f"Function '{function_name}' not found"}
    
    obj, exposer = app_instance._registry[function_name]
    
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