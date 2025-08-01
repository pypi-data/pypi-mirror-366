"""
Generic API Plugin - Universal API exposure using native discovery mechanisms
"""

import json
import requests
import urllib.parse
from typing import Any, Dict, Optional
from yaapp import yaapp
from yaapp.result import Result, Ok, Err


@yaapp.expose("api", custom=True)
class Api:
    """Universal API plugin that uses native API discovery mechanisms."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with API configuration."""
        # Store config for later loading (config might not be available yet during import)
        self._provided_config = config
        self.config = None
        self.discoverer = None
        self.executor = None
        self._discovered_methods = {}
        
        print(f"🔍 API Plugin: Initializing (config will be loaded during exposure)...")    
    def expose_to_registry(self, name: str, exposer):
        """Discover API endpoints using the API's native mechanisms."""
        try:
            # Load configuration now (during exposure phase)
            self._load_config()
            
            if not self.config:
                print(f"❌ API Plugin: No configuration found for '{name}' section")
                self._discovered_methods = {}
                return
            
            print(f"🔍 API Plugin: Loaded config for {self.config.get('type', 'unknown')} API")
            print(f"   Config keys: {list(self.config.keys())}")
            
            # Create discoverer based on API type
            self.discoverer = self._create_discoverer()
            self.executor = self._create_executor()
            
            # Discover methods using the API's native mechanisms
            self._discovered_methods = self.discoverer.discover()
            
            print(f"✅ API Plugin: Discovered {len(self._discovered_methods)} endpoints")
            
            # Show sample of discovered methods
            sample_methods = list(self._discovered_methods.keys())[:5]
            for method in sample_methods:
                print(f"   📡 {name}/{method}")
            if len(self._discovered_methods) > 5:
                print(f"   ... and {len(self._discovered_methods) - 5} more methods")
                
        except Exception as e:
            print(f"❌ API Plugin: Discovery failed: {e}")
            import traceback
            traceback.print_exc()
            self._discovered_methods = {}
    
    def execute_call(self, function_name: str, **kwargs) -> Result[Any]:
        """Execute API call using the appropriate executor."""
        try:
            print(f"📡 API Plugin: Calling {function_name} with args: {kwargs}")
            
            if function_name not in self._discovered_methods:
                return Err(f"Method '{function_name}' not found in discovered API methods")
            
            result = self.executor.execute(function_name, **kwargs)
            print(f"✅ API Plugin: {function_name} completed successfully")
            return Ok(result)
            
        except Exception as e:
            print(f"❌ API Plugin: {function_name} failed: {e}")
            return Err(str(e))
    
    def get_discovered_methods(self) -> Dict[str, Any]:
        """Get all discovered methods for debugging."""
        return self._discovered_methods
    
    def _create_discoverer(self):
        """Factory for different discovery mechanisms."""
        api_type = self.config.get('type')
        
        if api_type == 'openapi':
            return OpenAPIDiscoverer(self.config)
        elif api_type == 'graphql':
            return GraphQLDiscoverer(self.config)
        elif api_type == 'grpc':
            return GRPCDiscoverer(self.config)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")
    
    def _load_config(self):
        """Load configuration from yaapp config system or provided config."""
        if self._provided_config:
            self.config = self._provided_config
            return
        
        try:
            from yaapp.config import get_config
            yaapp_config = get_config()
            self.config = yaapp_config.discovered_sections.get('api', {})
        except Exception as e:
            print(f"Warning: Could not load config from yaapp: {e}")
            self.config = {}
    
    def _create_executor(self):
        """Factory for different execution mechanisms."""
        api_type = self.config.get('type')
        
        if api_type == 'openapi':
            return OpenAPIExecutor(self.config, self.discoverer)
        elif api_type == 'graphql':
            return GraphQLExecutor(self.config, self.discoverer)
        elif api_type == 'grpc':
            return GRPCExecutor(self.config, self.discoverer)
        else:
            raise ValueError(f"Unsupported executor type: {api_type}")


