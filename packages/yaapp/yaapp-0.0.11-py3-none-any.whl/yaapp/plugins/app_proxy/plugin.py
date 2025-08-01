"""
AppProxy plugin for YAPP - enables app-to-app chaining.
"""

import json
import asyncio
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
from ...result import Result, Ok
from yaapp import yaapp

if TYPE_CHECKING:
    import aiohttp

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    # Fallback to urllib for backward compatibility
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError


@yaapp.expose("app_proxy")
class AppProxy:
    """Proxy that discovers and exposes remote YApp APIs."""
    
    def __init__(self, config=None, target_url: str = None, timeout: float = 30.0, max_retries: int = 3):
        """Initialize AppProxy with target YApp server URL or config."""
        # Handle both config-based and direct parameter initialization
        if config is not None:
            # Config-based initialization (for discovery system)
            if isinstance(config, dict):
                self.target_url = config.get('target_url', 'http://localhost:8001').rstrip('/')
                self.timeout = config.get('timeout', 30.0)
                self.max_retries = config.get('max_retries', 3)
            else:
                # Backward compatibility: config is actually target_url string
                self.target_url = str(config).rstrip('/')
                self.timeout = timeout
                self.max_retries = max_retries
        else:
            # Direct parameter initialization (for manual use)
            if target_url is None:
                raise ValueError("Either config or target_url must be provided")
            self.target_url = target_url.rstrip('/')
            self.timeout = timeout
            self.max_retries = max_retries
        
        self.yaapp = None  # Will be set by the main app when registered
        self._discovered_functions = {}
        self._proxy_functions = {}
        self._session: Optional['aiohttp.ClientSession'] = None
        self._session_lock = asyncio.Lock() if HAS_AIOHTTP else None
        
        # Circuit breaker state
        self._failure_count = 0
        self._last_failure_time = 0
        self._circuit_open = False
        self._circuit_timeout = 60.0  # Circuit breaker timeout in seconds
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should allow requests."""
        if self._circuit_open:
            # Check if enough time has passed to retry
            if time.time() - self._last_failure_time > self._circuit_timeout:
                self._circuit_open = False
                self._failure_count = 0
            else:
                print(f"Warning: Circuit breaker open - service unavailable. Retry in {self._circuit_timeout - (time.time() - self._last_failure_time):.1f}s")
                return False
        return True
    
    def _record_success(self) -> None:
        """Record successful request."""
        self._failure_count = 0
        self._circuit_open = False
    
    def _record_failure(self) -> None:
        """Record failed request and potentially open circuit."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        # Open circuit breaker after 3 consecutive failures
        if self._failure_count >= 3:
            self._circuit_open = True
    
    async def _get_session(self) -> 'aiohttp.ClientSession':
        """Get or create aiohttp session with connection pooling."""
        if not HAS_AIOHTTP:
            print("Error: aiohttp not available - install with: pip install aiohttp")
            return None
        
        # Always create a new session to avoid event loop issues
        # when called from asyncio.run() in different contexts
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(
            limit=10,  # Connection pool size
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'Content-Type': 'application/json'}
        )
        return session
    
    async def close(self):
        """Close the HTTP session and clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def expose_to_registry(self, name: str, exposer) -> None:
        """Discover remote API and register proxy functions."""
        print(f"🔍 AppProxy: Discovering remote API from {self.target_url}...")
        
        # Use sync wrapper for async discovery
        try:
            # Check if we're already in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to schedule the discovery
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._async_expose_to_registry(name, exposer))
                    future.result(timeout=self.timeout)
            except RuntimeError:
                # No running loop, we can run async directly
                asyncio.run(self._async_expose_to_registry(name, exposer))
        except Exception as e:
            print(f"❌ AppProxy: Failed to expose proxy: {e}")
            # Re-raise the exception so the exposer system can handle it
            raise ValueError(f"AppProxy exposure failed: {e}")
    
    async def _async_expose_to_registry(self, name: str, exposer) -> None:
        """Async version of expose_to_registry."""
        # Discover the remote API structure
        discovery_result = await self._discover_remote_api()
        if not discovery_result.is_ok():
            print(f"Error: Failed to discover remote API: {discovery_result.as_error}")
            return
        
        api_structure = discovery_result.unwrap()
        
        # Create proxy functions for each discovered function
        self._create_proxy_functions(api_structure)
        
        # Store discovered functions for execution
        self._discovered_functions = api_structure
        
        print(f"✅ AppProxy: Successfully discovered {len(api_structure)} remote functions")
        for func_name in api_structure.keys():
            print(f"   📡 {func_name}")
    
    def execute_call(self, function_name: str, **kwargs) -> Any:
        """Execute a call to the remote API."""
        if function_name not in self._discovered_functions:
            available = list(self._discovered_functions.keys())
            print(f"Error: Function '{function_name}' not found in remote API. Available: {available}")
            return None
        
        print(f"📡 AppProxy: Calling remote function '{function_name}' with args: {kwargs}")
        
        # Make RPC call to remote server using sync wrapper
        try:
            # Check if we're already in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to schedule the call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._make_rpc_call(function_name, kwargs))
                    result = future.result(timeout=self.timeout)
                    print(f"✅ AppProxy: Remote call successful, result: {result}")
                    return result
            except RuntimeError:
                # No running loop, we can run async directly
                result = asyncio.run(self._make_rpc_call(function_name, kwargs))
                print(f"✅ AppProxy: Remote call successful, result: {result}")
                return result
        except Exception as e:
            print(f"❌ AppProxy: RPC call failed: {e}")
            return None
    
    async def execute_call_async(self, function_name: str, **kwargs) -> Any:
        """Async version of execute_call."""
        if function_name not in self._discovered_functions:
            print(f"Error: Function '{function_name}' not found in remote API")
            return None
        
        # Make RPC call to remote server
        return await self._make_rpc_call(function_name, kwargs)
    
    async def _discover_remote_api(self) -> Result[Dict[str, Any]]:
        """Discover remote API structure via /_describe_rpc endpoint."""
        if HAS_AIOHTTP:
            return await self._discover_remote_api_async()
        else:
            return self._discover_remote_api_sync()
    
    async def _discover_remote_api_async(self) -> Result[Dict[str, Any]]:
        """Async version using aiohttp."""
        session = None
        try:
            if not self._check_circuit_breaker():
                self._record_failure()
                return Result.error("Circuit breaker open - service unavailable")
            
            session = await self._get_session()
            if session is None:
                return Result.error("Failed to create HTTP session")
            url = f"{self.target_url}/_describe_rpc"
            
            async with session.get(url) as response:
                if response.status != 200:
                    self._record_failure()
                    return Result.error(f"HTTP {response.status}: {response.reason}")
                
                api_data = await response.json()
                
                # Extract function information
                functions = {}
                if 'functions' in api_data:
                    functions = api_data['functions']
                else:
                    # Handle tree structure - flatten it
                    functions = self._flatten_api_tree(api_data)
                
                self._record_success()
                return Ok(functions)
                
        except asyncio.TimeoutError:
            self._record_failure()
            return Result.error(f"Request timeout after {self.timeout}s")
        except aiohttp.ClientError as e:
            self._record_failure()
            return Result.error(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            self._record_failure()
            return Result.error(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            if "Circuit breaker" in str(e):
                return Result.error(f"Circuit breaker error: {str(e)}")
            self._record_failure()
            return Result.error(f"API discovery failed: {str(e)}")
        finally:
            if session and not session.closed:
                await session.close()
    
    def _discover_remote_api_sync(self) -> Result[Dict[str, Any]]:
        """Fallback sync version using urllib."""
        try:
            url = f"{self.target_url}/_describe_rpc"
            request = Request(url, method='GET')
            request.add_header('Content-Type', 'application/json')
            
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read().decode('utf-8')
                api_data = json.loads(data)
                
                # Extract function information
                functions = {}
                if 'functions' in api_data:
                    functions = api_data['functions']
                else:
                    # Handle tree structure - flatten it
                    functions = self._flatten_api_tree(api_data)
                
                return Ok(functions)
                
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            return Result.error(f"API discovery failed: {str(e)}")
    
    def _flatten_api_tree(self, tree: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten hierarchical API tree into function dictionary."""
        functions = {}
        
        for name, item in tree.items():
            full_name = f"{prefix}.{name}" if prefix else name
            
            if isinstance(item, dict):
                if item.get('type') == 'function':
                    functions[full_name] = item
                elif 'commands' in item:
                    # Namespace - recurse
                    functions.update(self._flatten_api_tree(item['commands'], full_name))
                elif 'methods' in item:
                    # Class with methods - recurse
                    functions.update(self._flatten_api_tree(item['methods'], full_name))
        
        return functions
    
    def _create_proxy_functions(self, functions: Dict[str, Any]) -> None:
        """Create proxy functions for discovered remote functions."""
        for func_name, func_info in functions.items():
            # Create a proxy function that calls the remote API
            def make_proxy(name):
                def proxy_func(**kwargs):
                    # Use sync wrapper for compatibility
                    try:
                        # Check if we're already in an async context
                        try:
                            loop = asyncio.get_running_loop()
                            # We're in an async context, need to schedule the call
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, self._make_rpc_call(name, kwargs))
                                return future.result(timeout=self.timeout)
                        except RuntimeError:
                            # No running loop, we can run async directly
                            return asyncio.run(self._make_rpc_call(name, kwargs))
                    except Exception as e:
                        print(f"Error: Proxy call failed: {e}")
                        return None
                return proxy_func
            
            self._proxy_functions[func_name] = make_proxy(func_name)
    
    async def _make_rpc_call(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Make RPC call to remote YApp server."""
        if HAS_AIOHTTP:
            return await self._make_rpc_call_async(function_name, arguments)
        else:
            return self._make_rpc_call_sync(function_name, arguments)
    
    async def _make_rpc_call_async(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Async version using aiohttp."""
        session = None
        try:
            if not self._check_circuit_breaker():
                self._record_failure()
                print("Error: Circuit breaker open - service unavailable")
                return None
            
            session = await self._get_session()
            if session is None:
                print("Error: Failed to create HTTP session")
                return None
            url = f"{self.target_url}/_rpc"
            
            payload = {
                "function": function_name,
                "arguments": arguments
            }
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    self._record_failure()
                    error_text = await response.text()
                    print(f"Error: HTTP {response.status}: {error_text}")
                    return None
                
                response_data = await response.json()
                
                if 'error' in response_data:
                    # This is an application error, not a network error
                    # Don't trigger circuit breaker for app errors
                    print(f"Remote error: {response_data['error']}")
                    return None
                else:
                    # Server returns result directly now
                    self._record_success()
                    return response_data
                    
        except asyncio.TimeoutError:
            self._record_failure()
            print(f"Error: RPC call timeout after {self.timeout}s")
            return None
        except aiohttp.ClientError as e:
            self._record_failure()
            print(f"Error: Network error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self._record_failure()
            print(f"Error: Invalid JSON response: {str(e)}")
            return None
        except Exception as e:
            if "Remote error:" in str(e):
                print(f"Remote error: {str(e)}")
                return None
            if "Circuit breaker" in str(e):
                print(f"Circuit breaker error: {str(e)}")
                return None
            self._record_failure()
            print(f"Error: RPC call failed: {str(e)}")
            return None
        finally:
            if session and not session.closed:
                await session.close()
    
    def _make_rpc_call_sync(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Fallback sync version using urllib."""
        try:
            url = f"{self.target_url}/_rpc"
            
            payload = {
                "function": function_name,
                "arguments": arguments
            }
            
            request = Request(url, method='POST')
            request.add_header('Content-Type', 'application/json')
            request.data = json.dumps(payload).encode('utf-8')
            
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read().decode('utf-8')
                response_data = json.loads(data)
                
                if 'error' in response_data:
                    print(f"Remote error: {response_data['error']}")
                    return None
                else:
                    # Server returns result directly now
                    return response_data
                    
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            print(f"Error: RPC call failed: {str(e)}")
            return None
    
    def get_available_functions(self) -> Dict[str, Any]:
        """Get list of available proxy functions."""
        return self._discovered_functions.copy()