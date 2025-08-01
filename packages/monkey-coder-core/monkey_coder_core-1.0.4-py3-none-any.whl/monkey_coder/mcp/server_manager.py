"""
MCP Server Manager - Manages Model Context Protocol server connections
Handles server discovery, lifecycle, and health monitoring
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

from .client import MCPClient

logger = logging.getLogger(__name__)


class ServerStatus(Enum):
    """MCP server status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    UNHEALTHY = "unhealthy"


class ServerType(Enum):
    """MCP server type"""
    BUILTIN = "builtin"
    NPM = "npm"
    CUSTOM = "custom"
    DOCKER = "docker"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    type: ServerType
    enabled: bool = True
    command: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    health_check_interval: int = 30  # seconds
    restart_on_failure: bool = True
    max_restart_attempts: int = 3


@dataclass
class MCPServerInfo:
    """Runtime information about an MCP server"""
    config: MCPServerConfig
    status: ServerStatus
    client: Optional[MCPClient] = None
    process: Optional[asyncio.subprocess.Process] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    error_message: Optional[str] = None
    connected_at: Optional[datetime] = None
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)


class MCPServerManager:
    """
    Manages MCP server lifecycle and connections
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the MCP server manager
        
        Args:
            config_path: Path to MCP configuration file
        """
        self.servers: Dict[str, MCPServerInfo] = {}
        self.config_path = config_path or Path.home() / ".monkey-coder" / "mcp-config.yaml"
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown = False
        
    async def start(self):
        """Start the server manager and load configuration"""
        logger.info("Starting MCP Server Manager")
        await self.load_configuration()
        await self.start_enabled_servers()
        
    async def stop(self):
        """Stop all servers and cleanup"""
        logger.info("Stopping MCP Server Manager")
        self._shutdown = True
        
        # Cancel health checks
        for task in self._health_check_tasks.values():
            task.cancel()
            
        # Stop all servers
        for server_name in list(self.servers.keys()):
            await self.stop_server(server_name)
            
    async def load_configuration(self):
        """Load MCP server configuration from file"""
        if not self.config_path.exists():
            logger.info(f"No configuration file found at {self.config_path}")
            await self._create_default_config()
            return
            
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                config_content = f.read()
                # Expand environment variables in the YAML content
                config_content = os.path.expandvars(config_content)
                config_data = yaml.safe_load(config_content)
                
            for server_data in config_data.get('servers', []):
                # Also expand environment variables in individual fields
                environment = server_data.get('environment', {})
                # Expand environment variables in the environment dict values
                expanded_environment = {
                    key: os.path.expandvars(str(value)) if isinstance(value, str) else value
                    for key, value in environment.items()
                }
                
                config = MCPServerConfig(
                    name=server_data['name'],
                    type=ServerType(server_data['type']),
                    enabled=server_data.get('enabled', True),
                    command=server_data.get('command'),
                    package=server_data.get('package'),
                    version=server_data.get('version'),
                    config=server_data.get('config', {}),
                    environment=expanded_environment,
                    capabilities=server_data.get('capabilities', []),
                    health_check_interval=server_data.get('health_check_interval', 30),
                    restart_on_failure=server_data.get('restart_on_failure', True),
                    max_restart_attempts=server_data.get('max_restart_attempts', 3),
                )
                
                self.servers[config.name] = MCPServerInfo(
                    config=config,
                    status=ServerStatus.DISCONNECTED
                )
                
            logger.info(f"Loaded {len(self.servers)} server configurations")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            
    async def _create_default_config(self):
        """Create default MCP configuration"""
        default_config = {
            'servers': [
                {
                    'name': 'filesystem',
                    'type': 'builtin',
                    'enabled': True,
                    'config': {
                        'allowed_paths': ['~/projects', '~/documents']
                    }
                },
                {
                    'name': 'github',
                    'type': 'npm',
                    'package': '@modelcontextprotocol/server-github',
                    'enabled': False,
                    'config': {
                        'token': '${GITHUB_TOKEN}'
                    }
                }
            ],
            'default_servers': ['filesystem']
        }
        
        # Create config directory
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write default config
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
            
        logger.info(f"Created default configuration at {self.config_path}")
        
        # Load the default config
        await self.load_configuration()
        
    async def start_enabled_servers(self):
        """Start all enabled servers"""
        for server_name, server_info in self.servers.items():
            if server_info.config.enabled:
                await self.start_server(server_name)
                
    async def start_server(self, server_name: str) -> bool:
        """
        Start a specific MCP server
        
        Args:
            server_name: Name of the server to start
            
        Returns:
            True if server started successfully
        """
        if server_name not in self.servers:
            logger.error(f"Server '{server_name}' not found")
            return False
            
        server_info = self.servers[server_name]
        
        if server_info.status == ServerStatus.CONNECTED:
            logger.info(f"Server '{server_name}' is already connected")
            return True
            
        logger.info(f"Starting MCP server '{server_name}'")
        server_info.status = ServerStatus.CONNECTING
        
        try:
            # Prepare environment
            env = dict(os.environ)
            env.update(server_info.config.environment)
            
            # Expand environment variables in config
            config = self._expand_env_vars(server_info.config.config)
            
            # Start server process
            if server_info.config.type == ServerType.BUILTIN:
                # Built-in servers are Python modules
                await self._start_builtin_server(server_info, config)
            else:
                # Get server command for external servers
                command = await self._get_server_command(server_info.config)
                if not command:
                    raise ValueError(f"No command found for server '{server_name}'")
                # External servers are subprocess
                await self._start_external_server(server_info, command, env, config)
                
            # Start health monitoring
            if server_name not in self._health_check_tasks:
                task = asyncio.create_task(self._monitor_server_health(server_name))
                self._health_check_tasks[server_name] = task
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server '{server_name}': {e}")
            server_info.status = ServerStatus.ERROR
            server_info.error_message = str(e)
            return False
            
    async def _start_builtin_server(self, server_info: MCPServerInfo, config: Dict[str, Any]):
        """Start a built-in Python MCP server"""
        # Import and instantiate the server
        module_name = f".servers.{server_info.config.name}"
        try:
            from importlib import import_module
            server_module = import_module(module_name, package="monkey_coder.mcp")
            server_class = getattr(server_module, f"{server_info.config.name.title()}MCPServer")
            
            # Create server instance
            server = server_class(config)
            
            # Create client and connect
            # For built-in servers, pass the server name
            client = await MCPClient.connect(server_info.config.name)
            
            server_info.client = client
            server_info.status = ServerStatus.CONNECTED
            server_info.connected_at = datetime.now()
            
            # Get available tools and resources
            server_info.tools = list(client.tools.keys()) if hasattr(client, 'tools') else []
            server_info.resources = list(client.resources.keys()) if hasattr(client, 'resources') else []
            
            logger.info(f"Connected to built-in server '{server_info.config.name}'")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start built-in server: {e}")
            
    async def _start_external_server(self, server_info: MCPServerInfo, command: List[str],
                                   env: Dict[str, str], config: Dict[str, Any]):
        """Start an external MCP server using async subprocess"""
        try:
            # Start process using asyncio subprocess for non-blocking operation
            process = await asyncio.create_subprocess_exec(
                *command,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            server_info.process = process
            
            # Wait for server to be ready with timeout
            try:
                await asyncio.wait_for(asyncio.sleep(2), timeout=10)
            except asyncio.TimeoutError:
                logger.warning(f"Server startup timeout for '{server_info.config.name}'")
            
            # Connect client
            server_config = {
                "name": server_info.config.name,
                "command": command
            }
            client = await MCPClient.connect(server_config)
            
            server_info.client = client
            server_info.status = ServerStatus.CONNECTED
            server_info.connected_at = datetime.now()
            
            logger.info(f"Connected to external server '{server_info.config.name}'")
            
        except Exception as e:
            logger.error(f"Failed to start external server '{server_info.config.name}': {e}")
            server_info.status = ServerStatus.ERROR
            server_info.error_message = str(e)
            raise
        
    async def stop_server(self, server_name: str) -> bool:
        """
        Stop a specific MCP server
        
        Args:
            server_name: Name of the server to stop
            
        Returns:
            True if server stopped successfully
        """
        if server_name not in self.servers:
            logger.error(f"Server '{server_name}' not found")
            return False
            
        server_info = self.servers[server_name]
        
        logger.info(f"Stopping MCP server '{server_name}'")
        
        # Cancel health check
        if server_name in self._health_check_tasks:
            self._health_check_tasks[server_name].cancel()
            del self._health_check_tasks[server_name]
            
        # Disconnect client
        if server_info.client:
            await server_info.client.disconnect()
            server_info.client = None
            
        # Stop process with async termination
        if server_info.process:
            server_info.process.terminate()
            try:
                # Use asyncio.wait_for for timeout handling
                await asyncio.wait_for(server_info.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"Process for '{server_name}' didn't terminate gracefully, killing")
                server_info.process.kill()
                # Wait for kill to complete
                try:
                    await asyncio.wait_for(server_info.process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    logger.error(f"Failed to kill process for '{server_name}'")
            server_info.process = None
            
        server_info.status = ServerStatus.DISCONNECTED
        server_info.connected_at = None
        server_info.restart_count = 0
        
        logger.info(f"Server '{server_name}' stopped")
        return True
        
    async def restart_server(self, server_name: str) -> bool:
        """Restart a server"""
        await self.stop_server(server_name)
        await asyncio.sleep(1)
        return await self.start_server(server_name)
        
    async def _monitor_server_health(self, server_name: str):
        """Monitor server health with exponential backoff and circuit breaker patterns"""
        failure_count = 0
        backoff_delay = 1.0  # Start with 1 second
        max_backoff = 60.0   # Maximum 60 seconds
        
        while not self._shutdown:
            try:
                server_info = self.servers.get(server_name)
                if not server_info:
                    break
                    
                # Wait for health check interval with exponential backoff on failures
                delay = server_info.config.health_check_interval
                if failure_count > 0:
                    # Apply exponential backoff for failed health checks
                    delay = min(backoff_delay * (2 ** failure_count), max_backoff)
                
                await asyncio.sleep(delay)
                
                if server_info.status == ServerStatus.CONNECTED:
                    # Perform health check with timeout
                    try:
                        is_healthy = await asyncio.wait_for(
                            self._check_server_health(server_info), 
                            timeout=10.0
                        )
                        
                        if is_healthy:
                            # Reset failure count on successful health check
                            failure_count = 0
                            server_info.last_health_check = datetime.now()
                        else:
                            failure_count += 1
                            logger.warning(f"Server '{server_name}' health check failed (attempt {failure_count})")
                            
                            # Circuit breaker: mark as unhealthy after 3 consecutive failures
                            if failure_count >= 3:
                                server_info.status = ServerStatus.UNHEALTHY
                                
                                # Restart if configured and within retry limits
                                if (server_info.config.restart_on_failure and 
                                    server_info.restart_count < server_info.config.max_restart_attempts):
                                    
                                    logger.info(f"Attempting to restart server '{server_name}' (restart {server_info.restart_count + 1})")
                                    server_info.restart_count += 1
                                    
                                    if await self.restart_server(server_name):
                                        failure_count = 0  # Reset on successful restart
                                        logger.info(f"Successfully restarted server '{server_name}'")
                                    else:
                                        logger.error(f"Failed to restart server '{server_name}'")
                                else:
                                    logger.error(f"Server '{server_name}' exceeded maximum restart attempts")
                    
                    except asyncio.TimeoutError:
                        failure_count += 1
                        logger.warning(f"Health check timeout for server '{server_name}' (attempt {failure_count})")
                        
            except asyncio.CancelledError:
                logger.info(f"Health monitoring cancelled for server '{server_name}'")
                break
            except Exception as e:
                failure_count += 1
                logger.error(f"Error in health monitor for '{server_name}': {e}")
    
    async def _check_server_health(self, server_info: MCPServerInfo) -> bool:
        """Check if server is healthy with comprehensive validation"""
        try:
            if not server_info.client:
                return False
            
            # Check if process is still running (for external servers)
            if server_info.process:
                return_code = server_info.process.returncode
                if return_code is not None:
                    # Process has terminated
                    logger.warning(f"Server process for '{server_info.config.name}' has terminated with code {return_code}")
                    return False
            
            # TODO: In a real implementation, this would:
            # 1. Send a ping/health request to the MCP server
            # 2. Verify expected capabilities are available
            # 3. Check response time is within acceptable limits
            # 4. Validate server is not in an error state
            
            # For now, return True if client exists and process is running
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for '{server_info.config.name}': {e}")
            return False
            
    async def _get_server_command(self, config: MCPServerConfig) -> Optional[List[str]]:
        """Get command to start server"""
        if config.type == ServerType.BUILTIN:
            # Built-in servers use their name
            return None
        elif config.type == ServerType.NPM:
            # NPM package server
            return ["npx", config.package] if config.package else None
        elif config.type == ServerType.CUSTOM:
            # Custom command - handle string properly
            if isinstance(config.command, str):
                return config.command.split()
            return config.command
        elif config.type == ServerType.DOCKER:
            # Docker container
            return ["docker", "run", config.package] if config.package else None
        else:
            return None
            
    def _expand_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Expand environment variables in configuration"""
        result = {}
        
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                result[key] = os.environ.get(env_var, value)
            elif isinstance(value, dict):
                result[key] = self._expand_env_vars(value)
            else:
                result[key] = value
                
        return result
        
    async def list_servers(self) -> List[Dict[str, Any]]:
        """List all configured servers with their status"""
        servers = []
        
        for name, info in self.servers.items():
            servers.append({
                'name': name,
                'type': info.config.type.value,
                'status': info.status.value,
                'enabled': info.config.enabled,
                'tools': len(info.tools),
                'resources': len(info.resources),
                'connected_at': info.connected_at.isoformat() if info.connected_at else None,
                'error': info.error_message
            })
            
        return servers
        
    async def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a server"""
        if server_name not in self.servers:
            return None
            
        info = self.servers[server_name]
        
        return {
            'name': server_name,
            'type': info.config.type.value,
            'status': info.status.value,
            'enabled': info.config.enabled,
            'config': info.config.config,
            'capabilities': info.config.capabilities,
            'tools': info.tools,
            'resources': info.resources,
            'connected_at': info.connected_at.isoformat() if info.connected_at else None,
            'restart_count': info.restart_count,
            'error': info.error_message
        }
        
    async def install_server(self, package: str, name: Optional[str] = None) -> bool:
        """
        Install a new MCP server from npm package
        
        Args:
            package: NPM package name
            name: Optional custom name for the server
            
        Returns:
            True if installation successful
        """
        if not name:
            # Extract name from package
            name = package.split('/')[-1].replace('@modelcontextprotocol/server-', '')
            
        logger.info(f"Installing MCP server '{name}' from package '{package}'")
        
        try:
            # Install npm package globally using async subprocess
            process = await asyncio.create_subprocess_exec(
                "npm", "install", "-g", package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"npm install failed: {error_msg}")
                
            logger.info(f"Successfully installed MCP server package '{package}'")
            
            # Add to configuration
            config = MCPServerConfig(
                name=name,
                type=ServerType.NPM,
                package=package,
                enabled=False  # Disabled by default
            )
            
            self.servers[name] = MCPServerInfo(
                config=config,
                status=ServerStatus.DISCONNECTED
            )
            
            # Save configuration
            await self._save_configuration()
            
            logger.info(f"Successfully installed server '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install server: {e}")
            return False
            
    async def _save_configuration(self):
        """Save current configuration to file"""
        config_data = {
            'servers': [],
            'default_servers': []
        }
        
        for server_info in self.servers.values():
            server_data = {
                'name': server_info.config.name,
                'type': server_info.config.type.value,
                'enabled': server_info.config.enabled,
            }
            
            if server_info.config.command:
                server_data['command'] = server_info.config.command
            if server_info.config.package:
                server_data['package'] = server_info.config.package
            if server_info.config.version:
                server_data['version'] = server_info.config.version
            if server_info.config.config:
                server_data['config'] = server_info.config.config
            if server_info.config.environment:
                server_data['environment'] = server_info.config.environment
            if server_info.config.capabilities:
                server_data['capabilities'] = server_info.config.capabilities
                
            config_data['servers'].append(server_data)
            
        # Save to file
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
            
        logger.info("Configuration saved")
