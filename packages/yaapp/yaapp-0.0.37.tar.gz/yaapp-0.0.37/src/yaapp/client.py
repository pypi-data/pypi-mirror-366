"""
yaapp client for connecting to remote yaapp servers.
"""

import json
from typing import Optional, Dict, Any, List

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class YaappClient:
    """Client for connecting to remote yaapp servers."""
    
    def __init__(self, server_url: str, token: Optional[str] = None):
        """Initialize client with server URL and optional token."""
        if not HAS_REQUESTS:
            raise ImportError("requests library required for client functionality")
        
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def get_help(self) -> str:
        """Get help information from remote server."""
        try:
            response = self.session.get(f"{self.server_url}/_describe")
            response.raise_for_status()
            
            data = response.json()
            
            # Format help output
            help_text = f"Remote yaapp server: {self.server_url}\n\n"
            help_text += "Available commands:\n"
            
            if 'functions' in data:
                for func_name, func_info in data['functions'].items():
                    description = func_info.get('description', 'No description')
                    help_text += f"  {func_name:<20} {description}\n"
            
            return help_text
            
        except requests.RequestException as e:
            return f"Error connecting to server: {e}"
        except Exception as e:
            return f"Error getting help: {e}"
    
    def execute_command(self, command: str, args: List[str]) -> str:
        """Execute a command on the remote server."""
        try:
            # Parse args into parameters
            params = self._parse_args(args)
            
            # Make RPC call
            payload = {
                'function': command,
                'args': params
            }
            
            response = self.session.post(
                f"{self.server_url}/_rpc",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                return f"Error: {result['error']}"
            
            if 'result' in result:
                if isinstance(result['result'], (dict, list)):
                    return json.dumps(result['result'], indent=2)
                else:
                    return str(result['result'])
            
            return "Command executed successfully"
            
        except requests.RequestException as e:
            return f"Error connecting to server: {e}"
        except Exception as e:
            return f"Error executing command: {e}"
    
    def _parse_args(self, args: List[str]) -> Dict[str, Any]:
        """Parse command line arguments into parameters."""
        params = {}
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                # Named parameter
                key = arg[2:].replace('-', '_')
                
                if i + 1 < len(args) and not args[i + 1].startswith('--'):
                    # Has value
                    value = args[i + 1]
                    i += 2
                else:
                    # Boolean flag
                    value = True
                    i += 1
                
                # Try to parse as JSON, fallback to string
                try:
                    params[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    params[key] = value
            else:
                # Positional argument - skip for now
                i += 1
        
        return params
    
    def list_functions(self) -> List[str]:
        """List available functions on the remote server."""
        try:
            response = self.session.get(f"{self.server_url}/_describe")
            response.raise_for_status()
            
            data = response.json()
            return list(data.get('functions', {}).keys())
            
        except Exception:
            return []
    
    def ping(self) -> bool:
        """Check if server is reachable."""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


def create_client(server_url: str, token: Optional[str] = None) -> YaappClient:
    """Create a yaapp client instance."""
    return YaappClient(server_url, token)