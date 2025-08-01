"""
MCP Client for connecting to Model Context Protocol servers
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server: str


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    server: Optional[str] = None


class MCPClient:
    """
    Client for communicating with MCP servers
    Handles JSON-RPC communication over stdio
    """
    
    def __init__(self, server_name: str, command: List[str]):
        self.server_name = server_name
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._request_id = 0
        self._is_connected = False
        
    @classmethod
    async def connect(cls, server_config: Union[str, Dict[str, Any]]) -> 'MCPClient':
        """
        Connect to an MCP server
        
        Args:
            server_config: Either a server name (for built-in servers) or config dict
        """
        if isinstance(server_config, str):
            # Built-in server
            command = cls._get_builtin_server_command(server_config)
            server_name = server_config
        else:
            # Custom server config
            server_name = server_config.get("name", "custom")
            command = server_config.get("command", [])
            
        client = cls(server_name, command)
        await client._connect()
        return client
        
    @staticmethod
    def _get_builtin_server_command(server_name: str) -> List[str]:
        """Get command for built-in servers"""
        builtin_servers = {
            "filesystem": ["python", "-m", "monkey_coder.mcp.servers.filesystem"],
            "github": ["npx", "-y", "@modelcontextprotocol/server-github"],
            "browser": ["npx", "-y", "@modelcontextprotocol/server-browserbase"],
            "postgres": ["npx", "-y", "@modelcontextprotocol/server-postgres"],
        }
        
        if server_name not in builtin_servers:
            raise ValueError(f"Unknown built-in server: {server_name}")
            
        return builtin_servers[server_name]
        
    async def _connect(self) -> None:
        """Establish connection to MCP server"""
        try:
            # Start the server process
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            
            # Initialize connection
            await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "monkey-coder",
                    "version": "1.0.0"
                }
            })
            
            # List available tools
            tools_response = await self._send_request("tools/list", {})
            if "tools" in tools_response:
                for tool_data in tools_response["tools"]:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        input_schema=tool_data.get("inputSchema", {}),
                        server=self.server_name
                    )
                    self.tools[tool.name] = tool
                    
            # List available resources
            resources_response = await self._send_request("resources/list", {})
            if "resources" in resources_response:
                for resource_data in resources_response["resources"]:
                    resource = MCPResource(
                        uri=resource_data["uri"],
                        name=resource_data.get("name", ""),
                        description=resource_data.get("description", ""),
                        mime_type=resource_data.get("mimeType"),
                        server=self.server_name
                    )
                    self.resources[resource.uri] = resource
                    
            self._is_connected = True
            logger.info(f"Connected to MCP server: {self.server_name}")
            logger.info(f"Available tools: {list(self.tools.keys())}")
            logger.info(f"Available resources: {list(self.resources.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server_name}: {e}")
            raise
            
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process()),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                self.process.kill()
            finally:
                self.process = None
                self._is_connected = False
                logger.info(f"Disconnected from MCP server: {self.server_name}")
                
    async def _wait_for_process(self):
        """Wait for process to terminate"""
        if self.process:
            while self.process.poll() is None:
                await asyncio.sleep(0.1)
                
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server")
            
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        response = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "content" in response:
            return response["content"]
        elif "error" in response:
            raise RuntimeError(f"Tool error: {response['error']}")
        else:
            return response
            
    async def get_resource(self, uri: str) -> Any:
        """
        Get a resource from the MCP server
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server")
            
        response = await self._send_request("resources/read", {"uri": uri})
        
        if "contents" in response:
            return response["contents"]
        elif "error" in response:
            raise RuntimeError(f"Resource error: {response['error']}")
        else:
            return response
            
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to server"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Server process not running")
            
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line)
        self.process.stdin.flush()
        
        # Read response
        response_line = await self._read_response()
        response = json.loads(response_line)
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
            
        return response.get("result", {})
        
    async def _read_response(self) -> str:
        """Read response from server stdout"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Server process not running")
            
        # Read until we get a complete JSON response
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process.stdout.readline)
        
    def get_tools(self) -> List[MCPTool]:
        """Get list of available tools"""
        return list(self.tools.values())
        
    def get_resources(self) -> List[MCPResource]:
        """Get list of available resources"""
        return list(self.resources.values())
        
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._is_connected
