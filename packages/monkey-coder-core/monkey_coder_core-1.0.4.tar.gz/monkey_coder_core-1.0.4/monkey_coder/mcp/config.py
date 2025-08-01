"""
MCP Configuration Management
Handles loading, saving, and validating MCP server configurations
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
import yaml

from .server_manager import ServerType, MCPServerConfig
from .registry import MCPServerRegistry

logger = logging.getLogger(__name__)


@dataclass
class MCPGlobalConfig:
    """Global MCP configuration"""
    enabled: bool = True
    default_servers: List[str] = field(default_factory=list)
    auto_start: bool = True
    log_level: str = "INFO"
    health_check_interval: int = 30
    max_restart_attempts: int = 3
    

class MCPConfigManager:
    """
    Manages MCP configuration
    Handles global and per-server configuration
    """
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "global": {
            "enabled": True,
            "default_servers": ["filesystem"],
            "auto_start": True,
            "log_level": "INFO",
            "health_check_interval": 30,
            "max_restart_attempts": 3
        },
        "servers": [
            {
                "name": "filesystem",
                "type": "builtin",
                "enabled": True,
                "config": {
                    "allowed_paths": ["~/projects", "~/documents"]
                }
            }
        ]
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or Path.home() / ".monkey-coder" / "mcp-config.yaml"
        self.registry = MCPServerRegistry()
        self.config_data: Dict[str, Any] = {}
        self.global_config: MCPGlobalConfig = MCPGlobalConfig()
        self.server_configs: Dict[str, MCPServerConfig] = {}
        
        self.load_config()
        
    def load_config(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if loaded successfully
        """
        if not self.config_path.exists():
            logger.info(f"No configuration found at {self.config_path}, creating default")
            self.create_default_config()
            return True
            
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)
                
            # Load global config
            global_data = self.config_data.get("global", {})
            self.global_config = MCPGlobalConfig(
                enabled=global_data.get("enabled", True),
                default_servers=global_data.get("default_servers", []),
                auto_start=global_data.get("auto_start", True),
                log_level=global_data.get("log_level", "INFO"),
                health_check_interval=global_data.get("health_check_interval", 30),
                max_restart_attempts=global_data.get("max_restart_attempts", 3)
            )
            
            # Load server configs
            self.server_configs = {}
            for server_data in self.config_data.get("servers", []):
                config = self._parse_server_config(server_data)
                if config:
                    self.server_configs[config.name] = config
                    
            logger.info(f"Loaded configuration with {len(self.server_configs)} servers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
            
    def save_config(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if saved successfully
        """
        try:
            # Prepare config data
            self.config_data = {
                "version": "1.0.0",
                "global": {
                    "enabled": self.global_config.enabled,
                    "default_servers": self.global_config.default_servers,
                    "auto_start": self.global_config.auto_start,
                    "log_level": self.global_config.log_level,
                    "health_check_interval": self.global_config.health_check_interval,
                    "max_restart_attempts": self.global_config.max_restart_attempts
                },
                "servers": []
            }
            
            # Add server configs
            for config in self.server_configs.values():
                server_data = {
                    "name": config.name,
                    "type": config.type.value,
                    "enabled": config.enabled,
                }
                
                if config.command:
                    server_data["command"] = config.command
                if config.package:
                    server_data["package"] = config.package
                if config.version:
                    server_data["version"] = config.version
                # Only add non-empty config and environment
                if config.config and isinstance(config.config, dict):
                    server_data["config"] = config.config
                if config.environment and isinstance(config.environment, dict):
                    server_data["environment"] = config.environment
                    
                self.config_data["servers"].append(server_data)
                
            # Create directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, sort_keys=False)
                
            logger.info("Saved configuration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
            
    def create_default_config(self):
        """Create default configuration"""
        self.config_data = self.DEFAULT_CONFIG.copy()
        
        # Set global config
        global_data = self.config_data["global"]
        self.global_config = MCPGlobalConfig(**global_data)
        
        # Set server configs
        self.server_configs = {}
        for server_data in self.config_data["servers"]:
            config = self._parse_server_config(server_data)
            if config:
                self.server_configs[config.name] = config
                
        # Save to file
        self.save_config()
        
    def _parse_server_config(self, data: Dict[str, Any]) -> Optional[MCPServerConfig]:
        """Parse server configuration from dict"""
        try:
            # Get server metadata from registry
            server_name = data.get("name")
            if not server_name:
                logger.error("Server configuration missing 'name' field")
                return None
                
            metadata = self.registry.get_server(server_name)
            
            # Determine capabilities from metadata
            capabilities = []
            if metadata:
                capabilities = metadata.capabilities
                
            return MCPServerConfig(
                name=server_name,
                type=ServerType(data.get("type", "custom")),
                enabled=data.get("enabled", True),
                command=data.get("command"),
                package=data.get("package"),
                version=data.get("version"),
                config=data.get("config", {}),
                environment=data.get("environment", {}),
                capabilities=capabilities,
                health_check_interval=data.get("health_check_interval", self.global_config.health_check_interval),
                restart_on_failure=data.get("restart_on_failure", True),
                max_restart_attempts=data.get("max_restart_attempts", self.global_config.max_restart_attempts)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse server config: {e}")
            return None
            
    def add_server(self, server_id: str, config: Optional[Dict[str, Any]] = None, 
                   enabled: bool = True) -> bool:
        """
        Add a server to configuration
        
        Args:
            server_id: Server identifier (name or package)
            config: Optional server-specific configuration
            enabled: Whether to enable the server
            
        Returns:
            True if added successfully
        """
        # Get metadata from registry
        metadata = self.registry.get_server(server_id)
        if not metadata:
            logger.error(f"Server not found in registry: {server_id}")
            return False
            
        # Determine type and package
        install = metadata.installation
        server_type = ServerType(install.get("type", "custom"))
        package = install.get("package") if server_type == ServerType.NPM else None
        
        # Create server config
        server_config = MCPServerConfig(
            name=metadata.name,
            type=server_type,
            enabled=enabled,
            package=package,
            config=config or {},
            capabilities=metadata.capabilities,
            health_check_interval=self.global_config.health_check_interval,
            restart_on_failure=True,
            max_restart_attempts=self.global_config.max_restart_attempts
        )
        
        # Add to configs
        self.server_configs[metadata.name] = server_config
        
        # Save config
        return self.save_config()
        
    def remove_server(self, server_name: str) -> bool:
        """
        Remove a server from configuration
        
        Args:
            server_name: Server name
            
        Returns:
            True if removed successfully
        """
        if server_name not in self.server_configs:
            logger.error(f"Server not in configuration: {server_name}")
            return False
            
        del self.server_configs[server_name]
        
        # Remove from default servers
        if server_name in self.global_config.default_servers:
            self.global_config.default_servers.remove(server_name)
            
        return self.save_config()
        
    def update_server_config(self, server_name: str, config: Dict[str, Any]) -> bool:
        """
        Update server-specific configuration
        
        Args:
            server_name: Server name
            config: New configuration
            
        Returns:
            True if updated successfully
        """
        if server_name not in self.server_configs:
            logger.error(f"Server not in configuration: {server_name}")
            return False
            
        # Validate config against schema
        metadata = self.registry.get_server(server_name)
        if metadata and metadata.config_schema:
            if not self._validate_config(config, metadata.config_schema):
                return False
                
        # Update config
        self.server_configs[server_name].config = config
        return self.save_config()
        
    def enable_server(self, server_name: str) -> bool:
        """Enable a server"""
        if server_name not in self.server_configs:
            logger.error(f"Server not in configuration: {server_name}")
            return False
            
        self.server_configs[server_name].enabled = True
        return self.save_config()
        
    def disable_server(self, server_name: str) -> bool:
        """Disable a server"""
        if server_name not in self.server_configs:
            logger.error(f"Server not in configuration: {server_name}")
            return False
            
        self.server_configs[server_name].enabled = False
        return self.save_config()
        
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific server"""
        return self.server_configs.get(server_name)
        
    def get_all_server_configs(self) -> Dict[str, MCPServerConfig]:
        """Get all server configurations"""
        return self.server_configs.copy()
        
    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled server names"""
        return [
            name for name, config in self.server_configs.items()
            if config.enabled
        ]
        
    def set_default_servers(self, server_names: List[str]) -> bool:
        """Set default servers to auto-start"""
        # Validate all servers exist
        for name in server_names:
            if name not in self.server_configs:
                logger.error(f"Server not in configuration: {name}")
                return False
                
        self.global_config.default_servers = server_names
        return self.save_config()
        
    def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against JSON schema
        
        Args:
            config: Configuration to validate
            schema: JSON schema
            
        Returns:
            True if valid
        """
        # Simple validation - check required fields
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for req_field in required:
            if req_field not in config:
                logger.error(f"Missing required field: {req_field}")
                return False
                
        # Check types
        for field_name, value in config.items():
            if field_name in properties:
                prop_schema = properties[field_name]
                expected_type = prop_schema.get("type")
                
                if expected_type:
                    actual_type = type(value).__name__
                    type_map = {
                        "string": "str",
                        "integer": "int",
                        "number": "float",
                        "boolean": "bool",
                        "array": "list",
                        "object": "dict"
                    }
                    
                    if type_map.get(expected_type) != actual_type:
                        # Handle special cases
                        if expected_type == "number" and actual_type == "int":
                            continue  # int is acceptable for number
                        logger.error(f"Invalid type for {field_name}: expected {expected_type}, got {actual_type}")
                        return False
                        
        return True
        
    def export_config(self, output_path: Path) -> bool:
        """Export configuration to file"""
        try:
            with open(output_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
            return False
            
    def import_config(self, input_path: Path) -> bool:
        """Import configuration from file"""
        try:
            with open(input_path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Validate structure
            if "version" not in data or "servers" not in data:
                logger.error("Invalid configuration format")
                return False
                
            # Load the new config
            self.config_path = input_path
            return self.load_config()
            
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False
