"""
Built-in MCP servers for Monkey Coder
"""

from .filesystem import FilesystemMCPServer
from .github import GithubMCPServer
from .browser import BrowserMCPServer
from .database import DatabaseMCPServer

__all__ = [
    "FilesystemMCPServer",
    "GithubMCPServer", 
    "BrowserMCPServer",
    "DatabaseMCPServer"
]
