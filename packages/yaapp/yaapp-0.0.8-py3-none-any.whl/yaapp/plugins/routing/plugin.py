"""
Routing plugin for YAAPP framework.
Provides context-aware routing, agent switching, session isolation, and load balancing.
"""

import re
import threading
import time
import hashlib
from typing import Dict, Any, Optional, List, Callable, Protocol, runtime_checkable, Union, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from ...result import Result, Ok


class RoutingStrategy(Enum):
    """Available routing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    HASH_BASED = "hash_based"
    CUSTOM = "custom"


@dataclass
class RouteTarget:
    """Represents a routing target (handler/backend)."""
    name: str
    handler: Callable
    weight: int = 1
    max_connections: Optional[int] = None
    current_connections: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    health_check: Optional[Callable[[], bool]] = None
    last_health_check: Optional[float] = None
    
    def is_healthy(self) -> bool:
        """Check if target is healthy."""
        if not self.enabled:
            return False
        
        if self.health_check:
            now = time.time()
            # Cache health check for 30 seconds
            if (self.last_health_check is None or 
                now - self.last_health_check > 30):
                try:
                    healthy = self.health_check()
                    self.last_health_check = now
                    return healthy
                except (ConnectionError, TimeoutError, OSError):
                    # Health check failed due to network/connection issues
                    return False
            return True
        
        return True
    
    def can_accept_connection(self) -> bool:
        """Check if target can accept new connection."""
        return (self.is_healthy() and 
                (self.max_connections is None or 
                 self.current_connections < self.max_connections))


@dataclass
class Route:
    """Represents a routing rule."""
    name: str
    pattern: str
    targets: List[RouteTarget]
    strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    compiled_pattern: Optional[re.Pattern] = None
    priority: int = 100  # Lower = higher priority
    middleware: List[Callable] = field(default_factory=list)
    session_required: bool = False
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Compile regex pattern after initialization."""
        if isinstance(self.pattern, str):
            self.compiled_pattern = re.compile(self.pattern)
    
    def matches(self, path: str) -> Optional[re.Match]:
        """Check if route matches path."""
        if self.compiled_pattern:
            return self.compiled_pattern.match(path)
        return None


@runtime_checkable
class RoutingMiddleware(Protocol):
    """Protocol for routing middleware."""
    
    def process_request(self, request: Dict[str, Any], route: Route) -> Result[Dict[str, Any]]:
        """Process request before routing."""
        ...
    
    def process_response(self, response: Any, request: Dict[str, Any], route: Route) -> Any:
        """Process response after routing."""
        ...


class SessionRoutingMiddleware:
    """Middleware for session-based routing."""
    
    def __init__(self, session_handler):
        self.session_handler = session_handler
    
    def process_request(self, request: Dict[str, Any], route: Route) -> Result[Dict[str, Any]]:
        """Extract and validate session for routing."""
        if route.session_required:
            headers = request.get('headers', {})
            session_data = self.session_handler.middleware_extract_session(headers)
            
            if not session_data:
                return Result.error("Session required but not found")
            
            request['session'] = session_data
        
        return Ok(request)
    
    def process_response(self, response: Any, request: Dict[str, Any], route: Route) -> Any:
        """Add session headers to response."""
        if 'session' in request:
            # Response should include session headers
            if isinstance(response, dict) and 'headers' in response:
                session_id = request.get('session', {}).get('_session_id')
                if session_id:
                    response['headers'] = self.session_handler.middleware_create_response_headers(
                        session_id, response.get('headers', {})
                    )
        
        return response


class AgentSwitchingMiddleware:
    """Middleware for @agent-name style routing."""
    
    def __init__(self, agent_registry: Dict[str, Callable]):
        self.agent_registry = agent_registry
    
    def process_request(self, request: Dict[str, Any], route: Route) -> Result[Dict[str, Any]]:
        """Check for agent switching in request."""
        message = request.get('message', '')
        
        # Look for @agent-name pattern
        agent_match = re.search(r'@(\w+)', message)
        if agent_match:
            agent_name = agent_match.group(1)
            
            if agent_name in self.agent_registry:
                request['target_agent'] = agent_name
                # Remove @agent-name from message
                request['message'] = re.sub(r'@\w+\s*', '', message).strip()
            else:
                return Result.error(f"Unknown agent: {agent_name}")
        
        return Ok(request)
    
    def process_response(self, response: Any, request: Dict[str, Any], route: Route) -> Any:
        """Add agent info to response."""
        if 'target_agent' in request:
            if isinstance(response, dict):
                response['agent'] = request['target_agent']
        
        return response


