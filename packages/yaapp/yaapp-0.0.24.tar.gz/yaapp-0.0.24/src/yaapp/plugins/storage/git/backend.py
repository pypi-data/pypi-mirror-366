"""
Git-based storage backend implementation.
Stores data as Git objects for immutable, auditable persistence.
"""

import json
import subprocess
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import threading
import fnmatch


class GitStorageError(Exception):
    """Git storage specific errors."""
    pass


class GitStorage:
    """
    Git-based storage backend that implements the YAAPP storage protocol.
    
    Stores data as Git objects (blobs) with commits providing audit trails.
    Each storage operation creates a Git commit for complete immutability.
    """
    
    def __init__(self, repo_path: str, author_name: str = "YAAPP Storage", 
                 author_email: str = "storage@yaapp.dev", auto_gc: bool = True):
        """
        Initialize Git storage backend.
        
        Args:
            repo_path: Path to Git repository
            author_name: Git author name for commits
            author_email: Git author email for commits
            auto_gc: Whether to automatically run git gc periodically
        """
        self.repo_path = Path(repo_path)
        self.author_name = author_name
        self.author_email = author_email
        self.auto_gc = auto_gc
        self._lock = threading.RLock()
        
        # Initialize repository
        self._init_repository()
        
        # In-memory cache for performance
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_max_age = 300  # 5 minutes
        
        # Start background maintenance if enabled
        if auto_gc:
            self._start_maintenance_thread()
    
    def _init_repository(self):
        """Initialize Git repository if it doesn't exist."""
        self.repo_path.mkdir(parents=True, exist_ok=True)
        
        if not (self.repo_path / ".git").exists():
            # Initialize Git repository
            self._run_git_command(["init"])
            
            # Configure Git user
            self._run_git_command(["config", "user.name", self.author_name])
            self._run_git_command(["config", "user.email", self.author_email])
            
            # Create initial commit
            readme_path = self.repo_path / "README.md"
            readme_path.write_text("# YAAPP Git Storage\\n\\nThis repository stores YAAPP data as Git objects.\\n")
            
            self._run_git_command(["add", "README.md"])
            self._run_git_command(["commit", "-m", "Initial commit: YAAPP Git Storage"])
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run Git command in repository directory."""
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: Git command failed: {e.stderr}")
            return None
    
    def _start_maintenance_thread(self):
        """Start background maintenance thread."""
        def maintenance_worker():
            while True:
                try:
                    time.sleep(3600)  # Run every hour
                    with self._lock:
                        # Run git gc to optimize repository
                        self._run_git_command(["gc", "--auto"], check=False)
                        
                        # Clean cache
                        self._cleanup_cache()
                        
                except Exception as e:
                    # Log error but don't crash
                    print(f"Git storage maintenance error: {e}")
        
        thread = threading.Thread(target=maintenance_worker, daemon=True)
        thread.start()
    
    def _cleanup_cache(self):
        """Remove expired cache entries."""
        now = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if now - timestamp > self._cache_max_age
        ]
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    def _get_data_file_path(self, key: str) -> Path:
        """Get file path for storing data."""
        # Use subdirectories to avoid too many files in one directory
        key_hash = str(hash(key) % 1000).zfill(3)
        subdir = self.repo_path / "data" / key_hash[:2]
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f"{key}.json"
    
    def _store_data_to_file(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store data to file with metadata."""
        try:
            file_path = self._get_data_file_path(key)
            
            # Prepare storage data with metadata
            storage_data = {
                "key": key,
                "data": data,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (
                        datetime.fromtimestamp(time.time() + ttl_seconds).isoformat()
                        if ttl_seconds else None
                    ),
                    "storage_version": "1.0"
                }
            }
            
            # Write to file
            file_path.write_text(json.dumps(storage_data, default=str, indent=2))
            
            # Add to Git
            relative_path = file_path.relative_to(self.repo_path)
            self._run_git_command(["add", str(relative_path)])
            
            return True
            
        except (json.JSONEncodeError, OSError) as e:
            print(f"Error: Failed to store data for key '{key}': {e}")
            return False
    
    def _load_data_from_file(self, key: str) -> Optional[Dict]:
        """Load data from file with expiration check."""
        try:
            file_path = self._get_data_file_path(key)
            
            if not file_path.exists():
                return None
            
            # Read and parse data
            content = file_path.read_text()
            storage_data = json.loads(content)
            
            # Check expiration
            expires_at = storage_data.get("metadata", {}).get("expires_at")
            if expires_at:
                expiry_time = datetime.fromisoformat(expires_at)
                if datetime.now() > expiry_time:
                    # Data expired, remove it
                    self.delete(key)
                    return None
            
            return storage_data
            
        except (json.JSONDecodeError, OSError, ValueError):
            return None
    
    def _commit_changes(self, message: str) -> str:
        """Commit current changes and return commit hash."""
        try:
            # Check if there are changes to commit
            status_result = self._run_git_command(["status", "--porcelain"])
            if not status_result.stdout.strip():
                # No changes to commit, return current HEAD
                head_result = self._run_git_command(["rev-parse", "HEAD"])
                return head_result.stdout.strip()
            
            # Commit changes
            self._run_git_command(["commit", "-m", message])
            
            # Get commit hash
            result = self._run_git_command(["rev-parse", "HEAD"])
            return result.stdout.strip()
            
        except GitStorageError as e:
            print(f"Error: Git storage error: {e}")
            return None
        except Exception as e:
            print(f"Error: Failed to commit changes: {e}")
            return None
    
    # Storage Protocol Implementation
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        with self._lock:
            # Check cache first
            if key in self._cache:
                cache_time = self._cache_timestamps.get(key, 0)
                if time.time() - cache_time < self._cache_max_age:
                    return self._cache[key]
            
            # Load from Git storage
            storage_data = self._load_data_from_file(key)
            if storage_data:
                data = storage_data["data"]
                
                # Update cache
                self._cache[key] = data
                self._cache_timestamps[key] = time.time()
                
                return data
            
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        with self._lock:
            try:
                # Store data to file
                success = self._store_data_to_file(key, value, ttl_seconds)
                if not success:
                    return False
                
                # Commit changes
                commit_message = f"Store: {key}"
                if ttl_seconds:
                    commit_message += f" (TTL: {ttl_seconds}s)"
                
                commit_hash = self._commit_changes(commit_message)
                
                # Update cache
                self._cache[key] = value
                self._cache_timestamps[key] = time.time()
                
                return True
                
            except GitStorageError:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        with self._lock:
            try:
                file_path = self._get_data_file_path(key)
                
                if not file_path.exists():
                    return False
                
                # Remove file
                file_path.unlink()
                
                # Remove from Git
                relative_path = file_path.relative_to(self.repo_path)
                self._run_git_command(["add", str(relative_path)])
                
                # Commit deletion
                self._commit_changes(f"Delete: {key}")
                
                # Remove from cache
                self._cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
                
                return True
                
            except (OSError, GitStorageError):
                return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        with self._lock:
            keys = []
            
            data_dir = self.repo_path / "data"
            if not data_dir.exists():
                return keys
            
            # Scan all data files
            for json_file in data_dir.rglob("*.json"):
                try:
                    content = json_file.read_text()
                    storage_data = json.loads(content)
                    key = storage_data.get("key")
                    
                    if not key:
                        continue
                    
                    # Check expiration
                    expires_at = storage_data.get("metadata", {}).get("expires_at")
                    if expires_at:
                        expiry_time = datetime.fromisoformat(expires_at)
                        if datetime.now() > expiry_time:
                            continue  # Skip expired keys
                    
                    # Apply pattern filter
                    if pattern and not fnmatch.fnmatch(key, pattern):
                        continue
                    
                    keys.append(key)
                    
                except (json.JSONDecodeError, OSError, ValueError):
                    continue
            
            return sorted(keys)
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        with self._lock:
            try:
                keys = self.keys()
                count = 0
                
                for key in keys:
                    if self.delete(key):
                        count += 1
                
                # Clear cache
                self._cache.clear()
                self._cache_timestamps.clear()
                
                return count
                
            except Exception:
                return 0
    
    def cleanup_expired(self) -> int:
        """Remove expired items, return count removed."""
        with self._lock:
            count = 0
            now = datetime.now()
            
            data_dir = self.repo_path / "data"
            if not data_dir.exists():
                return count
            
            # Scan for expired files
            for json_file in data_dir.rglob("*.json"):
                try:
                    content = json_file.read_text()
                    storage_data = json.loads(content)
                    
                    expires_at = storage_data.get("metadata", {}).get("expires_at")
                    if expires_at:
                        expiry_time = datetime.fromisoformat(expires_at)
                        if now > expiry_time:
                            key = storage_data.get("key")
                            if key and self.delete(key):
                                count += 1
                    
                except (json.JSONDecodeError, OSError, ValueError):
                    continue
            
            return count
    
    # Git-specific methods
    
    def get_history(self, key: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get Git history for a specific key."""
        with self._lock:
            try:
                file_path = self._get_data_file_path(key)
                relative_path = file_path.relative_to(self.repo_path)
                
                # Build git log command
                cmd = ["log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
                if limit:
                    cmd.extend(["-n", str(limit)])
                cmd.extend(["--", str(relative_path)])
                
                result = self._run_git_command(cmd, check=False)
                
                if result.returncode != 0:
                    return []
                
                history = []
                for line in result.stdout.strip().split('\\n'):
                    if line:
                        parts = line.split('|', 4)
                        if len(parts) == 5:
                            history.append({
                                'commit_hash': parts[0],
                                'author_name': parts[1],
                                'author_email': parts[2],
                                'date': parts[3],
                                'message': parts[4]
                            })
                
                return history
                
            except Exception:
                return []
    
    def get_commit_data(self, commit_hash: str, key: str) -> Optional[Any]:
        """Get data for a key at a specific commit."""
        with self._lock:
            try:
                file_path = self._get_data_file_path(key)
                relative_path = file_path.relative_to(self.repo_path)
                
                # Get file content at specific commit
                result = self._run_git_command([
                    "show", f"{commit_hash}:{relative_path}"
                ], check=False)
                
                if result.returncode != 0:
                    return None
                
                storage_data = json.loads(result.stdout)
                return storage_data.get("data")
                
            except (json.JSONDecodeError, GitStorageError):
                return None
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get Git repository statistics."""
        with self._lock:
            try:
                # Count commits
                commit_result = self._run_git_command(["rev-list", "--count", "HEAD"], check=False)
                total_commits = int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0
                
                # Count objects
                objects_result = self._run_git_command(["count-objects", "-v"], check=False)
                objects_info = {}
                if objects_result.returncode == 0:
                    for line in objects_result.stdout.strip().split('\\n'):
                        if ' ' in line:
                            key, value = line.split(' ', 1)
                            try:
                                objects_info[key] = int(value)
                            except ValueError:
                                objects_info[key] = value
                
                # Get repository size
                repo_size = sum(f.stat().st_size for f in self.repo_path.rglob('*') if f.is_file())
                
                # Get latest commit info
                latest_commit = {}
                try:
                    latest_result = self._run_git_command([
                        "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--date=iso"
                    ])
                    if latest_result.returncode == 0:
                        parts = latest_result.stdout.strip().split('|', 3)
                        if len(parts) == 4:
                            latest_commit = {
                                'hash': parts[0],
                                'author': parts[1],
                                'date': parts[2],
                                'message': parts[3]
                            }
                except Exception:
                    pass
                
                return {
                    'repository_path': str(self.repo_path),
                    'total_commits': total_commits,
                    'total_keys': len(self.keys()),
                    'cache_size': len(self._cache),
                    'repository_size_bytes': repo_size,
                    'git_objects': objects_info,
                    'latest_commit': latest_commit
                }
                
            except Exception as e:
                return {
                    'repository_path': str(self.repo_path),
                    'error': str(e)
                }
    
    def create_backup(self, backup_path: str) -> bool:
        """Create a backup of the Git repository."""
        with self._lock:
            try:
                backup_path_obj = Path(backup_path)
                backup_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                # Create a bare clone as backup
                subprocess.run([
                    "git", "clone", "--bare", str(self.repo_path), str(backup_path)
                ], check=True, capture_output=True)
                
                return True
                
            except subprocess.CalledProcessError:
                return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore repository from backup."""
        with self._lock:
            try:
                # Clear current repository
                import shutil
                if self.repo_path.exists():
                    shutil.rmtree(self.repo_path)
                
                # Clone from backup
                subprocess.run([
                    "git", "clone", str(backup_path), str(self.repo_path)
                ], check=True, capture_output=True)
                
                # Clear cache
                self._cache.clear()
                self._cache_timestamps.clear()
                
                return True
                
            except subprocess.CalledProcessError:
                return False


def create_git_storage(repo_path: str, **kwargs) -> GitStorage:
    """Factory function to create Git storage backend."""
    return GitStorage(repo_path, **kwargs)