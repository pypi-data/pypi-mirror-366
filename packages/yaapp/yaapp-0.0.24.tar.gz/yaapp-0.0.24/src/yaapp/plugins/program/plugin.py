"""
Program Plugin - YAML-based Service Orchestrator

Executes YAML-defined programs that can invoke services across meshes.
Supports service calls, expectations, and Python plugin invocations.
"""

import asyncio
import aiohttp
import yaml
from typing import Dict, List, Any, Optional
from yaapp import yaapp
from yaapp.result import Result, Ok, Err


@yaapp.expose("program", custom=True)
class Program:
    """YAML-based program executor for mesh orchestration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Program with configuration."""
        self._provided_config = config
        self.config = None
        self._services = {}  # service_name -> service_info
        self._python_plugins = {}  # plugin_name -> plugin_function
    
    def expose_to_registry(self, name: str, exposer):
        """Expose Program methods to the registry."""
        config_result = self._load_config()
        if config_result.is_err():
            print(f"❌ Program: Failed to load config: {config_result.as_error}")
            return
            
        print(f"📋 Program: YAML-based orchestrator ready")
        print(f"   Services configured: {len(self.config.get('services', {}))}")
        print(f"   Program code loaded: {'Yes' if self.config.get('code') else 'No'}")
        
        # Load service registry
        self._load_services()
        
        # Load Python plugins
        self._load_python_plugins()
    
    def execute_call(self, function_name: str, **kwargs) -> Result[Any]:
        """Execute Program method calls."""
        method = getattr(self, function_name, None)
        if not method:
            return Err(f"Method '{function_name}' not found")
        
        # Only use try/catch for foreign functions (asyncio.run)
        if asyncio.iscoroutinefunction(method):
            try:
                result = asyncio.run(method(**kwargs))
            except Exception as e:
                return Err(f"Async execution failed: {str(e)}")
        else:
            result = method(**kwargs)
        
        return Ok(result)
    
    async def run_program(self) -> Result[Dict[str, Any]]:
        """
        Execute the YAML program defined in separate program file.
        
        Returns:
            Result containing execution results
        """
        program_file = self.config.get('program_file', 'program.yaml')
        
        # Load program from separate file
        program_result = self._load_program_file(program_file)
        if program_result.is_err():
            return program_result
        
        program_code = program_result.unwrap()
        
        # Execute the program
        results = await self._execute_program(program_code)
        if results.is_err():
            return results
        
        return Ok({
            'status': 'completed',
            'results': results.unwrap()
        })
    
    async def invoke_service(self, service_name: str, endpoint: str, data: Dict[str, Any] = None) -> Result[Dict[str, Any]]:
        """
        Invoke a service endpoint.
        
        Args:
            service_name: Name of the service
            endpoint: Endpoint/method name
            data: Data to send to the endpoint
        
        Returns:
            Result containing service response
        """
        if service_name not in self._services:
            return Err(f'Service "{service_name}" not found in registry')
        
        service_info = self._services[service_name]
        url = f"{service_info['url']}/_rpc"
        
        payload = {
            'function': endpoint,
            'args': data or {}
        }
        
        # Only use try/catch for foreign functions (aiohttp)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
        except Exception as e:
            return Err(f"HTTP request failed: {str(e)}")
        
        return Ok({
            'status': 'success',
            'service': service_name,
            'endpoint': endpoint,
            'response': result
        })
    
    def call_python_plugin(self, plugin_name: str, **kwargs) -> Result[Dict[str, Any]]:
        """
        Call a Python plugin function.
        
        Args:
            plugin_name: Name of the Python plugin
            **kwargs: Arguments to pass to the plugin
        
        Returns:
            Result containing plugin result
        """
        if plugin_name not in self._python_plugins:
            return Err(f'Python plugin "{plugin_name}" not found')
        
        plugin_func = self._python_plugins[plugin_name]
        
        # Only use try/catch for foreign functions (user plugin code)
        try:
            result = plugin_func(**kwargs)
        except Exception as e:
            return Err(f"Plugin execution failed: {str(e)}")
        
        return Ok({
            'status': 'success',
            'plugin': plugin_name,
            'result': result
        })
    
    async def _execute_program(self, program_code: Dict[str, Any]) -> Result[List[Dict[str, Any]]]:
        """Execute the parsed YAML program code."""
        results = []
        
        # Handle different program structures
        if isinstance(program_code, dict):
            for step_name, step_config in program_code.items():
                step_result = await self._execute_step(step_name, step_config)
                if step_result.is_err():
                    return step_result  # Propagate error
                results.append(step_result.unwrap())
        elif isinstance(program_code, list):
            for i, step_config in enumerate(program_code):
                step_result = await self._execute_step(f"step_{i}", step_config)
                if step_result.is_err():
                    return step_result  # Propagate error
                results.append(step_result.unwrap())
        else:
            return Err(f"Invalid program code structure: expected dict or list, got {type(program_code)}")
        
        return Ok(results)
    
    async def _execute_step(self, step_name: str, step_config: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Execute a single program step."""
        step_result = {
            'step': step_name,
            'type': 'unknown',
            'status': 'pending'
        }
        
        # Handle 'invoke' step
        if 'invoke' in step_config:
            step_result['type'] = 'invoke'
            invoke_result = await self._handle_invoke(step_config['invoke'])
            if invoke_result.is_err():
                return Err(f"Step '{step_name}' invoke failed: {invoke_result.as_error}")
            
            invoke_data = invoke_result.unwrap()
            step_result.update(invoke_data)
            
            # Handle 'expected' validation if present
            if 'expected' in step_config:
                expected_result = self._handle_expected(invoke_data, step_config['expected'])
                if expected_result.is_err():
                    return expected_result
                
                validation_data = expected_result.unwrap()
                step_result['validation'] = validation_data
                if validation_data['status'] != 'passed':
                    step_result['status'] = 'failed'
                else:
                    step_result['status'] = 'success'
            else:
                step_result['status'] = 'success'
        
        # Handle 'call' step (Python plugin)
        elif 'call' in step_config:
            step_result['type'] = 'call'
            call_result = self.call_python_plugin(**step_config['call'])
            if call_result.is_err():
                return Err(f"Step '{step_name}' call failed: {call_result.as_error}")
            
            call_data = call_result.unwrap()
            step_result.update(call_data)
            step_result['status'] = call_data['status']
        
        # Handle direct service calls (service_name: {endpoint: data})
        else:
            # Assume it's a direct service call
            for service_name, service_calls in step_config.items():
                if service_name in self._services:
                    step_result['type'] = 'service_call'
                    step_result['service'] = service_name
                    
                    for endpoint, data in service_calls.items():
                        invoke_result = await self.invoke_service(service_name, endpoint, data)
                        if invoke_result.is_err():
                            return Err(f"Step '{step_name}' service call failed: {invoke_result.as_error}")
                        
                        invoke_data = invoke_result.unwrap()
                        step_result.update(invoke_data)
                        step_result['status'] = invoke_data['status']
                        break  # Handle first endpoint for now
                    break
            else:
                return Err(f"Unknown step configuration: {step_config}")
        
        return Ok(step_result)
    
    async def _handle_invoke(self, invoke_config: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Handle 'invoke' step configuration."""
        # invoke_config should be: {service_name: {endpoint: data}}
        for service_name, service_calls in invoke_config.items():
            for endpoint, data in service_calls.items():
                return await self.invoke_service(service_name, endpoint, data)
        
        return Err('Invalid invoke configuration')
    
    def _handle_expected(self, invoke_result: Dict[str, Any], expected_config: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Handle 'expected' validation."""
        validation_result = {
            'status': 'passed',
            'checks': [],
            'failed_checks': []
        }
        
        if invoke_result.get('status') != 'success':
            validation_result['status'] = 'failed'
            validation_result['failed_checks'].append({
                'field': 'status',
                'expected': 'success',
                'actual': invoke_result.get('status'),
                'reason': 'Service call failed'
            })
            return Ok(validation_result)
        
        response = invoke_result.get('response', {})
        
        # Check each expected field
        for field_path, expected_value in expected_config.items():
            check_result = self._check_field(response, field_path, expected_value)
            if check_result.is_err():
                return check_result
            
            check_data = check_result.unwrap()
            validation_result['checks'].append(check_data)
            
            if not check_data['passed']:
                validation_result['status'] = 'failed'
                validation_result['failed_checks'].append(check_data)
        
        return Ok(validation_result)
    
    def _check_field(self, response: Dict[str, Any], field_path: str, expected_value: Any) -> Result[Dict[str, Any]]:
        """Check a specific field in the response."""
        # Navigate nested fields using dot notation
        current = response
        for part in field_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return Ok({
                    'field': field_path,
                    'expected': expected_value,
                    'actual': None,
                    'passed': False,
                    'reason': f'Field "{field_path}" not found in response'
                })
        
        # Compare values
        if current == expected_value:
            return Ok({
                'field': field_path,
                'expected': expected_value,
                'actual': current,
                'passed': True
            })
        else:
            return Ok({
                'field': field_path,
                'expected': expected_value,
                'actual': current,
                'passed': False,
                'reason': f'Value mismatch'
            })
    
    def _load_program_file(self, program_file: str) -> Result[Dict[str, Any]]:
        """Load program from separate YAML file."""
        from pathlib import Path
        
        program_path = Path(program_file)
        if not program_path.exists():
            return Err(f"Program file not found: {program_file}")
        
        # Only use try/catch for foreign functions (file I/O and YAML parsing)
        try:
            with open(program_path, 'r') as f:
                program_data = yaml.safe_load(f)
        except Exception as e:
            return Err(f"Failed to load program file {program_file}: {str(e)}")
        
        if not isinstance(program_data, dict):
            return Err(f"Program file must contain a YAML dictionary, got {type(program_data)}")
        
        return Ok(program_data)
    
    def _load_config(self) -> Result[None]:
        """Load Program configuration."""
        if self._provided_config:
            self.config = self._provided_config
        else:
            # Get config from yaapp
            if hasattr(yaapp, '_config') and yaapp._config and yaapp._config.discovered_sections:
                self.config = yaapp._config.discovered_sections.get('program', {})
            else:
                self.config = {}
        
        # Set defaults
        self.config.setdefault('program_file', 'program.yaml')
        self.config.setdefault('python_plugins', {})
        
        return Ok(None)
    
    def _load_services(self):
        """Load service registry from program file."""
        program_file = self.config.get('program_file', 'program.yaml')
        
        # Load program file to get services
        program_result = self._load_program_file(program_file)
        if program_result.is_err():
            print(f"⚠️ Program: Failed to load services from {program_file}: {program_result.as_error}")
            return
        
        program_data = program_result.unwrap()
        services_config = program_data.get('services', {})
        
        for service_name, service_info in services_config.items():
            if isinstance(service_info, str):
                # Simple URL format
                self._services[service_name] = {
                    'url': service_info,
                    'type': 'http'
                }
            elif isinstance(service_info, dict):
                # Detailed service info
                self._services[service_name] = service_info
            
        print(f"📋 Program: Loaded {len(self._services)} services")
        for name, info in self._services.items():
            print(f"   - {name}: {info.get('url', 'unknown')}")
    
    def _load_python_plugins(self):
        """Load Python plugin functions from config."""
        plugins_config = self.config.get('python_plugins', {})
        
        for plugin_name, plugin_config in plugins_config.items():
            try:
                # Import and get the function
                module_path = plugin_config.get('module')
                function_name = plugin_config.get('function')
                
                if module_path and function_name:
                    # Dynamic import
                    import importlib
                    module = importlib.import_module(module_path)
                    plugin_func = getattr(module, function_name)
                    
                    self._python_plugins[plugin_name] = plugin_func
                    print(f"📋 Program: Loaded Python plugin '{plugin_name}' from {module_path}.{function_name}")
                
            except Exception as e:
                print(f"⚠️ Program: Failed to load Python plugin '{plugin_name}': {e}")
        
        print(f"📋 Program: Loaded {len(self._python_plugins)} Python plugins")