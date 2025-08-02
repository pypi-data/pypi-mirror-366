"""
Mesh Plugin - Service/Plugin Orchestrator

Starts and manages services/plugins based on configuration.
Provides endpoints to dynamically start new instances with custom configs.
"""

import subprocess
import time
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from yaapp import yaapp
from yaapp.result import Result, Ok, Err


@yaapp.expose("mesh", custom=True)
class Mesh:
    """Service orchestrator for managing microservices."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Mesh with configuration."""
        self._provided_config = config
        self.config = None
        self._running_services = {}  # service_name -> process_info
        self._registry = None  # Will be set if registry integration is enabled
    def expose_to_registry(self, name: str, exposer):
        """Expose Mesh methods to the registry."""
        config_result = self._load_config()
        if config_result.is_err():
            print(f"❌ Mesh: Failed to load config: {config_result.as_error}")
            return
            
        print(f"🕸️ Mesh: Service orchestrator ready")
        print(f"   Services configured: {len(self.config.get('services', []))}")
        
        # Initialize registry integration if enabled
        if self.config.get('registry_integration', False):
            print(f"🔗 Mesh: Registry integration will be initialized on first use")
        
        # Auto-start services if configured
        if self.config.get('auto_start', False):
            print(f"🚀 Mesh: Auto-start will be handled on first service start")
    
    def execute_call(self, function_name: str, **kwargs) -> Result[Any]:
        """Execute Mesh method calls."""
        method = getattr(self, function_name, None)
        if not method:
            return Err(f"Method '{function_name}' not found")
        
        result = method(**kwargs)
        return Ok(result)
    
    async def start_service(self, service_name: str) -> Dict[str, Any]:
        """
        Start a service that's defined in the mesh configuration.
        
        Args:
            service_name: Name of the service to start
        
        Returns:
            Dict with service start status
        """
        if service_name in self._running_services:
            service_info = self._running_services[service_name]
            if self._is_process_running(service_info['process']):
                return {
                    'service': service_name,
                    'status': 'already_running',
                    'pid': service_info['process'].pid,
                    'started_at': service_info['started_at']
                }
            else:
                # Process died, remove from tracking
                del self._running_services[service_name]
        
        # Find service in configuration
        service_config = None
        for config in self.config.get('services', []):
            if config.get('name') == service_name:
                service_config = config
                break
        
        if not service_config:
            return {
                'service': service_name,
                'status': 'error',
                'error': f'Service "{service_name}" not found in mesh configuration. Use start_with_config for dynamic services.'
            }
        
        # Start the service
        launch_result = self._launch_service(service_name, service_config)
        if launch_result.is_err():
            return {
                'service': service_name,
                'status': 'error',
                'error': launch_result.as_error
            }
        
        process_info = launch_result.value
        self._running_services[service_name] = process_info
        
        # Initialize registry if needed and register service
        if self.config.get('registry_integration', False) and service_config.get('register_with_registry', True):
            if not self._registry:
                registry_init_result = await self._init_registry_integration()
                if registry_init_result.is_err():
                    print(f"⚠️ Mesh: Failed to initialize registry: {registry_init_result.as_error}")
            
            if self._registry:
                registry_result = await self._register_service_with_registry(service_name, service_config, process_info)
                if registry_result.is_err():
                    print(f"⚠️ Mesh: Failed to register {service_name} with registry: {registry_result.as_error}")
        
        return {
            'service': service_name,
            'status': 'started',
            'pid': process_info['process'].pid,
            'started_at': process_info['started_at'],
            'command': process_info['command']
        }
    
    async def stop_service(self, service_name: str) -> Dict[str, Any]:
        """
        Stop a running service.
        
        Args:
            service_name: Name of the service to stop
        
        Returns:
            Dict with stop status
        """
        if service_name not in self._running_services:
            return {
                'service': service_name,
                'status': 'not_running'
            }
        
        service_info = self._running_services[service_name]
        process = service_info['process']
        
        if not self._is_process_running(process):
            # Process already dead, just clean up
            del self._running_services[service_name]
            return {
                'service': service_name,
                'status': 'already_stopped'
            }
        
        # Deregister from registry if enabled
        if self._registry:
            deregister_result = await self._deregister_service_from_registry(service_name)
            if deregister_result.is_err():
                print(f"⚠️ Mesh: Failed to deregister {service_name}: {deregister_result.as_error}")
        
        # Stop the process (external call - use try/except)
        try:
            # Graceful shutdown first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                process.kill()
                process.wait()
            
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'error': str(e)
            }
        
        del self._running_services[service_name]
        
        return {
            'service': service_name,
            'status': 'stopped',
            'pid': process.pid
        }
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """
        Restart a service.
        
        Args:
            service_name: Name of the service to restart
        
        Returns:
            Dict with restart status
        """
        # Stop the service first
        stop_result = await self.stop_service(service_name)
        if stop_result.get('status') not in ['stopped', 'not_running']:
            return {
                'service': service_name,
                'status': 'restart_failed',
                'error': f"Failed to stop service: {stop_result.get('error')}"
            }
        
        # Start the service
        start_result = await self.start_service(service_name)
        if start_result.get('status') == 'started':
            return {
                'service': service_name,
                'status': 'restarted',
                'pid': start_result.get('pid')
            }
        else:
            return {
                'service': service_name,
                'status': 'restart_failed',
                'error': f"Failed to start service: {start_result.get('error')}"
            }
    
    async def list_services(self) -> Dict[str, Any]:
        """List all services and their status."""
        services = []
        
        for service_name, service_info in self._running_services.items():
            is_running = self._is_process_running(service_info['process'])
            
            services.append({
                'name': service_name,
                'pid': service_info['process'].pid,
                'status': 'running' if is_running else 'stopped',
                'started_at': service_info['started_at'],
                'command': service_info['command']
            })
        
        return {
            'services': services,
            'total_services': len(services)
        }
    
    def start_with_config(self, service_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new yaapp instance with provided configuration.
        This creates a temporary config file and launches a new yaapp process.
        
        Args:
            service_name: Name for the new service instance
            config_data: Complete yaapp configuration dict (app, plugins, server, etc.)
        
        Returns:
            Dict with service start status
        """
        # Create temporary config file
        config_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )
        
        try:
            # Write config to temporary file
            yaml.dump(config_data, config_file, default_flow_style=False)
            config_file.close()
            
            # Prepare command with config file
            command = [
                'python', '-m', 'yaapp.app',
                '--config', config_file.name
            ]
            
            # Launch the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Track the service
            service_info = {
                'process': process,
                'command': ' '.join(command),
                'started_at': time.time(),
                'config_file': config_file.name
            }
            
            self._running_services[service_name] = service_info
            
            return {
                'service': service_name,
                'status': 'started',
                'pid': process.pid,
                'config_file': config_file.name
            }
            
        except Exception as e:
            # Clean up config file on error
            try:
                Path(config_file.name).unlink()
            except:
                pass
            
            return {
                'service': service_name,
                'status': 'error',
                'error': str(e)
            }
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific service."""
        with self._lock:
            if service_name not in self._running_services:
                return {
                    'service': service_name,
                    'status': 'not_running'
                }
            
            service_info = self._running_services[service_name]
            process = service_info['process']
            
            if self._is_process_running(process):
                return {
                    'service': service_name,
                    'status': 'running',
                    'pid': process.pid,
                    'started_at': service_info['started_at'],
                    'uptime': time.time() - service_info['started_at'],
                    'command': service_info['command'],
                    'config_file': service_info.get('config_file')
                }
            else:
                # Process is dead
                del self._running_services[service_name]
                return {
                    'service': service_name,
                    'status': 'dead',
                    'started_at': service_info['started_at'],
                    'command': service_info['command']
                }
    
    def cleanup_dead_services(self) -> Dict[str, Any]:
        """Clean up dead service processes."""
        # Clean up any dead processes first
        dead_services = []
        for service_name, service_info in list(self._running_services.items()):
            if not self._is_process_running(service_info['process']):
                dead_services.append(service_name)
                del self._running_services[service_name]
        
        return {
            'status': 'cleanup_completed',
            'cleaned_services': dead_services,
            'count': len(dead_services)
        }
    
    def _load_config(self) -> Result[None]:
        """Load Mesh configuration."""
        if self._provided_config:
            self.config = self._provided_config
        else:
            # Get config from yaapp
            if hasattr(yaapp, '_config') and yaapp._config and yaapp._config.discovered_sections:
                self.config = yaapp._config.discovered_sections.get('mesh', {})
            else:
                self.config = {}
        
        # Set defaults
        self.config.setdefault('services', [])
        self.config.setdefault('auto_start', False)
        self.config.setdefault('registry_integration', False)
        
        return Ok(None)
    
    async def _init_registry_integration(self) -> Result[None]:
        """Initialize registry integration."""
        try:
            from yaapp.plugins.registry.plugin import Registry
            self._registry = Registry()
            self._registry._load_config()
            print(f"🔗 Mesh: Registry integration enabled")
            return Ok(None)
        except ImportError:
            return Err("Registry plugin not available")
    
    async def _register_service_with_registry(self, service_name: str, service_config: Dict, process_info: Dict) -> Result[None]:
        """Register a service with the registry."""
        if not self._registry:
            return Err("Registry not initialized")
        
        # Extract port from service config or use default
        port = service_config.get('port', 8000)
        host = service_config.get('host', 'localhost')
        instance_id = f"{service_name}-{process_info['process'].pid}"
        
        metadata = {
            'mesh_managed': True,
            'pid': process_info['process'].pid,
            'started_at': process_info['started_at'],
            'command': process_info['command']
        }
        
        result = await self._registry.register_service(
            service_name=service_name,
            instance_id=instance_id,
            host=host,
            port=port,
            metadata=metadata
        )
        
        if result.get('status') == 'registered':
            print(f"📋 Mesh: Registered {service_name} with registry at {host}:{port}")
            return Ok(None)
        else:
            return Err(f"Failed to register service: {result}")
    
    async def _deregister_service_from_registry(self, service_name: str) -> Result[None]:
        """Deregister a service from the registry."""
        if not self._registry:
            return Ok(None)  # No registry, nothing to do
        
        # Find the instance ID for this service
        if service_name in self._running_services:
            process_info = self._running_services[service_name]
            instance_id = f"{service_name}-{process_info['process'].pid}"
            
            result = await self._registry.deregister_service(service_name, instance_id)
            
            if result.get('status') == 'deregistered':
                print(f"📋 Mesh: Deregistered {service_name} from registry")
                return Ok(None)
            else:
                return Err(f"Failed to deregister service: {result}")
        
        return Ok(None)
    
    def _auto_start_services(self) -> Result[None]:
        """Auto-start configured services."""
        services = self.config.get('services', [])
        if not services:
            return Ok(None)
        
        print(f"🚀 Mesh: Auto-starting {len(services)} services...")
        
        for service_config in services:
            service_name = service_config.get('name')
            if not service_name:
                print(f"⚠️ Mesh: Skipping service with no name: {service_config}")
                continue
            
            result = self.start_service(service_name)
            if result.get('status') == 'started':
                print(f"✅ Mesh: Started {service_name}")
            elif result.get('status') == 'already_running':
                print(f"ℹ️ Mesh: {service_name} already running")
            else:
                print(f"❌ Mesh: Failed to start {service_name}: {result.get('error')}")
        
        return Ok(None)
    
    def _start_configured_services(self):
        """Start all services defined in configuration."""
        if not self.config.get('auto_start', True):
            print("🕸️ Mesh: Auto-start disabled")
            return
        
        services = self.config.get('services', [])
        if not services:
            print("🕸️ Mesh: No services configured to start")
            return
        
        print(f"🕸️ Mesh: Starting {len(services)} configured services...")
        
        for service_config in services:
            service_name = service_config['name']
            try:
                result = self.start_service(service_name)
                if result['status'] == 'started':
                    print(f"   ✅ Started {service_name} (PID: {result['pid']})")
                else:
                    print(f"   ❌ Failed to start {service_name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"   ❌ Error starting {service_name}: {e}")
    
    def _get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific service."""
        for service_config in self.config.get('services', []):
            if service_config['name'] == service_name:
                return service_config
        return None
    
    def _launch_service(self, service_name: str, service_config: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Launch a service process."""
        command = service_config.get('command')
        if not command:
            return Err(f"No command specified for service {service_name}")
        
        # Parse command into list if it's a string
        if isinstance(command, str):
            command_list = command.split()
        else:
            command_list = command
        
        # Set working directory if specified
        cwd = service_config.get('working_directory')
        
        # Set environment variables
        import os
        env = dict(os.environ)
        if 'environment' in service_config:
            env.update(service_config['environment'])
        
        # Launch the process (external call - use try/except)
        try:
            process = subprocess.Popen(
                command_list,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            return Err(f"Failed to launch {service_name}: {e}")
        
        return Ok({
            'process': process,
            'command': ' '.join(command_list),
            'started_at': time.time(),
            'config': service_config
        })
    
    def _is_process_running(self, process: subprocess.Popen) -> bool:
        """Check if a process is still running."""
        return process.poll() is None
    
    def _start_dynamic_service(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a dynamic service (used by start_with_config)."""
        with self._lock:
            if service_name in self._running_services:
                service_info = self._running_services[service_name]
                if self._is_process_running(service_info['process']):
                    return {
                        'service': service_name,
                        'status': 'already_running',
                        'pid': service_info['process'].pid,
                        'started_at': service_info['started_at']
                    }
                else:
                    # Process died, remove from tracking
                    del self._running_services[service_name]
            
            # Start the service
            try:
                process_info = self._launch_service(service_name, service_config)
                self._running_services[service_name] = process_info
                
                return {
                    'service': service_name,
                    'status': 'started',
                    'pid': process_info['process'].pid,
                    'started_at': process_info['started_at'],
                    'command': process_info['command']
                }
                
            except Exception as e:
                return {
                    'service': service_name,
                    'status': 'error',
                    'error': str(e)
                }
    
    def _create_temp_config(self, config_data: Dict[str, Any]) -> Path:
        """Create a temporary configuration file."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            prefix='mesh_config_',
            delete=False
        )
        
        with temp_file as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        return Path(temp_file.name)