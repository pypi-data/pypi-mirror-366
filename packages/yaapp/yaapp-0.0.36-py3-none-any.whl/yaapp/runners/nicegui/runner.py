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
        
        # Get all available functions and methods
        available_items = _get_available_items(app_instance)
        item_names = list(available_items.keys())
        
        if not item_names:
            ui.label('No functions available')
            return
            
        with ui.card().classes('w-full max-w-2xl'):
            selected_func = ui.select(item_names, label='Select Function/Method').classes('w-full')
            
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
                    if selected_func.value and selected_func.value in available_items:
                        item_info = available_items[selected_func.value]
                        
                        if item_info['type'] == 'method':
                            info_html = f"""
                            <div>
                                <p><strong>Method:</strong> {selected_func.value}</p>
                                <p><strong>Class:</strong> {item_info['class_name']}</p>
                                <p><strong>Description:</strong> {item_info['doc'] or 'No description'}</p>
                                <p><strong>Signature:</strong> <code>{item_info['signature']}</code></p>
                                <p><strong>Example params:</strong></p>
                                <pre>{item_info['example_params']}</pre>
                            </div>
                            """
                        else:
                            info_html = f"""
                            <div>
                                <p><strong>Function:</strong> {selected_func.value}</p>
                                <p><strong>Description:</strong> {item_info['doc'] or 'No description'}</p>
                                <p><strong>Signature:</strong> <code>{item_info['signature']}</code></p>
                                <p><strong>Example params:</strong></p>
                                <pre>{item_info['example_params']}</pre>
                            </div>
                            """
                        info_area.content = info_html
                
                selected_func.on('update:model-value', lambda: update_info())


def _get_available_items(app_instance):
    """Get all available functions and methods from the registry."""
    available_items = {}
    
    for name, (obj, exposer) in app_instance._registry.items():
        # Handle both functions and class instances
        if inspect.isclass(obj) or hasattr(obj, '__dict__'):
            # It's a class or instance - get its methods
            for method_name in dir(obj):
                if not method_name.startswith('_'):
                    method = getattr(obj, method_name)
                    if callable(method):
                        try:
                            sig = inspect.signature(method)
                            doc = getattr(method, '__doc__', 'No description')
                            example_params = _generate_example_params(sig)
                            
                            full_name = f"{name}.{method_name}"
                            available_items[full_name] = {
                                'type': 'method',
                                'class_name': name,
                                'method_name': method_name,
                                'signature': str(sig),
                                'doc': doc,
                                'example_params': example_params
                            }
                        except (ValueError, TypeError):
                            # Skip methods that can't be inspected
                            continue
        else:
            # It's a regular function
            try:
                sig = inspect.signature(obj)
                doc = getattr(obj, '__doc__', 'No description')
                example_params = _generate_example_params(sig)
                
                available_items[name] = {
                    'type': 'function',
                    'signature': str(sig),
                    'doc': doc,
                    'example_params': example_params
                }
            except (ValueError, TypeError):
                # Skip objects that can't be inspected
                continue
    
    return available_items


def _generate_example_params(sig: inspect.Signature) -> str:
    """Generate example parameters for function signature."""
    example = {}
    for param in sig.parameters.values():
        if param.name == 'self':
            continue
            
        if param.annotation == bool:
            example[param.name] = True
        elif param.annotation == int:
            example[param.name] = 42
        elif param.annotation == float:
            example[param.name] = 3.14
        elif param.annotation == list:
            example[param.name] = ["item1", "item2"]
        elif param.annotation == dict:
            example[param.name] = {"key": "value"}
        else:
            example[param.name] = "example_value"
    
    return json.dumps(example, indent=2) if example else "{}"


async def _call_function_async(app_instance, item_name: str, kwargs: Dict[str, Any]):
    """Execute a yaapp function or method asynchronously."""
    # Check if it's a method call (contains a dot)
    if '.' in item_name:
        class_name, method_name = item_name.split('.', 1)
        
        if class_name not in app_instance._registry:
            return {"error": f"Class '{class_name}' not found"}
        
        obj, exposer = app_instance._registry[class_name]
        
        if not hasattr(obj, method_name):
            return {"error": f"Method '{method_name}' not found in class '{class_name}'"}
        
        method = getattr(obj, method_name)
        
        try:
            # Call the method directly
            import asyncio
            if asyncio.iscoroutinefunction(method):
                result = await method(**kwargs)
            else:
                result = method(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Method execution error: {str(e)}"}
    
    else:
        # Regular function call
        if item_name not in app_instance._registry:
            return {"error": f"Function '{item_name}' not found"}
        
        obj, exposer = app_instance._registry[item_name]
        
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