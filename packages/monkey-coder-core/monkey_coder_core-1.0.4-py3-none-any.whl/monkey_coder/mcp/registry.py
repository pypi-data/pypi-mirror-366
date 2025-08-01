"""
MCP Server Registry - Central registry of available MCP servers
Manages server discovery, capabilities, and metadata
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class ServerMetadata:
    """Metadata about an MCP server"""
    name: str
    display_name: str
    description: str
    author: str
    version: str
    repository: Optional[str] = None
    documentation: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    installation: Dict[str, Any] = field(default_factory=dict)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    
    
class ServerSource(Enum):
    """Source of server definition"""
    BUILTIN = "builtin"
    OFFICIAL = "official"
    COMMUNITY = "community"
    LOCAL = "local"
    

class MCPServerRegistry:
    """
    Central registry for MCP servers
    Manages available servers and their metadata
    """
    
    # Built-in servers that ship with Monkey Coder
    BUILTIN_SERVERS = {
        "filesystem": ServerMetadata(
            name="filesystem",
            display_name="Filesystem Server",
            description="Access and manipulate files and directories",
            author="Monkey Coder Team",
            version="1.0.0",
            repository="https://github.com/GaryOcean428/monkey-coder",
            documentation="https://docs.monkeycoder.dev/mcp/filesystem",
            tags=["file", "directory", "io", "builtin"],
            capabilities=["read", "write", "search", "watch"],
            installation={"type": "builtin"},
            config_schema={
                "type": "object",
                "properties": {
                    "allowed_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of allowed file paths"
                    },
                    "watch_enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable file watching"
                    }
                },
                "required": ["allowed_paths"]
            }
        ),
        "github": ServerMetadata(
            name="github",
            display_name="GitHub Server",
            description="Interact with GitHub repositories, issues, and PRs",
            author="Monkey Coder Team",
            version="1.0.0",
            repository="https://github.com/GaryOcean428/monkey-coder",
            documentation="https://docs.monkeycoder.dev/mcp/github",
            tags=["github", "git", "repository", "builtin"],
            capabilities=["repos", "issues", "pull_requests", "search"],
            installation={"type": "builtin"},
            config_schema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "GitHub personal access token"
                    },
                    "default_owner": {
                        "type": "string",
                        "description": "Default repository owner"
                    }
                },
                "required": ["token"]
            }
        ),
        "browser": ServerMetadata(
            name="browser",
            display_name="Browser Server",
            description="Web browsing and scraping capabilities",
            author="Monkey Coder Team",
            version="1.0.0",
            repository="https://github.com/GaryOcean428/monkey-coder",
            documentation="https://docs.monkeycoder.dev/mcp/browser",
            tags=["web", "browser", "scraping", "builtin"],
            capabilities=["navigate", "scrape", "screenshot", "interact"],
            installation={"type": "builtin"},
            config_schema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "default": True,
                        "description": "Run browser in headless mode"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Default timeout in milliseconds"
                    }
                }
            }
        ),
        "database": ServerMetadata(
            name="database",
            display_name="Database Server",
            description="Database operations and schema management",
            author="Monkey Coder Team",
            version="1.0.0",
            repository="https://github.com/GaryOcean428/monkey-coder",
            documentation="https://docs.monkeycoder.dev/mcp/database",
            tags=["database", "sql", "schema", "builtin"],
            capabilities=["query", "schema", "migrate", "backup"],
            installation={"type": "builtin"},
            config_schema={
                "type": "object",
                "properties": {
                    "connection_string": {
                        "type": "string",
                        "description": "Database connection string"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["postgres", "mysql", "sqlite"],
                        "description": "Database type"
                    }
                },
                "required": ["connection_string", "type"]
            }
        )
    }
    
    # Official MCP servers from modelcontextprotocol
    OFFICIAL_SERVERS = {
        "@modelcontextprotocol/server-brave-search": ServerMetadata(
            name="brave-search",
            display_name="Brave Search",
            description="Web search using Brave Search API",
            author="Anthropic",
            version="0.1.0",
            repository="https://github.com/modelcontextprotocol/servers",
            tags=["search", "web", "official"],
            capabilities=["search"],
            installation={
                "type": "npm",
                "package": "@modelcontextprotocol/server-brave-search"
            },
            config_schema={
                "type": "object",
                "properties": {
                    "apiKey": {
                        "type": "string",
                        "description": "Brave Search API key"
                    }
                },
                "required": ["apiKey"]
            }
        ),
        "@modelcontextprotocol/server-postgres": ServerMetadata(
            name="postgres",
            display_name="PostgreSQL",
            description="PostgreSQL database operations",
            author="Anthropic",
            version="0.1.0",
            repository="https://github.com/modelcontextprotocol/servers",
            tags=["database", "postgres", "sql", "official"],
            capabilities=["query", "schema"],
            installation={
                "type": "npm",
                "package": "@modelcontextprotocol/server-postgres"
            },
            config_schema={
                "type": "object",
                "properties": {
                    "connectionString": {
                        "type": "string",
                        "description": "PostgreSQL connection string"
                    }
                },
                "required": ["connectionString"]
            }
        )
    }
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize the registry
        
        Args:
            registry_path: Path to custom registry file
        """
        self.registry_path = registry_path or Path.home() / ".monkey-coder" / "mcp-registry.json"
        self.custom_servers: Dict[str, ServerMetadata] = {}
        self._load_custom_registry()
        
    def _load_custom_registry(self):
        """Load custom server definitions from registry file"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    
                for server_id, server_data in data.get("servers", {}).items():
                    self.custom_servers[server_id] = ServerMetadata(**server_data)
                    
                logger.info(f"Loaded {len(self.custom_servers)} custom servers from registry")
                
            except Exception as e:
                logger.error(f"Failed to load custom registry: {e}")
                
    def _save_custom_registry(self):
        """Save custom server definitions to registry file"""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "servers": {
                    server_id: {
                        "name": server.name,
                        "display_name": server.display_name,
                        "description": server.description,
                        "author": server.author,
                        "version": server.version,
                        "repository": server.repository,
                        "documentation": server.documentation,
                        "tags": server.tags,
                        "capabilities": server.capabilities,
                        "installation": server.installation,
                        "config_schema": server.config_schema
                    }
                    for server_id, server in self.custom_servers.items()
                }
            }
            
            with open(self.registry_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("Saved custom registry")
            
        except Exception as e:
            logger.error(f"Failed to save custom registry: {e}")
            
    def get_all_servers(self) -> Dict[str, ServerMetadata]:
        """Get all available servers"""
        servers = {}
        servers.update(self.BUILTIN_SERVERS)
        servers.update(self.OFFICIAL_SERVERS)
        servers.update(self.custom_servers)
        return servers
        
    def get_server(self, server_id: str) -> Optional[ServerMetadata]:
        """Get metadata for a specific server"""
        # Check builtin first
        if server_id in self.BUILTIN_SERVERS:
            return self.BUILTIN_SERVERS[server_id]
            
        # Check official
        if server_id in self.OFFICIAL_SERVERS:
            return self.OFFICIAL_SERVERS[server_id]
            
        # Check custom
        if server_id in self.custom_servers:
            return self.custom_servers[server_id]
            
        return None
        
    def search_servers(self, query: str, tags: Optional[List[str]] = None) -> List[ServerMetadata]:
        """
        Search for servers by query and/or tags
        
        Args:
            query: Search query (searches name, display_name, description)
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching servers
        """
        results = []
        query_lower = query.lower() if query else ""
        
        for server in self.get_all_servers().values():
            # Check query match
            if query:
                if not any(
                    query_lower in field.lower()
                    for field in [server.name, server.display_name, server.description]
                ):
                    continue
                    
            # Check tag match
            if tags:
                if not any(tag in server.tags for tag in tags):
                    continue
                    
            results.append(server)
            
        return results
        
    def register_server(self, server_id: str, metadata: ServerMetadata) -> bool:
        """
        Register a custom server
        
        Args:
            server_id: Unique server identifier
            metadata: Server metadata
            
        Returns:
            True if registered successfully
        """
        if server_id in self.BUILTIN_SERVERS or server_id in self.OFFICIAL_SERVERS:
            logger.error(f"Cannot override builtin/official server: {server_id}")
            return False
            
        self.custom_servers[server_id] = metadata
        self._save_custom_registry()
        logger.info(f"Registered custom server: {server_id}")
        return True
        
    def unregister_server(self, server_id: str) -> bool:
        """
        Unregister a custom server
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if unregistered successfully
        """
        if server_id not in self.custom_servers:
            logger.error(f"Server not found in custom registry: {server_id}")
            return False
            
        del self.custom_servers[server_id]
        self._save_custom_registry()
        logger.info(f"Unregistered custom server: {server_id}")
        return True
        
    def get_installation_command(self, server_id: str) -> Optional[str]:
        """
        Get installation command for a server
        
        Args:
            server_id: Server identifier
            
        Returns:
            Installation command or None
        """
        server = self.get_server(server_id)
        if not server:
            return None
            
        install = server.installation
        install_type = install.get("type")
        
        if install_type == "builtin":
            return None  # No installation needed
        elif install_type == "npm":
            package = install.get("package", server_id)
            return f"npm install -g {package}"
        elif install_type == "pip":
            package = install.get("package", server_id)
            return f"pip install {package}"
        elif install_type == "docker":
            image = install.get("image", server_id)
            return f"docker pull {image}"
        elif install_type == "custom":
            return install.get("command")
            
        return None
        
    def get_servers_by_capability(self, capability: str) -> List[ServerMetadata]:
        """Get all servers that have a specific capability"""
        return [
            server for server in self.get_all_servers().values()
            if capability in server.capabilities
        ]
        
    def get_servers_by_tag(self, tag: str) -> List[ServerMetadata]:
        """Get all servers that have a specific tag"""
        return [
            server for server in self.get_all_servers().values()
            if tag in server.tags
        ]