class LoadBalancer:
    """Load balancer for route targets."""
    
    def __init__(self):
        self._round_robin_counters: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def select_target(self, route: Route, request: Dict[str, Any]) -> Optional[RouteTarget]:
        """Select target based on routing strategy."""
        available_targets = [t for t in route.targets if t.can_accept_connection()]
        
        if not available_targets:
            return None
        
        if route.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_select(route.name, available_targets)
        elif route.strategy == RoutingStrategy.WEIGHTED:
            return self._weighted_select(available_targets)
        elif route.strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(available_targets)
        elif route.strategy == RoutingStrategy.HASH_BASED:
            return self._hash_based_select(available_targets, request)
        else:
            # Default to first available
            return available_targets[0]
    
    def _round_robin_select(self, route_name: str, targets: List[RouteTarget]) -> RouteTarget:
        """Round-robin target selection."""
        with self._lock:
            counter = self._round_robin_counters.get(route_name, 0)
            target = targets[counter % len(targets)]
            self._round_robin_counters[route_name] = counter + 1
            return target
    
    def _weighted_select(self, targets: List[RouteTarget]) -> RouteTarget:
        """Weighted random target selection."""
        import random
        
        total_weight = sum(t.weight for t in targets)
        if total_weight == 0:
            return random.choice(targets)
        
        rand = random.randint(1, total_weight)
        current = 0
        
        for target in targets:
            current += target.weight
            if rand <= current:
                return target
        
        return targets[-1]  # Fallback
    
    def _least_connections_select(self, targets: List[RouteTarget]) -> RouteTarget:
        """Select target with least connections."""
        return min(targets, key=lambda t: t.current_connections)
    
    def _hash_based_select(self, targets: List[RouteTarget], request: Dict[str, Any]) -> RouteTarget:
        """Hash-based target selection for session affinity."""
        # Use session ID or client IP for hashing
        hash_key = (request.get('session', {}).get('_session_id') or 
                   request.get('client_ip', '') or 
                   str(time.time()))
        
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        return targets[hash_value % len(targets)]


