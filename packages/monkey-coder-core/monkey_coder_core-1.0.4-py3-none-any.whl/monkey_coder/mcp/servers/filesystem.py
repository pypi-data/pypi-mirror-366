"""
Filesystem MCP Server
Provides file and directory operations through MCP protocol
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Union
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)


class FilesystemMCPServer:
    """
    MCP server for filesystem operations
    Provides tools for reading, writing, searching, and managing files
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the filesystem server
        
        Args:
            config: Server configuration including allowed_paths
        """
        self.config = config
        self.allowed_paths = self._normalize_paths(config.get("allowed_paths", ["~"]))
        self.watch_enabled = config.get("watch_enabled", True)
        self._watchers: Dict[str, asyncio.Task] = {}
        
        # Define available tools
        self.tools = {
            "read_file": {
                "name": "read_file",
                "description": "Read the contents of a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to read"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path"]
                }
            },
            "write_file": {
                "name": "write_file",
                "description": "Write content to a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "Create parent directories if they don't exist",
                            "default": True
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            "list_directory": {
                "name": "list_directory",
                "description": "List files and directories in a path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List recursively",
                            "default": False
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter files",
                            "default": "*"
                        }
                    },
                    "required": ["path"]
                }
            },
            "create_directory": {
                "name": "create_directory",
                "description": "Create a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to create"
                        },
                        "parents": {
                            "type": "boolean",
                            "description": "Create parent directories if needed",
                            "default": True
                        }
                    },
                    "required": ["path"]
                }
            },
            "delete": {
                "name": "delete",
                "description": "Delete a file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to delete"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Delete directories recursively",
                            "default": False
                        }
                    },
                    "required": ["path"]
                }
            },
            "move": {
                "name": "move",
                "description": "Move or rename a file/directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source path"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination path"
                        }
                    },
                    "required": ["source", "destination"]
                }
            },
            "copy": {
                "name": "copy",
                "description": "Copy a file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source path"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination path"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Copy directories recursively",
                            "default": True
                        }
                    },
                    "required": ["source", "destination"]
                }
            },
            "search_files": {
                "name": "search_files",
                "description": "Search for files matching patterns",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory to search in"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (glob or regex)"
                        },
                        "content_pattern": {
                            "type": "string",
                            "description": "Pattern to search within files"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Search recursively",
                            "default": True
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 100
                        }
                    },
                    "required": ["path", "pattern"]
                }
            },
            "get_file_info": {
                "name": "get_file_info",
                "description": "Get detailed information about a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path"
                        }
                    },
                    "required": ["path"]
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "file://": {
                "uri": "file://",
                "name": "Local Files",
                "description": "Access local filesystem",
                "mimeType": "text/plain"
            }
        }
        
    def _normalize_paths(self, paths: List[str]) -> List[Path]:
        """Normalize and expand paths"""
        normalized = []
        for path in paths:
            p = Path(path).expanduser().resolve()
            normalized.append(p)
        return normalized
        
    def _is_path_allowed(self, path: Union[str, Path]) -> bool:
        """Check if a path is within allowed directories"""
        p = Path(path).expanduser().resolve()
        
        for allowed in self.allowed_paths:
            try:
                p.relative_to(allowed)
                return True
            except ValueError:
                continue
                
        return False
        
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
            
        try:
            if tool_name == "read_file":
                return await self._read_file(arguments)
            elif tool_name == "write_file":
                return await self._write_file(arguments)
            elif tool_name == "list_directory":
                return await self._list_directory(arguments)
            elif tool_name == "create_directory":
                return await self._create_directory(arguments)
            elif tool_name == "delete":
                return await self._delete(arguments)
            elif tool_name == "move":
                return await self._move(arguments)
            elif tool_name == "copy":
                return await self._copy(arguments)
            elif tool_name == "search_files":
                return await self._search_files(arguments)
            elif tool_name == "get_file_info":
                return await self._get_file_info(arguments)
            else:
                return {"error": f"Tool not implemented: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
            
    async def _read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        path = Path(args["path"]).expanduser()
        encoding = args.get("encoding", "utf-8")
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists():
            return {"error": f"File not found: {path}"}
            
        if not path.is_file():
            return {"error": f"Not a file: {path}"}
            
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
                
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }],
                "metadata": {
                    "path": str(path),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
            
    async def _write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write file contents"""
        path = Path(args["path"]).expanduser()
        content = args["content"]
        encoding = args.get("encoding", "utf-8")
        create_dirs = args.get("create_dirs", True)
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
                
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
                
            return {
                "content": [{
                    "type": "text",
                    "text": f"File written successfully: {path}"
                }],
                "metadata": {
                    "path": str(path),
                    "size": len(content.encode(encoding))
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to write file: {e}"}
            
    async def _list_directory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        path = Path(args["path"]).expanduser()
        recursive = args.get("recursive", False)
        pattern = args.get("pattern", "*")
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists():
            return {"error": f"Directory not found: {path}"}
            
        if not path.is_dir():
            return {"error": f"Not a directory: {path}"}
            
        try:
            items = []
            
            if recursive:
                for item in path.rglob(pattern):
                    relative = item.relative_to(path)
                    items.append({
                        "path": str(relative),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
            else:
                for item in path.glob(pattern):
                    items.append({
                        "path": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
                    
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(items, indent=2)
                }],
                "metadata": {
                    "path": str(path),
                    "count": len(items)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to list directory: {e}"}
            
    async def _create_directory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create directory"""
        path = Path(args["path"]).expanduser()
        parents = args.get("parents", True)
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        try:
            path.mkdir(parents=parents, exist_ok=True)
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Directory created: {path}"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to create directory: {e}"}
            
    async def _delete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Delete file or directory"""
        path = Path(args["path"]).expanduser()
        recursive = args.get("recursive", False)
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists():
            return {"error": f"Path not found: {path}"}
            
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                if recursive:
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.rmdir()
                    
            return {
                "content": [{
                    "type": "text",
                    "text": f"Deleted: {path}"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to delete: {e}"}
            
    async def _move(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Move/rename file or directory"""
        source = Path(args["source"]).expanduser()
        destination = Path(args["destination"]).expanduser()
        
        if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
            return {"error": "Path not allowed"}
            
        if not source.exists():
            return {"error": f"Source not found: {source}"}
            
        try:
            source.rename(destination)
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Moved {source} to {destination}"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to move: {e}"}
            
    async def _copy(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Copy file or directory"""
        source = Path(args["source"]).expanduser()
        destination = Path(args["destination"]).expanduser()
        recursive = args.get("recursive", True)
        
        if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
            return {"error": "Path not allowed"}
            
        if not source.exists():
            return {"error": f"Source not found: {source}"}
            
        try:
            import shutil
            
            if source.is_file():
                shutil.copy2(source, destination)
            elif source.is_dir() and recursive:
                shutil.copytree(source, destination)
            else:
                return {"error": "Cannot copy directory without recursive flag"}
                
            return {
                "content": [{
                    "type": "text",
                    "text": f"Copied {source} to {destination}"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to copy: {e}"}
            
    async def _search_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files"""
        path = Path(args["path"]).expanduser()
        pattern = args["pattern"]
        content_pattern = args.get("content_pattern")
        recursive = args.get("recursive", True)
        max_results = args.get("max_results", 100)
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists() or not path.is_dir():
            return {"error": f"Directory not found: {path}"}
            
        try:
            results = []
            count = 0
            
            glob_func = path.rglob if recursive else path.glob
            
            for file_path in glob_func(pattern):
                if count >= max_results:
                    break
                    
                if file_path.is_file():
                    match_info = {
                        "path": str(file_path.relative_to(path)),
                        "size": file_path.stat().st_size
                    }
                    
                    # Search content if pattern provided
                    if content_pattern:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content_pattern in content:
                                    # Find line with match
                                    lines = content.splitlines()
                                    for i, line in enumerate(lines):
                                        if content_pattern in line:
                                            match_info["match"] = {
                                                "line": i + 1,
                                                "content": line.strip()
                                            }
                                            break
                                    results.append(match_info)
                                    count += 1
                        except Exception:
                            pass  # Skip files that can't be read
                    else:
                        results.append(match_info)
                        count += 1
                        
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(results, indent=2)
                }],
                "metadata": {
                    "path": str(path),
                    "pattern": pattern,
                    "matches": len(results)
                }
            }
            
        except Exception as e:
            return {"error": f"Search failed: {e}"}
            
    async def _get_file_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get file information"""
        path = Path(args["path"]).expanduser()
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists():
            return {"error": f"Path not found: {path}"}
            
        try:
            stat = path.stat()
            
            info = {
                "path": str(path),
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
            }
            
            if path.is_file():
                mime_type, _ = mimetypes.guess_type(str(path))
                if mime_type:
                    info["mime_type"] = mime_type
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(info, indent=2)
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to get file info: {e}"}
            
    async def handle_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle resource request
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not uri.startswith("file://"):
            return {"error": f"Invalid URI scheme: {uri}"}
            
        path = Path(uri[7:])  # Remove file:// prefix
        
        if not self._is_path_allowed(path):
            return {"error": f"Path not allowed: {path}"}
            
        if not path.exists():
            return {"error": f"Resource not found: {path}"}
            
        try:
            if path.is_file():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": mimetypes.guess_type(str(path))[0] or "text/plain",
                        "text": content
                    }]
                }
            else:
                # Return directory listing
                items = []
                for item in path.iterdir():
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file"
                    })
                    
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(items, indent=2)
                    }]
                }
                
        except Exception as e:
            return {"error": f"Failed to read resource: {e}"}