class OpenAPIDiscoverer:
    """Discovers API endpoints from OpenAPI/Swagger specifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.spec_url = config['spec_url']
        self.spec = None
    
    def discover(self) -> Dict[str, Any]:
        """Fetch and parse OpenAPI specification."""
        print(f"🔍 OpenAPI: Fetching specification from {self.spec_url}")
        
        try:
            # Fetch OpenAPI spec
            response = requests.get(self.spec_url, timeout=30)
            response.raise_for_status()
            
            # Parse YAML or JSON
            if self.spec_url.endswith('.yaml') or self.spec_url.endswith('.yml'):
                import yaml
                self.spec = yaml.safe_load(response.text)
            else:
                self.spec = response.json()
            
            print(f"✅ OpenAPI: Loaded specification v{self.spec.get('swagger', self.spec.get('openapi', 'unknown'))}")
            
            # Parse paths into hierarchical methods
            methods = {}
            for path, path_item in self.spec.get('paths', {}).items():
                for http_method, operation in path_item.items():
                    if http_method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                        operation_id = self._generate_operation_id(path, http_method, operation)
                        methods[operation_id] = {
                            'path': path,
                            'method': http_method.upper(),
                            'operation': operation,
                            'parameters': operation.get('parameters', []),
                            'summary': operation.get('summary', ''),
                            'description': operation.get('description', ''),
                            'tags': operation.get('tags', [])
                        }
            
            return methods
            
        except Exception as e:
            print(f"❌ OpenAPI: Failed to fetch specification: {e}")
            raise
    
    def _generate_operation_id(self, path: str, method: str, operation: Dict) -> str:
        """Convert OpenAPI path to hierarchical command structure."""
        # Generate from path - expose endpoints exactly as they are
        # /containers/json GET -> containers/json
        # /containers/{id}/json GET -> containers/inspect (to avoid collision)
        # /containers/{id}/start POST -> containers/start  
        # /images/search GET -> images/search
        
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        has_path_params = '{' in path
        
        if len(path_parts) == 0:
            return self._method_to_action(method.lower())
        elif len(path_parts) == 1:
            return path_parts[0]
        else:
            # For nested paths, use the full path structure
            endpoint = "/".join(path_parts)
            
            # Handle special cases to avoid collisions
            if has_path_params and endpoint.endswith('/json'):
                # /containers/{id}/json -> containers/inspect
                # /images/{id}/json -> images/inspect  
                base = endpoint.replace('/json', '')
                return f"{base}/inspect"
            
            return endpoint
    
    def _convert_operation_id(self, operation_id: str) -> str:
        """Convert camelCase operationId to hierarchical path."""
        # ContainerList -> containers/list
        # ImageBuild -> images/build
        import re
        
        # Split camelCase
        parts = re.findall(r'[A-Z][a-z]*', operation_id)
        if len(parts) >= 2:
            resource = parts[0].lower() + 's'  # Make plural
            action = parts[1].lower()
            return f"{resource}/{action}"
        else:
            return operation_id.lower()
    
    def _method_to_action(self, method: str) -> str:
        """Convert HTTP method to action name."""
        method_map = {
            'get': 'list',
            'post': 'create', 
            'put': 'update',
            'patch': 'update',
            'delete': 'remove',
            'head': 'head',
            'options': 'options'
        }
        return method_map.get(method, method)


class OpenAPIExecutor:
    """Executes API calls based on OpenAPI specification."""
    
    def __init__(self, config: Dict[str, Any], discoverer: OpenAPIDiscoverer):
        self.config = config
        self.discoverer = discoverer
        self.base_url = config['base_url']
        self.transport = config.get('transport', 'http')
        self.socket_path = config.get('socket_path')
    
    def execute(self, function_name: str, **kwargs) -> Any:
        """Execute an API call."""
        method_info = self.discoverer._discovered_methods[function_name]
        
        # Build URL with path parameters
        url = self._build_url(method_info['path'], kwargs)
        
        # Categorize parameters
        path_params, query_params, body_params = self._categorize_params(method_info, kwargs)
        
        # Make HTTP request
        response = self._make_request(
            method=method_info['method'],
            url=url,
            params=query_params,
            json=body_params if body_params else None
        )
        
        return self._process_response(response)
    
    def _build_url(self, path_template: str, params: Dict) -> str:
        """Build URL with path parameter substitution."""
        url = path_template
        for param_name, param_value in params.items():
            if f'{{{param_name}}}' in url:
                url = url.replace(f'{{{param_name}}}', str(param_value))
        
        return self.base_url + url
    
    def _categorize_params(self, method_info: Dict, kwargs: Dict) -> tuple:
        """Categorize parameters into path, query, and body parameters."""
        path_params = {}
        query_params = {}
        body_params = {}
        
        # Get parameter definitions from OpenAPI spec
        param_definitions = {p['name']: p for p in method_info['parameters']}
        
        for param_name, param_value in kwargs.items():
            if param_name in param_definitions:
                param_def = param_definitions[param_name]
                param_in = param_def.get('in', 'query')
                
                if param_in == 'path':
                    path_params[param_name] = param_value
                elif param_in == 'query':
                    query_params[param_name] = param_value
                elif param_in == 'body':
                    body_params[param_name] = param_value
                else:
                    # Default to query parameter
                    query_params[param_name] = param_value
            else:
                # Unknown parameter, default to query
                query_params[param_name] = param_value
        
        return path_params, query_params, body_params
    
    def _make_request(self, method: str, url: str, params: Dict = None, json: Dict = None) -> requests.Response:
        """Make HTTP request with appropriate transport."""
        if self.transport == 'unix_socket' and self.socket_path:
            # Use Unix socket for Docker API
            import requests_unixsocket
            session = requests_unixsocket.Session()
            # Convert URL to unix socket format
            socket_url = f"http+unix://{self.socket_path.replace('/', '%2F')}{url}"
            response = session.request(method, socket_url, params=params, json=json)
        else:
            # Regular HTTP request
            response = requests.request(method, url, params=params, json=json)
        
        response.raise_for_status()
        return response
    
    def _process_response(self, response: requests.Response) -> Any:
        """Process API response."""
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            return response.json()
        elif 'text/' in content_type:
            return response.text
        else:
            return response.content


# Placeholder classes for future API types
class GraphQLDiscoverer:
    """Discovers GraphQL API using introspection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        raise NotImplementedError("GraphQL discovery not yet implemented")


class GraphQLExecutor:
    """Executes GraphQL queries."""
    
    def __init__(self, config: Dict[str, Any], discoverer):
        self.config = config
        raise NotImplementedError("GraphQL execution not yet implemented")


class GRPCDiscoverer:
    """Discovers gRPC services using reflection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        raise NotImplementedError("gRPC discovery not yet implemented")


class GRPCExecutor:
    """Executes gRPC calls."""
    
    def __init__(self, config: Dict[str, Any], discoverer):
        self.config = config
        raise NotImplementedError("gRPC execution not yet implemented")