class RouteManager:
    """Main routing manager."""
    
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[RoutingMiddleware] = []
        self.load_balancer = LoadBalancer()
        self._lock = threading.RLock()
        
        # Built-in agent registry for @agent switching
        self.agent_registry: Dict[str, Callable] = {}
        
        # Default error handlers
        self.error_handlers: Dict[str, Callable] = {
            'route_not_found': self._default_404_handler,
            'target_unavailable': self._default_503_handler,
            'middleware_error': self._default_500_handler,
            'session_error': self._default_401_handler
        }
    
    def add_route(self, route: Route) -> None:
        """Add a route to the manager."""
        with self._lock:
            self.routes.append(route)
            # Sort by priority (lower = higher priority)
            self.routes.sort(key=lambda r: r.priority)
    
    def remove_route(self, name: str) -> bool:
        """Remove route by name."""
        with self._lock:
            for i, route in enumerate(self.routes):
                if route.name == name:
                    del self.routes[i]
                    return True
            return False
    
    def add_middleware(self, middleware: RoutingMiddleware) -> None:
        """Add routing middleware."""
        self.middleware.append(middleware)
    
    def register_agent(self, name: str, handler: Callable) -> None:
        """Register agent for @agent switching."""
        self.agent_registry[name] = handler
    
    def set_error_handler(self, error_type: str, handler: Callable) -> None:
        """Set custom error handler."""
        self.error_handlers[error_type] = handler
    
    def route_request(self, path: str, request: Dict[str, Any]) -> Result[Any]:
        """Route a request through the system."""
        try:
            # Find matching route
            route = self._find_route(path)
            if not route:
                return Result.error(self.error_handlers['route_not_found'](path, request))
            
            # Process middleware
            processed_request = self._process_middleware(request, route)
            if not processed_request.is_ok():
                error_response = self.error_handlers['middleware_error'](
                    processed_request.error_message, request, route
                )
                return Result.error(error_response)
            
            request = processed_request.unwrap()
            
            # Select target
            target = self.load_balancer.select_target(route, request)
            if not target:
                error_response = self.error_handlers['target_unavailable'](route, request)
                return Result.error(error_response)
            
            # Execute request
            response = self._execute_request(target, request, route)
            
            # Process response through middleware
            final_response = self._process_response_middleware(response, request, route)
            
            return Ok(final_response)
            
        except Exception as e:
            error_response = self.error_handlers['middleware_error'](str(e), request, None)
            return Result.error(error_response)
    
    def _find_route(self, path: str) -> Optional[Route]:
        """Find matching route for path."""
        with self._lock:
            for route in self.routes:
                if route.matches(path):
                    return route
            return None
    
    def _process_middleware(self, request: Dict[str, Any], route: Route) -> Result[Dict[str, Any]]:
        """Process request through middleware chain."""
        current_request = request
        
        # Process global middleware
        for middleware in self.middleware:
            result = middleware.process_request(current_request, route)
            if not result.is_ok():
                return result
            current_request = result.unwrap()
        
        # Process route-specific middleware
        for middleware_func in route.middleware:
            try:
                current_request = middleware_func(current_request, route)
            except Exception as e:
                return Result.error(f"Route middleware error: {str(e)}")
        
        return Ok(current_request)
    
    def _process_response_middleware(self, response: Any, request: Dict[str, Any], route: Route) -> Any:
        """Process response through middleware chain (in reverse order)."""
        current_response = response
        
        # Process route-specific middleware (reverse order)
        for middleware_func in reversed(route.middleware):
            try:
                if hasattr(middleware_func, 'process_response'):
                    current_response = middleware_func.process_response(current_response, request, route)
            except Exception as e:
                print(f"Response middleware error: {e}")
        
        # Process global middleware (reverse order)
        for middleware in reversed(self.middleware):
            try:
                current_response = middleware.process_response(current_response, request, route)
            except Exception as e:
                print(f"Global response middleware error: {e}")
        
        return current_response
    
    def _execute_request(self, target: RouteTarget, request: Dict[str, Any], route: Route) -> Any:
        """Execute request on target."""
        # Track connection
        target.current_connections += 1
        
        try:
            # Check for agent switching
            if 'target_agent' in request and request['target_agent'] in self.agent_registry:
                handler = self.agent_registry[request['target_agent']]
                return handler(request)
            else:
                return target.handler(request)
        
        except Exception as e:
            return {'error': str(e)}
        
        finally:
            # Release connection
            target.current_connections = max(0, target.current_connections - 1)
    
    def _default_404_handler(self, path: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler for route not found."""
        return {
            'error': 'Route not found',
            'path': path,
            'status_code': 404
        }
    
    def _default_503_handler(self, route: Route, request: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler for target unavailable."""
        return {
            'error': 'Service temporarily unavailable',
            'route': route.name,
            'status_code': 503
        }
    
    def _default_500_handler(self, error: str, request: Dict[str, Any], route: Optional[Route]) -> Dict[str, Any]:
        """Default handler for middleware errors."""
        return {
            'error': 'Internal server error',
            'details': error,
            'status_code': 500
        }
    
    def _default_401_handler(self, error: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler for session errors."""
        return {
            'error': 'Authentication required',
            'details': error,
            'status_code': 401
        }
    
    def get_routes_info(self) -> List[Dict[str, Any]]:
        """Get information about all routes."""
        with self._lock:
            return [
                {
                    'name': route.name,
                    'pattern': route.pattern,
                    'strategy': route.strategy.value,
                    'targets': len(route.targets),
                    'healthy_targets': len([t for t in route.targets if t.is_healthy()]),
                    'priority': route.priority,
                    'session_required': route.session_required,
                    'permissions': route.permissions
                }
                for route in self.routes
            ]
    
    def get_target_stats(self) -> Dict[str, Any]:
        """Get statistics about route targets."""
        stats = {}
        
        with self._lock:
            for route in self.routes:
                route_stats = []
                for target in route.targets:
                    route_stats.append({
                        'name': target.name,
                        'enabled': target.enabled,
                        'healthy': target.is_healthy(),
                        'connections': target.current_connections,
                        'max_connections': target.max_connections,
                        'weight': target.weight
                    })
                stats[route.name] = route_stats
        
        return stats
    
    def health_check_all(self) -> Dict[str, bool]:
        """Run health checks on all targets."""
        results = {}
        
        with self._lock:
            for route in self.routes:
                for target in route.targets:
                    key = f"{route.name}.{target.name}"
                    results[key] = target.is_healthy()
        
        return results


# Convenience functions for common routing patterns
def create_simple_route(name: str, pattern: str, handler: Callable, 
                       priority: int = 100) -> Route:
    """Create a simple route with single target."""
    target = RouteTarget(name=f"{name}_target", handler=handler)
    return Route(
        name=name,
        pattern=pattern,
        targets=[target],
        priority=priority
    )


def create_load_balanced_route(name: str, pattern: str, handlers: List[Tuple[str, Callable]], 
                             strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN,
                             priority: int = 100) -> Route:
    """Create a load-balanced route with multiple targets."""
    targets = []
    for handler_name, handler in handlers:
        target = RouteTarget(name=handler_name, handler=handler)
        targets.append(target)
    
    return Route(
        name=name,
        pattern=pattern,
        targets=targets,
        strategy=strategy,
        priority=priority
    )


def create_session_aware_route(name: str, pattern: str, handler: Callable,
                             session_required: bool = True,
                             priority: int = 100) -> Route:
    """Create a session-aware route."""
    target = RouteTarget(name=f"{name}_target", handler=handler)
    return Route(
        name=name,
        pattern=pattern,
        targets=[target],
        session_required=session_required,
        priority=priority
    )


def create_agent_switching_route_manager(session_handler=None) -> RouteManager:
    """Create route manager with agent switching and session support."""
    manager = RouteManager()
    
    # Add agent switching middleware
    agent_middleware = AgentSwitchingMiddleware(manager.agent_registry)
    manager.add_middleware(agent_middleware)
    
    # Add session middleware if provided
    if session_handler:
        session_middleware = SessionRoutingMiddleware(session_handler)
        manager.add_middleware(session_middleware)
    
    return manager


# Alias for backward compatibility
Router = RouteManager