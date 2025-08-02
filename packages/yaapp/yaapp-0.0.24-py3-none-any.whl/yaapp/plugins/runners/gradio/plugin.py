import inspect
import json
import asyncio
from typing import Dict, Any

# Import yaapp for the decorator
from yaapp import yaapp

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


@yaapp.expose("gradio")
class Gradio:
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def help(self) -> str:
        return """
🤖 GRADIO RUNNER HELP:
  --port INTEGER  Server port (default: 7860)
  --share BOOL    Share publicly (default: False)
        """
    
    def run(self, app_instance, **kwargs):
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
            
        if not yaapp._registry:
            print("No functions exposed. Use @app.expose to expose functions.")
            return
            
        port = kwargs.get('port', self.config.get('port', 7860))
        share = kwargs.get('share', self.config.get('share', False))
        
        print(f"Starting Gradio interface on port {port}")
        print(f"Available functions: {list(yaapp._registry.keys())}")
        
        interface = self._create_interface()
        interface.launch(server_port=port, share=share)
    
    def _create_interface(self):
        functions = list(yaapp._registry.keys())
        
        def execute_function(selected_func: str, params_json: str):
            if not selected_func:
                return "Error: No function selected"
                
            try:
                params = json.loads(params_json) if params_json.strip() else {}
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self._call_function_async(selected_func, params)
                    )
                    return json.dumps(result, indent=2)
                finally:
                    loop.close()
                    
            except json.JSONDecodeError:
                return "Error: Invalid JSON in parameters"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def get_function_info(selected_func: str):
            if not selected_func or selected_func not in yaapp._registry:
                return "Select a function to see its information"
                
            obj, exposer = yaapp._registry[selected_func]
            sig = inspect.signature(obj)
            doc = getattr(obj, '__doc__', 'No description')
            
            info = f"""
**Function:** {selected_func}
**Description:** {doc}
**Signature:** {sig}

**Example parameters:**
```json
{self._generate_example_params(sig)}
```
            """
            return info
        
        with gr.Blocks(title="yaapp Gradio Interface") as interface:
            gr.Markdown("# yaapp Function Interface")
            
            with gr.Row():
                with gr.Column(scale=1):
                    func_dropdown = gr.Dropdown(
                        choices=functions,
                        label="Select Function",
                        value=functions[0] if functions else None
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
            
            if functions:
                interface.load(
                    fn=get_function_info,
                    inputs=[func_dropdown],
                    outputs=[function_info]
                )
        
        return interface
    
    def _generate_example_params(self, sig: inspect.Signature) -> str:
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