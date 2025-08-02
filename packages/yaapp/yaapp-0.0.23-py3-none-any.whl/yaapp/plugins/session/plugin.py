"""
Session handling plugin for YAAPP framework.
Provides HTTP header-based session management with pluggable storage backends.
Based on MCP (Model Context Protocol) session management patterns.
"""

import json
import threading
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from yaapp import yaapp

from ...result import Ok, Result


@runtime_checkable
class SessionStorage(Protocol):
    """Protocol for session storage backends."""

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by ID."""
        ...

    def set(
        self, session_id: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store session data with optional TTL."""
        ...

    def delete(self, session_id: str) -> bool:
        """Delete session data."""
        ...

    def cleanup_expired(self) -> int:
        """Remove expired sessions, return count removed."""
        ...


class MemorySessionStorage:
    """In-memory session storage with TTL support."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by ID."""
        with self._lock:
            # Check if expired
            if session_id in self._expiry:
                if time.time() > self._expiry[session_id]:
                    self.delete(session_id)
                    return None

            return self._sessions.get(session_id)

    def set(
        self, session_id: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store session data with optional TTL."""
        with self._lock:
            self._sessions[session_id] = data.copy()

            if ttl_seconds:
                self._expiry[session_id] = time.time() + ttl_seconds
            elif session_id in self._expiry:
                # Remove expiry if TTL not specified
                del self._expiry[session_id]

            return True

    def delete(self, session_id: str) -> bool:
        """Delete session data."""
        with self._lock:
            existed = session_id in self._sessions
            self._sessions.pop(session_id, None)
            self._expiry.pop(session_id, None)
            return existed

    def cleanup_expired(self) -> int:
        """Remove expired sessions, return count removed."""
        with self._lock:
            now = time.time()
            expired_ids = [sid for sid, expiry in self._expiry.items() if now > expiry]

            for session_id in expired_ids:
                self.delete(session_id)

            return len(expired_ids)


class FileSessionStorage:
    """File-based session storage with JSON serialization."""

    def __init__(self, storage_dir: str = "./sessions"):
        from pathlib import Path

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()

    def _get_session_file(self, session_id: str) -> "Path":
        """Get session file path."""
        return self.storage_dir / f"{session_id}.json"

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by ID."""
        with self._lock:
            session_file = self._get_session_file(session_id)

            if not session_file.exists():
                return None

            try:
                with open(session_file, "r") as f:
                    session_data = json.load(f)

                # Check TTL
                if "expires_at" in session_data:
                    if time.time() > session_data["expires_at"]:
                        self.delete(session_id)
                        return None

                return session_data.get("data", {})

            except (json.JSONDecodeError, IOError):
                return None

    def set(
        self, session_id: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store session data with optional TTL."""
        with self._lock:
            session_file = self._get_session_file(session_id)

            session_data = {
                "data": data,
                "created_at": time.time(),
                "updated_at": time.time(),
            }

            if ttl_seconds:
                session_data["expires_at"] = time.time() + ttl_seconds

            try:
                with open(session_file, "w") as f:
                    json.dump(session_data, f, indent=2)
                return True
            except IOError:
                return False

    def delete(self, session_id: str) -> bool:
        """Delete session data."""
        with self._lock:
            session_file = self._get_session_file(session_id)

            if session_file.exists():
                try:
                    session_file.unlink()
                    return True
                except IOError:
                    return False

            return False

    def cleanup_expired(self) -> int:
        """Remove expired sessions, return count removed."""
        with self._lock:
            now = time.time()
            removed_count = 0

            for session_file in self.storage_dir.glob("*.json"):
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)

                    if (
                        "expires_at" in session_data
                        and now > session_data["expires_at"]
                    ):
                        session_file.unlink()
                        removed_count += 1

                except (json.JSONDecodeError, IOError):
                    # Remove corrupted files
                    try:
                        session_file.unlink()
                        removed_count += 1
                    except IOError:
                        pass

            return removed_count


@yaapp.expose("session")
class SessionHandler:
    """HTTP header-based session handler for YAAPP framework."""

    def __init__(
        self,
        storage: Optional[SessionStorage] = None,
        session_header: str = "yaapp-session-id",
        default_ttl: Optional[int] = 3600,  # 1 hour
        auto_cleanup: bool = True,
    ):
        """
        Initialize session handler.

        Args:
            storage: Session storage backend (defaults to MemorySessionStorage)
            session_header: HTTP header name for session ID
            default_ttl: Default session TTL in seconds (None = no expiry)
            auto_cleanup: Whether to automatically cleanup expired sessions
        """
        self.storage = storage or MemorySessionStorage()
        self.session_header = session_header
        self.default_ttl = default_ttl
        self.auto_cleanup = auto_cleanup

        self._cleanup_thread = None
        if auto_cleanup:
            self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""

        def cleanup_worker():
            while True:
                try:
                    if hasattr(self.storage, "cleanup_expired"):
                        removed = self.storage.cleanup_expired()
                        if removed > 0:
                            print(f"Cleaned up {removed} expired sessions")
                except Exception as e:
                    print(f"Session cleanup error: {e}")

                time.sleep(300)  # Cleanup every 5 minutes

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        return str(uuid.uuid4()).replace("-", "")

    def create_session(
        self,
        initial_data: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """
        Create new session and return session ID.

        Args:
            initial_data: Initial session data
            ttl_seconds: Session TTL (uses default_ttl if None)

        Returns:
            New session ID
        """
        session_id = self.generate_session_id()
        session_data = initial_data or {}

        # Add metadata
        session_data.update(
            {
                "_created_at": datetime.now().isoformat(),
                "_last_accessed": datetime.now().isoformat(),
                "_access_count": 0,
            }
        )

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self.storage.set(session_id, session_data, ttl)

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data and update last accessed time.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found/expired
        """
        if not session_id:
            return None

        session_data = self.storage.get(session_id)
        if session_data is None:
            return None

        # Update access metadata
        session_data["_last_accessed"] = datetime.now().isoformat()
        session_data["_access_count"] = session_data.get("_access_count", 0) + 1

        # Save updated metadata
        ttl = self.default_ttl
        self.storage.set(session_id, session_data, ttl)

        return session_data

    def update_session(
        self, session_id: str, data: Dict[str, Any], merge: bool = True
    ) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Data to update
            merge: Whether to merge with existing data or replace

        Returns:
            True if successful, False if session not found
        """
        if not session_id:
            return False

        if merge:
            existing_data = self.storage.get(session_id)
            if existing_data is None:
                return False

            existing_data.update(data)
            session_data = existing_data
        else:
            session_data = data.copy()
            session_data.update(
                {
                    "_created_at": datetime.now().isoformat(),
                    "_last_accessed": datetime.now().isoformat(),
                    "_access_count": 0,
                }
            )

        ttl = self.default_ttl
        return self.storage.set(session_id, session_data, ttl)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if session was deleted, False if not found
        """
        if not session_id:
            return False

        return self.storage.delete(session_id)

    def extract_session_id_from_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Extract session ID from HTTP headers.

        Args:
            headers: HTTP headers dictionary (case-insensitive lookup)

        Returns:
            Session ID or None if not found
        """
        # Case-insensitive header lookup
        for header_name, header_value in headers.items():
            if header_name.lower() == self.session_header.lower():
                return header_value.strip()

        return None

    def inject_session_id_to_headers(
        self, headers: Dict[str, str], session_id: str
    ) -> Dict[str, str]:
        """
        Inject session ID into HTTP headers.

        Args:
            headers: Existing headers dictionary
            session_id: Session ID to inject

        Returns:
            Updated headers dictionary
        """
        updated_headers = headers.copy()
        updated_headers[self.session_header] = session_id
        return updated_headers

    def middleware_extract_session(
        self, request_headers: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Middleware helper: Extract and load session from request headers.

        Args:
            request_headers: HTTP request headers

        Returns:
            Session data or None if no valid session
        """
        session_id = self.extract_session_id_from_headers(request_headers)
        if not session_id:
            return None

        return self.get_session(session_id)

    def middleware_create_response_headers(
        self, session_id: str, existing_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Middleware helper: Create response headers with session ID.

        Args:
            session_id: Session ID to include
            existing_headers: Existing response headers

        Returns:
            Response headers with session ID
        """
        headers = existing_headers.copy() if existing_headers else {}
        return self.inject_session_id_to_headers(headers, session_id)

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics (if storage backend supports it).

        Returns:
            Statistics dictionary
        """
        stats = {
            "storage_type": type(self.storage).__name__,
            "session_header": self.session_header,
            "default_ttl": self.default_ttl,
            "auto_cleanup": self.auto_cleanup,
        }

        # Try to get storage-specific stats
        if hasattr(self.storage, "_sessions"):
            stats["active_sessions"] = len(self.storage._sessions)

        if hasattr(self.storage, "_expiry"):
            now = time.time()
            expired_count = sum(
                1 for expiry in self.storage._expiry.values() if now > expiry
            )
            stats["expired_sessions"] = expired_count

        return stats


# Convenience factory functions
def create_memory_session_handler(
    session_header: str = "yaapp-session-id", default_ttl: int = 3600
) -> SessionHandler:
    """Create session handler with in-memory storage."""
    return SessionHandler(
        storage=MemorySessionStorage(),
        session_header=session_header,
        default_ttl=default_ttl,
    )


def create_file_session_handler(
    storage_dir: str = "./sessions",
    session_header: str = "yaapp-session-id",
    default_ttl: int = 3600,
) -> SessionHandler:
    """Create session handler with file-based storage."""
    return SessionHandler(
        storage=FileSessionStorage(storage_dir),
        session_header=session_header,
        default_ttl=default_ttl,
    )
