"""
Expose MCP runner to yaapp registry.
"""

from yaapp import yaapp
from .plugin import MCPRunner

# Expose the MCP runner to yaapp
@yaapp.expose
def mcp():
    """MCP (Model Context Protocol) server runner"""
    return MCPRunner()