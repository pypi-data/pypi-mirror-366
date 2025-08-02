"""
Auth plugin for yaapp - comprehensive authentication and authorization.

This plugin provides both authentication (who are you?) and authorization (what can you do?)
services. All endpoints are exposed but access is controlled by the plugin itself.
"""

import hashlib
import secrets
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from yaapp import yaapp
from yaapp.result import Result, Ok


@yaapp.expose('auth')
class AuthPlugin:
    """
    Authentication and Authorization plugin for yaapp.
    
    Provides comprehensive auth services including:
    - User management (create, delete, list users)
    - Authentication (login, logout, token validation)
    - Authorization (roles, permissions, access control)
    - Token management (create, revoke, validate tokens)
    
    All endpoints are exposed but access is controlled internally based on:
    - Admin operations require admin role
    - User operations require valid authentication
    - Public operations (login) are unrestricted
    """
    
    def __init__(self, config: dict = None):
        """Initialize the auth plugin with configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        
        # Configuration with defaults
        self.auth_config = self.config.get('authentication', {})
        self.authz_config = self.config.get('authorization', {})
        
        # Authentication settings
        self.enabled = self.auth_config.get('enabled', True)
        self.methods = self.auth_config.get('methods', ['api_key', 'jwt'])
        self.token_expiry_hours = self._parse_duration(self.auth_config.get('token_expiry', '24h'))
        self.initial_admin_token = self.auth_config.get('initial_admin_token')
        
        # Authorization settings
        self.rbac_enabled = self.authz_config.get('rbac_enabled', True)
        self.default_role = self.authz_config.get('default_role', 'user')
        self.admin_role = self.authz_config.get('admin_role', 'admin')
        
        # Internal state
        self._storage_namespace = "auth"
        self._initialized = False
        self._initialization_attempted = False
        self.storage = None  # Will be set during initialization
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string like '24h', '7d', '30m' to hours."""
        if isinstance(duration_str, int):
            return duration_str
        
        duration_str = duration_str.lower().strip()
        if duration_str.endswith('h'):
            return int(duration_str[:-1])
        elif duration_str.endswith('d'):
            return int(duration_str[:-1]) * 24
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) // 60
        else:
            return int(duration_str)  # Assume hours
    
    def _ensure_initialized(self) -> Result[bool]:
        """Ensure the auth system is initialized."""
        if self._initialized:
            return Ok(True)
        
        if not self.yaapp:
            return Result.error("Auth plugin not properly initialized with yaapp instance")
        
        # Mark that we've attempted initialization to avoid repeated attempts
        if self._initialization_attempted:
            return Result.error("Storage plugin is not available. Make sure the storage plugin is properly configured and loaded.")
        
        self._initialization_attempted = True
        
        # Get storage plugin with retry logic
        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            # Storage plugin might not be registered yet - this is common during startup
            # Reset the attempt flag so we can try again later
            self._initialization_attempted = False
            return Result.error(f"Storage plugin not available: {storage_result.as_error}. Ensure storage is configured in yaapp.json.")
        
        self.storage = storage_result.unwrap()
        
        # Verify storage plugin has the required methods
        required_methods = ['get', 'set', 'delete', 'exists', 'keys']
        for method in required_methods:
            if not hasattr(self.storage, method):
                return Result.error(f"Storage plugin missing required method: {method}")
        
        # Initialize default admin user if initial token provided
        if self.initial_admin_token:
            self._create_initial_admin()
        
        self._initialized = True
        return Ok(True)
    
    def _create_initial_admin(self):
        """Create initial admin user with the provided token."""
        try:
            # Check if admin already exists
            admin_exists = self.storage.exists("user:admin", namespace=self._storage_namespace)
            if not admin_exists:
                # Create admin user
                admin_user = {
                    "id": "admin",
                    "username": "admin",
                    "password_hash": None,  # Token-only admin
                    "role": self.admin_role,
                    "created_at": datetime.now().isoformat(),
                    "active": True
                }
                self.storage.set("user:admin", admin_user, namespace=self._storage_namespace)
                self.storage.set("user_by_id:admin", admin_user, namespace=self._storage_namespace)  # Also store by ID
                
                # Create initial admin token
                token_data = {
                    "token": self.initial_admin_token,
                    "user_id": "admin",
                    "role": self.admin_role,
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),  # Long-lived bootstrap token
                    "active": True
                }
                self.storage.set(f"token:{self.initial_admin_token}", token_data, namespace=self._storage_namespace)
                
                print(f"✅ Created initial admin user with token: {self.initial_admin_token}")
        except Exception as e:
            print(f"Warning: Failed to create initial admin: {e}")
    
    def _get_storage(self):
        """Get storage instance, ensuring initialization."""
        init_result = self._ensure_initialized()
        if init_result.is_err():
            # Don't print error here - let the calling method handle it
            return None
        return self.storage
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, password_hash = stored_hash.split(':', 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except:
            return False
    
    def _generate_token(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    def _check_token_auth(self, token: str = None) -> Result[Dict[str, Any]]:
        """Check if provided token is valid and return user info."""
        if not token:
            return Result.error("No authentication token provided")
        
        storage = self._get_storage()
        if not storage:
            init_result = self._ensure_initialized()
            if init_result.is_err():
                return Result.error(f"Auth plugin initialization failed: {init_result.as_error}")
            return Result.error("Storage not available")
        
        try:
            token_data = storage.get(f"token:{token}", namespace=self._storage_namespace)
            if not token_data:
                return Result.error("Invalid token")
            
            if not token_data.get('active', True):
                return Result.error("Token has been revoked")
            
            # Check expiry
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                return Result.error("Token has expired")
            
            return Ok(token_data)
        except Exception as e:
            return Result.error(f"Token validation failed: {str(e)}")
    
    def _check_admin_auth(self, token: str = None) -> Result[Dict[str, Any]]:
        """Check if provided token has admin privileges."""
        auth_result = self._check_token_auth(token)
        if auth_result.is_err():
            return auth_result
        
        token_data = auth_result.unwrap()
        if token_data.get('role') != self.admin_role:
            return Result.error("Admin privileges required")
        
        return Ok(token_data)
    
    # =============================================================================
    # PUBLIC ENDPOINTS (No authentication required)
    # =============================================================================
    
    def login(self, username: str, password: str) -> Result[Dict[str, Any]]:
        """
        Authenticate user with username/password and return token.
        
        Public endpoint - no authentication required.
        """
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get user
            user_data = storage.get(f"user:{username}", namespace=self._storage_namespace)
            if not user_data:
                return Result.error("Invalid username or password")
            
            if not user_data.get('active', True):
                return Result.error("User account is disabled")
            
            # Verify password
            if not user_data.get('password_hash'):
                return Result.error("Password authentication not available for this user")
            
            if not self._verify_password(password, user_data['password_hash']):
                return Result.error("Invalid username or password")
            
            # Create token
            token = self._generate_token()
            token_data = {
                "token": token,
                "user_id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat(),
                "active": True
            }
            
            storage.set(f"token:{token}", token_data, namespace=self._storage_namespace)
            
            return Ok({
                "token": token,
                "user_id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "expires_at": token_data['expires_at']
            })
            
        except Exception as e:
            return Result.error(f"Login failed: {str(e)}")
    
    def validate_token(self, token: str) -> Result[Dict[str, Any]]:
        """
        Validate authentication token and return user info.
        
        Public endpoint - no authentication required.
        """
        auth_result = self._check_token_auth(token)
        if auth_result.is_err():
            return auth_result
        
        token_data = auth_result.unwrap()
        return Ok({
            "valid": True,
            "user_id": token_data['user_id'],
            "username": token_data.get('username'),
            "role": token_data['role'],
            "expires_at": token_data['expires_at']
        })
    
    def get_auth_info(self) -> Result[Dict[str, Any]]:
        """
        Get authentication system information.
        
        Public endpoint - returns non-sensitive configuration info.
        """
        return Ok({
            "enabled": self.enabled,
            "methods": self.methods,
            "rbac_enabled": self.rbac_enabled,
            "default_role": self.default_role,
            "token_expiry_hours": self.token_expiry_hours
        })
    
    # =============================================================================
    # USER ENDPOINTS (Authentication required)
    # =============================================================================
    
    def logout(self, token: str) -> Result[Dict[str, str]]:
        """
        Logout user by revoking their token.
        
        Requires: Valid authentication token
        """
        auth_result = self._check_token_auth(token)
        if auth_result.is_err():
            return auth_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Revoke token
            token_data = auth_result.unwrap()
            token_data['active'] = False
            token_data['revoked_at'] = datetime.now().isoformat()
            
            storage.set(f"token:{token}", token_data, namespace=self._storage_namespace)
            
            return Ok({"message": "Successfully logged out"})
            
        except Exception as e:
            return Result.error(f"Logout failed: {str(e)}")
    
    def get_my_profile(self, token: str) -> Result[Dict[str, Any]]:
        """
        Get current user's profile information.
        
        Requires: Valid authentication token
        """
        auth_result = self._check_token_auth(token)
        if auth_result.is_err():
            return auth_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            token_data = auth_result.unwrap()
            user_data = storage.get(f"user_by_id:{token_data['user_id']}", namespace=self._storage_namespace)
            
            if not user_data:
                return Result.error("User not found")
            
            # Return safe user info (no password hash)
            return Ok({
                "id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "created_at": user_data['created_at'],
                "active": user_data.get('active', True)
            })
            
        except Exception as e:
            return Result.error(f"Failed to get profile: {str(e)}")
    
    def change_password(self, token: str, current_password: str, new_password: str) -> Result[Dict[str, str]]:
        """
        Change current user's password.
        
        Requires: Valid authentication token
        """
        auth_result = self._check_token_auth(token)
        if auth_result.is_err():
            return auth_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            token_data = auth_result.unwrap()
            user_data = storage.get(f"user_by_id:{token_data['user_id']}", namespace=self._storage_namespace)
            
            if not user_data:
                return Result.error("User not found")
            
            # Verify current password
            if not user_data.get('password_hash'):
                return Result.error("Password authentication not available for this user")
            
            if not self._verify_password(current_password, user_data['password_hash']):
                return Result.error("Current password is incorrect")
            
            # Update password
            user_data['password_hash'] = self._hash_password(new_password)
            user_data['password_changed_at'] = datetime.now().isoformat()
            
            storage.set(f"user:{user_data['id']}", user_data, namespace=self._storage_namespace)
            
            return Ok({"message": "Password changed successfully"})
            
        except Exception as e:
            return Result.error(f"Password change failed: {str(e)}")
    
    # =============================================================================
    # ADMIN ENDPOINTS (Admin authentication required)
    # =============================================================================
    
    def create_user(self, token: str, username: str, password: str, role: str = None) -> Result[Dict[str, Any]]:
        """
        Create a new user account.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Check if user already exists
            if storage.exists(f"user:{username}", namespace=self._storage_namespace):
                return Result.error(f"User '{username}' already exists")
            
            # Create user
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "username": username,
                "password_hash": self._hash_password(password),
                "role": role or self.default_role,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            storage.set(f"user:{username}", user_data, namespace=self._storage_namespace)
            storage.set(f"user_by_id:{user_id}", user_data, namespace=self._storage_namespace)
            
            return Ok({
                "id": user_id,
                "username": username,
                "role": user_data['role'],
                "created_at": user_data['created_at']
            })
            
        except Exception as e:
            return Result.error(f"User creation failed: {str(e)}")
    
    def delete_user(self, token: str, username: str) -> Result[Dict[str, str]]:
        """
        Delete a user account.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get user data
            user_data = storage.get(f"user:{username}", namespace=self._storage_namespace)
            if not user_data:
                return Result.error(f"User '{username}' not found")
            
            # Prevent deleting admin user
            if username == "admin":
                return Result.error("Cannot delete admin user")
            
            # Delete user records
            storage.delete(f"user:{username}", namespace=self._storage_namespace)
            storage.delete(f"user_by_id:{user_data['id']}", namespace=self._storage_namespace)
            
            # TODO: Revoke all user tokens
            
            return Ok({"message": f"User '{username}' deleted successfully"})
            
        except Exception as e:
            return Result.error(f"User deletion failed: {str(e)}")
    
    def list_users(self, token: str) -> Result[List[Dict[str, Any]]]:
        """
        List all user accounts.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get all user keys
            user_keys = storage.keys(pattern="user:*", namespace=self._storage_namespace)
            users = []
            
            for key in user_keys:
                if key.startswith("user:") and not key.startswith("user_by_id:"):
                    user_data = storage.get(key, namespace=self._storage_namespace)
                    if user_data:
                        users.append({
                            "id": user_data['id'],
                            "username": user_data['username'],
                            "role": user_data['role'],
                            "created_at": user_data['created_at'],
                            "active": user_data.get('active', True)
                        })
            
            return Ok(users)
            
        except Exception as e:
            return Result.error(f"Failed to list users: {str(e)}")
    
    def create_token(self, token: str, user_id: str, expires: str = "24h") -> Result[Dict[str, Any]]:
        """
        Create authentication token for a user.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get user data
            user_data = storage.get(f"user_by_id:{user_id}", namespace=self._storage_namespace)
            if not user_data:
                return Result.error(f"User with ID '{user_id}' not found")
            
            # Create token
            new_token = self._generate_token()
            expiry_hours = self._parse_duration(expires)
            
            token_data = {
                "token": new_token,
                "user_id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
                "active": True
            }
            
            storage.set(f"token:{new_token}", token_data, namespace=self._storage_namespace)
            
            return Ok({
                "token": new_token,
                "user_id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "expires_at": token_data['expires_at']
            })
            
        except Exception as e:
            return Result.error(f"Token creation failed: {str(e)}")
    
    def revoke_token(self, token: str, target_token: str) -> Result[Dict[str, str]]:
        """
        Revoke an authentication token.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get token data
            token_data = storage.get(f"token:{target_token}", namespace=self._storage_namespace)
            if not token_data:
                return Result.error("Token not found")
            
            # Revoke token
            token_data['active'] = False
            token_data['revoked_at'] = datetime.now().isoformat()
            
            storage.set(f"token:{target_token}", token_data, namespace=self._storage_namespace)
            
            return Ok({"message": "Token revoked successfully"})
            
        except Exception as e:
            return Result.error(f"Token revocation failed: {str(e)}")
    
    def assign_role(self, token: str, username: str, role: str) -> Result[Dict[str, str]]:
        """
        Assign role to a user.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get user data
            user_data = storage.get(f"user:{username}", namespace=self._storage_namespace)
            if not user_data:
                return Result.error(f"User '{username}' not found")
            
            # Update role
            user_data['role'] = role
            user_data['role_changed_at'] = datetime.now().isoformat()
            
            storage.set(f"user:{username}", user_data, namespace=self._storage_namespace)
            storage.set(f"user_by_id:{user_data['id']}", user_data, namespace=self._storage_namespace)
            
            return Ok({"message": f"Role '{role}' assigned to user '{username}'"})
            
        except Exception as e:
            return Result.error(f"Role assignment failed: {str(e)}")
    
    def check_permission(self, token: str, user_id: str, resource: str, action: str) -> Result[Dict[str, Any]]:
        """
        Check if user has permission for action on resource.
        
        Requires: Admin authentication token
        """
        admin_result = self._check_admin_auth(token)
        if admin_result.is_err():
            return admin_result
        
        storage = self._get_storage()
        if not storage:
            return Result.error("Storage not available")
        
        try:
            # Get user data
            user_data = storage.get(f"user_by_id:{user_id}", namespace=self._storage_namespace)
            if not user_data:
                return Result.error(f"User with ID '{user_id}' not found")
            
            # Simple role-based check (can be extended)
            user_role = user_data['role']
            
            # Admin has all permissions
            if user_role == self.admin_role:
                allowed = True
            else:
                # Basic permission logic (extend as needed)
                allowed = action in ['read']  # Users can only read by default
            
            return Ok({
                "user_id": user_id,
                "username": user_data['username'],
                "role": user_role,
                "resource": resource,
                "action": action,
                "allowed": allowed
            })
            
        except Exception as e:
            return Result.error(f"Permission check failed: {str(e)}")