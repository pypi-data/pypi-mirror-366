"""
Context tree implementation for YAAPP framework.
Replaces fragile string-based context navigation with proper tree structure.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ContextNode:
    """A node in the context tree."""
    name: str
    item: Optional[Any] = None
    children: Dict[str, 'ContextNode'] = field(default_factory=dict)
    parent: Optional['ContextNode'] = None
    
    def add_child(self, name: str, item: Any = None) -> 'ContextNode':
        """Add a child node."""
        child = ContextNode(name=name, item=item, parent=self)
        self.children[name] = child
        return child
    
    def get_child(self, name: str) -> Optional['ContextNode']:
        """Get a child node by name."""
        return self.children.get(name)
    
    def has_children(self) -> bool:
        """Check if node has children."""
        return len(self.children) > 0
    
    def is_leaf(self) -> bool:
        """Check if node is leaf (has no children)."""
        return not self.has_children()
    
    def get_path(self) -> List[str]:
        """Get path from root to this node."""
        if self.parent is None:
            return [] if self.name == "root" else [self.name]
        return self.parent.get_path() + [self.name]
    
    def get_path_string(self) -> str:
        """Get path as dot-separated string."""
        path = self.get_path()
        return ".".join(path) if path else ""


class ContextTree:
    """Tree structure for managing command contexts and navigation."""
    
    def __init__(self):
        self.root = ContextNode(name="root")
        self._current_node = self.root
        self._navigation_stack: List[ContextNode] = []
    
    def add_item(self, path: str, item: Any) -> None:
        """
        Add an item at the given path.
        
        Args:
            path: Dot-separated path (e.g., "math.operations.add")
            item: The item to store
        """
        if not path:
            raise ValueError("Path cannot be empty")
        
        parts = path.split(".")
        current_node = self.root
        
        # Navigate/create path
        for i, part in enumerate(parts):
            if part in current_node.children:
                current_node = current_node.children[part]
            else:
                # Create new node
                is_leaf = (i == len(parts) - 1)
                node_item = item if is_leaf else None
                current_node = current_node.add_child(part, node_item)
        
        # Set item on final node if not already set
        if current_node.item is None:
            current_node.item = item
    
    def get_item(self, path: str) -> Optional[Any]:
        """
        Get item at the given path.
        
        Args:
            path: Dot-separated path
            
        Returns:
            Item at path or None if not found
        """
        node = self._get_node_at_path(path)
        return node.item if node else None
    
    def remove_item(self, path: str) -> bool:
        """
        Remove item at the given path.
        
        Args:
            path: Dot-separated path
            
        Returns:
            True if item was removed, False if not found
        """
        if not path:
            return False
            
        parts = path.split(".")
        if len(parts) == 1:
            # Remove from root
            if parts[0] in self.root.children:
                del self.root.children[parts[0]]
                return True
            return False
        
        # Navigate to parent
        parent_path = ".".join(parts[:-1])
        parent_node = self._get_node_at_path(parent_path)
        
        if parent_node and parts[-1] in parent_node.children:
            del parent_node.children[parts[-1]]
            return True
        
        return False
    
    def _get_node_at_path(self, path: str) -> Optional[ContextNode]:
        """Get node at the given path."""
        if not path:
            return self.root
        
        parts = path.split(".")
        current_node = self.root
        
        for part in parts:
            if part in current_node.children:
                current_node = current_node.children[part]
            else:
                return None
        
        return current_node
    
    def get_current_context_items(self) -> Dict[str, Any]:
        """Get all items available in current context."""
        items = {}
        
        # Add direct children
        for name, child in self._current_node.children.items():
            if child.item is not None:
                items[name] = child.item
        
        return items
    
    def get_current_context_path(self) -> List[str]:
        """Get current context path as list."""
        return self._current_node.get_path()
    
    def get_current_context_string(self) -> str:
        """Get current context path as string."""
        return self._current_node.get_path_string()
    
    def can_enter_context(self, name: str) -> bool:
        """Check if we can enter the given context."""
        child = self._current_node.get_child(name)
        return child is not None and child.has_children()
    
    def is_leaf_command(self, name: str) -> bool:
        """Check if command is leaf (executable)."""
        child = self._current_node.get_child(name)
        return child is not None and child.is_leaf()
    
    def enter_context(self, name: str) -> bool:
        """
        Enter a context (navigate to child node).
        
        Args:
            name: Name of child context to enter
            
        Returns:
            True if successful, False if context doesn't exist or is leaf
        """
        if not self.can_enter_context(name):
            return False
        
        # Save current position to stack
        self._navigation_stack.append(self._current_node)
        self._current_node = self._current_node.children[name]
        return True
    
    def exit_context(self) -> bool:
        """
        Exit current context (go back to parent).
        
        Returns:
            True if successful, False if already at root
        """
        if not self._navigation_stack:
            return False  # Already at root
        
        self._current_node = self._navigation_stack.pop()
        return True
    
    def reset_to_root(self) -> None:
        """Reset navigation to root context."""
        self._current_node = self.root
        self._navigation_stack.clear()
    
    def get_all_paths(self) -> List[str]:
        """Get all paths in the tree."""
        paths = []
        
        def _collect_paths(node: ContextNode, current_path: str = ""):
            if node.item is not None and current_path:
                paths.append(current_path)
            
            for name, child in node.children.items():
                child_path = f"{current_path}.{name}" if current_path else name
                _collect_paths(child, child_path)
        
        _collect_paths(self.root)
        return paths
    
    def get_children_at_path(self, path: List[str]) -> Dict[str, Any]:
        """
        Get direct children at the given path.
        
        Args:
            path: Path as list of strings
            
        Returns:
            Dictionary of child name -> item
        """
        # Navigate to the target node
        current_node = self.root
        
        for part in path:
            if part in current_node.children:
                current_node = current_node.children[part]
            else:
                return {}  # Path doesn't exist
        
        # Return direct children with items
        children = {}
        for name, child in current_node.children.items():
            if child.item is not None:
                children[name] = child.item
        
        return children
    
    def print_tree(self, node: Optional[ContextNode] = None, indent: int = 0) -> None:
        """Print tree structure for debugging."""
        if node is None:
            node = self.root
        
        prefix = "  " * indent
        item_info = f" [{type(node.item).__name__}]" if node.item else ""
        print(f"{prefix}{node.name}{item_info}")
        
        for child in node.children.values():
            self.print_tree(child, indent + 1)