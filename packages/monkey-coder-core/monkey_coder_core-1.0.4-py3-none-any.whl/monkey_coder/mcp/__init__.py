"""
Model Context Protocol (MCP) integration for Monkey Coder
Provides tools and resources from external servers
"""

from .client import MCPClient, MCPTool, MCPResource
from .server_manager import MCPServerManager, MCPServerConfig
from .registry import MCPServerRegistry

__all__ = [
    "MCPClient",
    "MCPTool",
    "MCPResource",
    "MCPServerManager",
    "MCPServerConfig",
    "MCPServerRegistry",
]
