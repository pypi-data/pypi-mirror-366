"""
Gradio runner for yaapp.
Provides a web-based interface using Gradio.
"""

import inspect
import json
import asyncio
from typing import Dict, Any

try:
    import gradio as gr
    HAS_GRADIO = True
    GRADIO_ERROR = None
except ImportError as e:
    HAS_GRADIO = False
    # Capture both the main error and the underlying cause
    error_msg = str(e)
    if hasattr(e, '__cause__') and e.__cause__:
        error_msg += f" (Cause: {e.__cause__})"
    GRADIO_ERROR = error_msg


def help() -> str:
    """Return Gradio runner-specific help text."""
    return """
🤖 GRADIO RUNNER HELP:
  --port INTEGER  Server port (default: 7860)
  --share BOOL    Share publicly (default: False)
    """


def run(app_instance, **kwargs):
    """Execute the Gradio runner with the app instance."""
    if not HAS_GRADIO:
        print("❌ Gradio Runner Error")
        print("")
        if GRADIO_ERROR and "libstdc++" in GRADIO_ERROR:
            print("Gradio is installed but can't load due to missing system libraries.")
            print("This is a system configuration issue, not a yaapp problem.")
            print("")
            print("Missing system library: libstdc++.so.6")
            print("")
            print("Solutions:")
            print("  • Install build-essential: sudo apt install build-essential")
            print("  • Install libstdc++6: sudo apt install libstdc++6")
            print("  • Use a different environment with proper C++ libraries")
            print("")
            print("Alternative runners that work:")
            print("  --server     # FastAPI web server")
            print("  --streamlit  # Streamlit web app (if available)")
            print("  --mcp        # MCP server for AI integration")
        else:
            print("Gradio not available. Install with: uv add gradio")
            if GRADIO_ERROR:
                print(f"Error: {GRADIO_ERROR}")
        print("")
        return
        
    if not app_instance._registry:
        print("No functions exposed. Use @app.expose to expose functions.")
        return
        
    port = kwargs.get('port', 7860)
    share = kwargs.get('share', False)
    
    print(f"Starting Gradio interface on port {port}")
    print(f"Available functions: {list(app_instance._registry.keys())}")
    
    interface = _create_interface(app_instance)
    interface.launch(server_port=port, share=share)


def _create_interface(app_instance):
    """Create Gradio interface."""
    # Get all available functions and methods
    available_items = _get_available_items(app_instance)
    item_names = list(available_items.keys())
    
    def execute_function(selected_item: str, params_json: str):
        if not selected_item:
            return "Error: No function selected"
            
        try:
            params = json.loads(params_json) if params_json.strip() else {}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    _call_function_async(app_instance, selected_item, params)
                )
                return json.dumps(result, indent=2)
            finally:
                loop.close()
                
        except json.JSONDecodeError:
            return "Error: Invalid JSON in parameters"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_function_info(selected_item: str):
        if not selected_item or selected_item not in available_items:
            return "Select a function to see its information"
            
        item_info = available_items[selected_item]
        
        if item_info['type'] == 'method':
            info = f"""
**Method:** {selected_item}
**Class:** {item_info['class_name']}
**Description:** {item_info['doc']}
**Signature:** {item_info['signature']}

**Example parameters:**
```json
{item_info['example_params']}
```
            """
        else:
            info = f"""
**Function:** {selected_item}
**Description:** {item_info['doc']}
**Signature:** {item_info['signature']}

**Example parameters:**
```json
{item_info['example_params']}
```
            """
        return info
    
    with gr.Blocks(title="yaapp Gradio Interface") as interface:
        gr.Markdown("# yaapp Function Interface")
        
        with gr.Row():
            with gr.Column(scale=1):
                func_dropdown = gr.Dropdown(
                    choices=item_names,
                    label="Select Function/Method",
                    value=item_names[0] if item_names else None
                )
                
                params_input = gr.Textbox(
                    label="Parameters (JSON)",
                    placeholder='{"param1": "value1", "param2": 123}',
                    lines=5
                )
                
                execute_btn = gr.Button("Execute Function", variant="primary")
            
            with gr.Column(scale=1):
                function_info = gr.Markdown(
                    value="Select a function to see its information"
                )
                
                result_output = gr.Textbox(
                    label="Result",
                    lines=10,
                    interactive=False
                )
        
        func_dropdown.change(
            fn=get_function_info,
            inputs=[func_dropdown],
            outputs=[function_info]
        )
        
        execute_btn.click(
            fn=execute_function,
            inputs=[func_dropdown, params_input],
            outputs=[result_output]
        )
        
        if item_names:
            interface.load(
                fn=get_function_info,
                inputs=[func_dropdown],
                outputs=[function_info]
            )
    
    return interface


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