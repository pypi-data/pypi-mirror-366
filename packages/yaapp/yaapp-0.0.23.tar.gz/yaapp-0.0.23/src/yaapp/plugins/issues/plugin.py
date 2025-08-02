"""
Issues plugin - FIXED VERSION that actually works!
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from yaapp import yaapp
from yaapp.result import Ok, Result


@yaapp.expose("issues")
class Issues:
    """Issues management that calls storage plugin methods."""

    def __init__(self, config=None):
        """Initialize with configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered

    def create(
        self,
        title: str,
        description: str,
        reporter: str,
        priority: str = "medium",
        assignee: str = None,
    ) -> Result[str]:
        """Create a new issue."""
        issue_id = f"issue_{uuid.uuid4().hex[:8]}"

        issue = {
            "id": issue_id,
            "title": title,
            "description": description,
            "reporter": reporter,
            "priority": priority,
            "assignee": assignee,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Call storage plugin's set() method
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            result = storage_obj.set(key=issue_id, value=issue, namespace="issues")
            if result:
                return Ok(issue_id)
            else:
                return Result.error("Failed to store issue")
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

    def get(self, issue_id: str) -> Result[Optional[Dict[str, Any]]]:
        """Get issue by ID."""
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            result = storage_obj.get(key=issue_id, namespace="issues")
            return Ok(result)
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

    def update(self, issue_id: str, **updates) -> Result[bool]:
        """Update issue."""
        # Get current issue
        get_result = self.get(issue_id)
        if get_result.is_err():
            return get_result  # Pass through the error

        issue = get_result.unwrap()
        if not issue:
            return Result.error(f"Issue {issue_id} not found")

        # Apply updates
        issue.update(updates)
        issue["updated_at"] = datetime.now().isoformat()

        # Save back through storage
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            result = storage_obj.set(key=issue_id, value=issue, namespace="issues")
            if result:
                return Ok(True)
            else:
                return Result.error("Failed to update issue")
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

    def delete(self, issue_id: str) -> Result[bool]:
        """Delete issue."""
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            result = storage_obj.delete(key=issue_id, namespace="issues")
            return Ok(result)
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

    def list(
        self, status: str = None, assignee: str = None
    ) -> Result[List[Dict[str, Any]]]:
        """List issues with simple filtering."""
        # Get all issue keys through storage
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            keys = storage_obj.keys(pattern="issue_*", namespace="issues")
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

        issues = []

        for key in keys:
            try:
                issue = storage_obj.get(key=key, namespace="issues")
                if issue:
                    # Simple filtering
                    if status and issue.get("status") != status:
                        continue
                    if assignee and issue.get("assignee") != assignee:
                        continue
                    issues.append(issue)
            except Exception:
                continue  # Skip failed retrievals

        # Sort by creation date
        sorted_issues = sorted(
            issues, key=lambda x: x.get("created_at", ""), reverse=True
        )
        return Ok(sorted_issues)

    def assign(self, issue_id: str, assignee: str) -> Result[bool]:
        """Assign issue to user."""
        return self.update(issue_id, assignee=assignee)

    def close(self, issue_id: str, resolution: str = "fixed") -> Result[bool]:
        """Close issue."""
        return self.update(issue_id, status="closed", resolution=resolution)

    def reopen(self, issue_id: str) -> Result[bool]:
        """Reopen issue."""
        return self.update(issue_id, status="open")

    def add_comment(self, issue_id: str, text: str, author: str) -> Result[bool]:
        """Add comment to issue."""
        # Get current issue
        get_result = self.get(issue_id)
        if get_result.is_err():
            return get_result  # Pass through the error

        issue = get_result.unwrap()
        if not issue:
            return Result.error(f"Issue {issue_id} not found")

        # Create comment
        comment = {
            "id": f"comment_{uuid.uuid4().hex[:8]}",
            "text": text,
            "author": author,
            "created_at": datetime.now().isoformat(),
        }

        # Add to issue comments
        if "comments" not in issue:
            issue["comments"] = []
        issue["comments"].append(comment)
        issue["updated_at"] = datetime.now().isoformat()

        # Save through storage
        if not self.yaapp:
            return Result.error("Plugin not properly initialized with yaapp instance")

        storage_result = self.yaapp.get_registry_item("storage")
        if storage_result.is_err():
            return Result.error("Storage plugin not found")

        storage_obj = storage_result.unwrap()

        try:
            result = storage_obj.set(key=issue_id, value=issue, namespace="issues")
            if result:
                return Ok(True)
            else:
                return Result.error("Failed to save comment")
        except Exception as e:
            return Result.error(f"Storage error: {str(e)}")

    def get_comments(self, issue_id: str) -> Result[List[Dict[str, Any]]]:
        """Get all comments for an issue."""
        get_result = self.get(issue_id)
        if get_result.is_err():
            return get_result  # Pass through the error

        issue = get_result.unwrap()
        if not issue:
            return Result.error(f"Issue {issue_id} not found")

        return Ok(issue.get("comments", []))

