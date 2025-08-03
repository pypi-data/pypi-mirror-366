"""Registry Plugin - Service Registry for Microservices

Simple service registry that tracks services and their instances.
Services can register, deregister, and discover other services.
"""

from typing import Dict, List, Any, Optional
from yaapp import expose


@expose(name='registry')
class Registry:
    """Service registry for microservice discovery."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Registry with configuration."""
        self._provided_config = config
        self.config = None
        self.yaapp = None  # Will be set by the main app when registered
        self._services = {}  # service_name -> {instances: [], metadata: {}}
        
        # Load configuration
        self._load_config()
        print(f"📋 Registry: Service registry ready")
    
    async def register_service(self, service_name: str, instance_id: str, host: str, port: int,
                        metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Register a service instance.
        
        Args:
            service_name: Name of the service
            instance_id: Unique identifier for this instance
            host: Host where service is running
            port: Port where service is listening
            metadata: Additional service metadata (optional)
        
        Returns:
            Registration result
        """
        instance_data = {
            'instance_id': instance_id,
            'service_name': service_name,
            'host': host,
            'port': port,
            'metadata': metadata or {}
        }
        
        # Add to services tracking
        if service_name not in self._services:
            self._services[service_name] = {
                'instances': [],
                'metadata': {}
            }
        
        # Remove existing instance if re-registering
        self._services[service_name]['instances'] = [
            inst for inst in self._services[service_name]['instances'] 
            if inst['instance_id'] != instance_id
        ]
        
        # Add new instance
        self._services[service_name]['instances'].append(instance_data)
        
        return {
            'status': 'registered',
            'service_name': service_name,
            'instance_id': instance_id
        }
    
    async def deregister_service(self, service_name: str, instance_id: str) -> Dict[str, Any]:
        """
        Deregister a service instance.
        
        Args:
            service_name: Name of the service
            instance_id: Instance to deregister
        
        Returns:
            Deregistration result
        """
        if service_name not in self._services:
            return {
                'status': 'service_not_found',
                'service_name': service_name
            }
        
        # Find and remove the instance
        original_count = len(self._services[service_name]['instances'])
        self._services[service_name]['instances'] = [
            inst for inst in self._services[service_name]['instances']
            if inst['instance_id'] != instance_id
        ]
        
        if len(self._services[service_name]['instances']) == original_count:
            return {
                'status': 'instance_not_found',
                'service_name': service_name,
                'instance_id': instance_id
            }
        
        # Remove service if no instances left
        if not self._services[service_name]['instances']:
            del self._services[service_name]
        
        return {
            'status': 'deregistered',
            'service_name': service_name,
            'instance_id': instance_id
        }
    
    async def discover_service(self, service_name: str) -> Dict[str, Any]:
        """
        Discover instances of a service.
        
        Args:
            service_name: Name of service to discover
        
        Returns:
            Service instances
        """
        if service_name not in self._services:
            return {
                'service_name': service_name,
                'instances': [],
                'total_instances': 0
            }
        
        service_data = self._services[service_name]
        instances = service_data['instances']
        
        return {
            'service_name': service_name,
            'instances': instances,
            'total_instances': len(instances),
            'metadata': service_data['metadata']
        }
    
    async def list_services(self) -> Dict[str, Any]:
        """
        List all registered services.
        
        Returns:
            All services and their instances
        """
        services = []
        
        for service_name, service_data in self._services.items():
            instances = service_data['instances']
            
            services.append({
                'service_name': service_name,
                'instance_count': len(instances),
                'instances': instances,
                'metadata': service_data['metadata']
            })
        
        return {
            'services': services,
            'total_services': len(services),
            'total_instances': sum(len(s['instances']) for s in services)
        }
    
    def _load_config(self):
        """Load Registry configuration."""
        if self._provided_config:
            self.config = self._provided_config
        else:
            # Get config from yaapp if available
            if self.yaapp and hasattr(self.yaapp, '_config') and self.yaapp._config:
                self.config = self.yaapp._config.discovered_sections.get('registry', {})
            else:
                self.config = {}