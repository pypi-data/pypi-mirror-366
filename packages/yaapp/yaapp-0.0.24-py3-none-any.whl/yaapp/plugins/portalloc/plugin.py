"""
PortAlloc Plugin - Microservice Port Allocation Manager

Manages port allocation for microservices by scanning localhost for available ports
in a specified range and tracking allocations.
"""

import socket
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from yaapp import yaapp
from yaapp.result import Result, Ok, Err


@yaapp.expose("portalloc", custom=True)
class PortAlloc:
    """Port allocation manager for microservices."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize PortAlloc with configuration."""
        self._provided_config = config
        self.config = None
        self._allocations = {}  # port -> {service, allocated_at, lease_time}
        self._persistence_file = None
        
    def expose_to_registry(self, name: str, exposer):
        """Expose PortAlloc methods to the registry."""
        try:
            self._load_config()
            self._load_allocations()
            print(f"🔌 PortAlloc: Port allocation service ready")
            print(f"   Port range: {self.config.get('port_range', '8000-9000')}")
            print(f"   Host: {self.config.get('host', 'localhost')}")
            
        except Exception as e:
            print(f"❌ PortAlloc: Failed to initialize: {e}")
            import traceback
            traceback.print_exc()
    
    def execute_call(self, function_name: str, **kwargs) -> Result[Any]:
        """Execute PortAlloc method calls."""
        try:
            method = getattr(self, function_name, None)
            if not method:
                return Err(f"Method '{function_name}' not found")
            
            result = method(**kwargs)
            return Ok(result)
            
        except Exception as e:
            return Err(str(e))
    
    def allocate_port(self, service_name: str, preferred_port: Optional[int] = None, 
                     lease_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Allocate an available port for a service.
        
        Args:
            service_name: Name of the service requesting the port
            preferred_port: Preferred port number (optional)
            lease_time: Lease time in seconds (optional, uses config default)
        
        Returns:
            Dict with allocated port info or error
        """
        # Clean up expired allocations first
        self._cleanup_expired()
        
        port_range = self._parse_port_range()
        host = self.config.get('host', 'localhost')
        default_lease = self.config.get('default_lease_time', 3600)  # 1 hour default
        lease_time = lease_time or default_lease
        
        # Check if service already has a port allocated
        existing_port = self._find_service_port(service_name)
        if existing_port:
            # Extend the lease
            self._allocations[existing_port]['allocated_at'] = time.time()
            self._allocations[existing_port]['lease_time'] = lease_time
            self._save_allocations()
            return {
                'port': existing_port,
                'service': service_name,
                'status': 'renewed',
                'lease_expires_at': time.time() + lease_time
            }
        
        # Try preferred port first if specified
        if preferred_port and self._is_port_available(host, preferred_port):
            if preferred_port in port_range:
                port = preferred_port
            else:
                # Preferred port outside range, scan for available
                port = self._scan_for_available_port(host, port_range)
        else:
            # Scan for any available port in range
            port = self._scan_for_available_port(host, port_range)
        
        if not port:
            return {
                'error': f'No available ports in range {port_range[0]}-{port_range[-1]}',
                'allocated_ports': len(self._allocations),
                'total_range': len(port_range)
            }
        
        # Allocate the port
        allocation = {
            'service': service_name,
            'allocated_at': time.time(),
            'lease_time': lease_time,
            'host': host
        }
        
        self._allocations[port] = allocation
        self._save_allocations()
        
        return {
            'port': port,
            'service': service_name,
            'status': 'allocated',
            'lease_expires_at': time.time() + lease_time,
            'host': host
        }
    
    def release_port(self, port_or_service: str) -> Dict[str, Any]:
        """
        Release a port allocation.
        
        Args:
            port_or_service: Port number or service name to release
        
        Returns:
            Dict with release status
        """
        # Try to parse as port number first
        try:
            port = int(port_or_service)
            if port in self._allocations:
                service = self._allocations[port]['service']
                del self._allocations[port]
                self._save_allocations()
                return {
                    'status': 'released',
                    'port': port,
                    'service': service
                }
            else:
                return {'error': f'Port {port} not allocated'}
        except ValueError:
            # Treat as service name
            service_name = port_or_service
            port = self._find_service_port(service_name)
            if port:
                del self._allocations[port]
                self._save_allocations()
                return {
                    'status': 'released',
                    'port': port,
                    'service': service_name
                }
            else:
                return {'error': f'Service "{service_name}" has no allocated port'}
    
    def list_allocations(self) -> Dict[str, Any]:
        """List all current port allocations."""
        self._cleanup_expired()
        
        allocations = []
        for port, info in self._allocations.items():
            expires_at = info['allocated_at'] + info['lease_time']
            allocations.append({
                'port': port,
                'service': info['service'],
                'allocated_at': info['allocated_at'],
                'expires_at': expires_at,
                'time_remaining': max(0, expires_at - time.time()),
                'host': info.get('host', 'localhost')
            })
        
        return {
            'allocations': sorted(allocations, key=lambda x: x['port']),
            'total_allocated': len(allocations),
            'port_range': self.config.get('port_range', '8000-9000')
        }
    
    def scan_ports(self, start_port: Optional[int] = None, end_port: Optional[int] = None) -> Dict[str, Any]:
        """
        Scan port range for availability.
        
        Args:
            start_port: Start of range (optional, uses config)
            end_port: End of range (optional, uses config)
        
        Returns:
            Dict with scan results
        """
        if start_port and end_port:
            port_range = list(range(start_port, end_port + 1))
        else:
            port_range = self._parse_port_range()
        
        host = self.config.get('host', 'localhost')
        available = []
        allocated = []
        unavailable = []
        
        for port in port_range:
            if port in self._allocations:
                allocated.append(port)
            elif self._is_port_available(host, port):
                available.append(port)
            else:
                unavailable.append(port)
        
        return {
            'range': f"{port_range[0]}-{port_range[-1]}",
            'total_ports': len(port_range),
            'available': available,
            'allocated_by_portalloc': allocated,
            'unavailable': unavailable,
            'summary': {
                'available_count': len(available),
                'allocated_count': len(allocated),
                'unavailable_count': len(unavailable)
            }
        }
    
    def check_port(self, port: int) -> Dict[str, Any]:
        """Check if a specific port is available."""
        host = self.config.get('host', 'localhost')
        
        if port in self._allocations:
            allocation = self._allocations[port]
            return {
                'port': port,
                'status': 'allocated_by_portalloc',
                'service': allocation['service'],
                'allocated_at': allocation['allocated_at'],
                'expires_at': allocation['allocated_at'] + allocation['lease_time']
            }
        elif self._is_port_available(host, port):
            return {
                'port': port,
                'status': 'available',
                'host': host
            }
        else:
            return {
                'port': port,
                'status': 'unavailable',
                'host': host,
                'note': 'Port is in use by another process'
            }
    
    def cleanup_expired(self) -> Dict[str, Any]:
        """Manually trigger cleanup of expired allocations."""
        before_count = len(self._allocations)
        expired = self._cleanup_expired()
        after_count = len(self._allocations)
        
        return {
            'expired_allocations': expired,
            'cleaned_count': before_count - after_count,
            'remaining_allocations': after_count
        }
    
    def _load_config(self):
        """Load PortAlloc configuration."""
        if self._provided_config:
            self.config = self._provided_config
        else:
            # Get config from yaapp
            if hasattr(yaapp, '_config') and yaapp._config and yaapp._config.discovered_sections:
                self.config = yaapp._config.discovered_sections.get('portalloc', {})
            else:
                self.config = {}
        
        # Set defaults
        self.config.setdefault('port_range', '8000-9000')
        self.config.setdefault('host', 'localhost')
        self.config.setdefault('default_lease_time', 3600)
        self.config.setdefault('persistence_file', 'portalloc_allocations.json')
        
        # Set persistence file path
        self._persistence_file = Path(self.config['persistence_file'])
    
    def _parse_port_range(self) -> List[int]:
        """Parse port range from config."""
        port_range = self.config.get('port_range', '8000-9000')
        if '-' in port_range:
            start, end = map(int, port_range.split('-'))
            return list(range(start, end + 1))
        else:
            # Single port
            return [int(port_range)]
    
    def _is_port_available(self, host: str, port: int) -> bool:
        """Check if a port is available by trying to bind to it."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, port))
                return True
        except (socket.error, OSError):
            return False
    
    def _scan_for_available_port(self, host: str, port_range: List[int]) -> Optional[int]:
        """Scan for the first available port in range."""
        for port in port_range:
            if port not in self._allocations and self._is_port_available(host, port):
                return port
        return None
    
    def _find_service_port(self, service_name: str) -> Optional[int]:
        """Find the port allocated to a service."""
        for port, allocation in self._allocations.items():
            if allocation['service'] == service_name:
                return port
        return None
    
    def _cleanup_expired(self) -> List[Dict[str, Any]]:
        """Clean up expired allocations."""
        current_time = time.time()
        expired = []
        
        for port in list(self._allocations.keys()):
            allocation = self._allocations[port]
            expires_at = allocation['allocated_at'] + allocation['lease_time']
            
            if current_time > expires_at:
                expired.append({
                    'port': port,
                    'service': allocation['service'],
                    'expired_at': expires_at
                })
                del self._allocations[port]
        
        if expired:
            self._save_allocations()
        
        return expired
    
    def _load_allocations(self):
        """Load allocations from persistence file."""
        if self._persistence_file and self._persistence_file.exists():
            try:
                with open(self._persistence_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    self._allocations = {int(k): v for k, v in data.items()}
                print(f"🔌 PortAlloc: Loaded {len(self._allocations)} allocations from {self._persistence_file}")
            except Exception as e:
                print(f"⚠️ PortAlloc: Failed to load allocations: {e}")
                self._allocations = {}
    
    def _save_allocations(self):
        """Save allocations to persistence file."""
        if self._persistence_file:
            try:
                # Ensure directory exists
                self._persistence_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self._persistence_file, 'w') as f:
                    json.dump(self._allocations, f, indent=2)
            except Exception as e:
                print(f"⚠️ PortAlloc: Failed to save allocations: {e}")