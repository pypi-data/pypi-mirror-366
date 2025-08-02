"""
Docker2 plugin using CustomExposer for dynamic Docker API exposure.
Provides hierarchical paths and full Docker API coverage with zero boilerplate.
"""

import docker
import inspect
from typing import Dict, Any, Optional, Callable
from yaapp import yaapp
from yaapp.result import Result, Ok


@yaapp.expose("docker2", custom=True)
class Docker2:
    """Docker plugin using CustomExposer for dynamic API exposure."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Docker2 plugin with cached client."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        
        # Cache Docker client to avoid boilerplate
        self._client = None
        self._client_error = None
        
        # Cache discovered methods to avoid repeated introspection
        self._discovered_methods = {}
        self._introspection_done = False
    
    @property
    def client(self):
        """Lazy-loaded, cached Docker client."""
        if self._client is None and self._client_error is None:
            try:
                self._client = docker.from_env()
                self._client.ping()  # Test connection
                print("✅ Docker2: Connected to Docker daemon")
            except Exception as e:
                self._client_error = str(e)
                print(f"❌ Docker2: Failed to connect to Docker daemon: {e}")
        return self._client
    
    def expose_to_registry(self, name: str, exposer) -> None:
        """
        DISCOVERY PHASE: Dynamically discover and register all Docker methods.
        Creates hierarchical paths like containers/list, images/pull, etc.
        """
        print(f"🔍 Docker2: Discovering Docker API methods...")
        
        if not self.client:
            print(f"❌ Docker2: Cannot discover methods - Docker client unavailable: {self._client_error}")
            return
        
        try:
            # Introspect Docker client to discover all available methods
            self._introspect_docker_api()
            
            # Register all discovered methods with the exposer
            # The exposer should have a way to register proxy functions
            # For now, let's store them in the exposer if it has a register method
            if hasattr(exposer, 'register_proxy_function'):
                for method_path, method_info in self._discovered_methods.items():
                    full_path = f"{name}/{method_path}"
                    proxy_func = self._create_proxy_function(method_path)
                    exposer.register_proxy_function(full_path, proxy_func)
            
            print(f"✅ Docker2: Discovered and registered {len(self._discovered_methods)} methods")
            
            # Show some examples
            example_methods = list(self._discovered_methods.keys())[:5]
            for method in example_methods:
                print(f"   📡 {name}/{method}")
            if len(self._discovered_methods) > 5:
                print(f"   ... and {len(self._discovered_methods) - 5} more methods")
                
        except Exception as e:
            print(f"❌ Docker2: Failed to discover methods: {e}")
    
    def _introspect_docker_api(self) -> None:
        """Introspect Docker client to discover all available methods."""
        if self._introspection_done:
            return
        
        try:
            # Main client methods (ping, version, info, etc.)
            self._discover_object_methods(self.client, "")
            
            # Container collection methods
            if hasattr(self.client, 'containers'):
                self._discover_object_methods(self.client.containers, "containers")
            
            # Image collection methods
            if hasattr(self.client, 'images'):
                self._discover_object_methods(self.client.images, "images")
            
            # Volume collection methods
            if hasattr(self.client, 'volumes'):
                self._discover_object_methods(self.client.volumes, "volumes")
            
            # Network collection methods
            if hasattr(self.client, 'networks'):
                self._discover_object_methods(self.client.networks, "networks")
            
            # Secret collection methods (if available)
            if hasattr(self.client, 'secrets'):
                self._discover_object_methods(self.client.secrets, "secrets")
            
            # Config collection methods (if available)
            if hasattr(self.client, 'configs'):
                self._discover_object_methods(self.client.configs, "configs")
            
            # Service collection methods (if available)
            if hasattr(self.client, 'services'):
                self._discover_object_methods(self.client.services, "services")
            
            # Node collection methods (if available)
            if hasattr(self.client, 'nodes'):
                self._discover_object_methods(self.client.nodes, "nodes")
            
            # Plugin collection methods (if available)
            if hasattr(self.client, 'plugins'):
                self._discover_object_methods(self.client.plugins, "plugins")
            
            self._introspection_done = True
            
        except Exception as e:
            print(f"❌ Docker2: Introspection failed: {e}")
    
    def _discover_object_methods(self, obj: Any, path_prefix: str) -> None:
        """Discover callable methods from an object."""
        try:
            # Get all public methods that are callable
            for attr_name in dir(obj):
                if attr_name.startswith('_'):
                    continue
                
                try:
                    attr = getattr(obj, attr_name)
                    if callable(attr):
                        # Build hierarchical path
                        if path_prefix:
                            method_path = f"{path_prefix}/{attr_name}"
                        else:
                            method_path = attr_name
                        
                        # Store method info
                        self._discovered_methods[method_path] = {
                            'object': obj,
                            'method_name': attr_name,
                            'method': attr,
                            'path': method_path
                        }
                        
                except Exception:
                    # Skip attributes that can't be accessed
                    continue
                    
        except Exception as e:
            print(f"❌ Docker2: Failed to discover methods for {path_prefix}: {e}")
    
    def _create_proxy_function(self, method_path: str) -> Callable:
        """Create a proxy function that will call execute_call with the method path."""
        def proxy_function(**kwargs):
            return self.execute_call(method_path, **kwargs)
        
        # Set some metadata for better introspection
        proxy_function.__name__ = method_path.replace('/', '_')
        proxy_function.__doc__ = f"Docker API method: {method_path}"
        
        return proxy_function
    
    def execute_call(self, function_name: str, **kwargs) -> Result[Any]:
        """
        EXECUTION PHASE: Route function calls to appropriate Docker methods.
        All foreign calls are wrapped in try/catch and return Result objects.
        """
        if not self.client:
            return Result.error(f"Docker daemon not available: {self._client_error}")
        
        if function_name not in self._discovered_methods:
            available = list(self._discovered_methods.keys())[:10]
            return Result.error(f"Method '{function_name}' not found. Available: {available}...")
        
        method_info = self._discovered_methods[function_name]
        method = method_info['method']
        
        try:
            # Call the actual Docker method with provided arguments
            print(f"📡 Docker2: Calling {function_name} with args: {kwargs}")
            
            # Handle different types of method calls
            result = method(**kwargs)
            
            # Convert result to serializable format if needed
            serialized_result = self._serialize_docker_result(result)
            
            print(f"✅ Docker2: {function_name} completed successfully")
            return Ok(serialized_result)
            
        except Exception as e:
            error_msg = f"Docker API call failed for {function_name}: {str(e)}"
            print(f"❌ Docker2: {error_msg}")
            return Result.error(error_msg)
    
    def _serialize_docker_result(self, result: Any) -> Any:
        """
        Convert Docker API results to serializable format.
        Handles Docker objects, lists, and other complex types.
        """
        try:
            # Handle None
            if result is None:
                return None
            
            # Handle basic types
            if isinstance(result, (str, int, float, bool)):
                return result
            
            # Handle lists
            if isinstance(result, list):
                return [self._serialize_docker_result(item) for item in result]
            
            # Handle dictionaries
            if isinstance(result, dict):
                return {k: self._serialize_docker_result(v) for k, v in result.items()}
            
            # Handle Docker container objects
            if hasattr(result, 'attrs') and hasattr(result, 'id'):
                return self._serialize_docker_object(result)
            
            # Handle iterables (but not strings)
            if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                try:
                    return [self._serialize_docker_result(item) for item in result]
                except Exception:
                    pass
            
            # Handle bytes
            if isinstance(result, bytes):
                try:
                    return result.decode('utf-8')
                except UnicodeDecodeError:
                    return f"<binary data: {len(result)} bytes>"
            
            # For other objects, try to convert to string or extract useful info
            if hasattr(result, '__dict__'):
                # Try to extract useful attributes
                obj_dict = {}
                for attr in ['id', 'name', 'status', 'tags', 'short_id']:
                    if hasattr(result, attr):
                        obj_dict[attr] = getattr(result, attr)
                if obj_dict:
                    return obj_dict
            
            # Fallback to string representation
            return str(result)
            
        except Exception as e:
            # If serialization fails, return string representation
            return f"<serialization failed: {str(result)[:100]}>"
    
    def _serialize_docker_object(self, obj: Any) -> Dict[str, Any]:
        """Serialize Docker objects (containers, images, etc.) to dictionaries."""
        try:
            result = {}
            
            # Common attributes for most Docker objects
            for attr in ['id', 'short_id', 'name', 'status', 'tags']:
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    result[attr] = value
            
            # Add attrs if available (contains full object data)
            if hasattr(obj, 'attrs'):
                attrs = obj.attrs
                if isinstance(attrs, dict):
                    # Add some key attributes from attrs
                    for key in ['Created', 'State', 'Config', 'Image', 'Names']:
                        if key in attrs:
                            result[key.lower()] = attrs[key]
            
            # Add labels if available
            if hasattr(obj, 'labels'):
                result['labels'] = obj.labels
            
            # Add ports if available (for containers)
            if hasattr(obj, 'ports'):
                result['ports'] = obj.ports
            
            return result
            
        except Exception as e:
            # Fallback to basic info
            return {
                'id': getattr(obj, 'id', str(obj)),
                'type': type(obj).__name__,
                'error': f"Serialization failed: {str(e)}"
            }
    
    def get_discovered_methods(self) -> Result[Dict[str, Any]]:
        """Get list of all discovered methods (for debugging/inspection)."""
        if not self.client:
            return Result.error(f"Docker daemon not available: {self._client_error}")
        
        try:
            if not self._introspection_done:
                self._introspect_docker_api()
            
            methods_info = {}
            for path, info in self._discovered_methods.items():
                methods_info[path] = {
                    'path': path,
                    'object_type': type(info['object']).__name__,
                    'method_name': info['method_name']
                }
            
            return Ok(methods_info)
            
        except Exception as e:
            return Result.error(f"Failed to get discovered methods: {str(e)}")
    
    def ping(self) -> Result[bool]:
        """Test Docker daemon connectivity (convenience method)."""
        if not self.client:
            return Result.error(f"Docker daemon not available: {self._client_error}")
        
        try:
            result = self.client.ping()
            return Ok(result)
        except Exception as e:
            return Result.error(f"Docker ping failed: {str(e)}")