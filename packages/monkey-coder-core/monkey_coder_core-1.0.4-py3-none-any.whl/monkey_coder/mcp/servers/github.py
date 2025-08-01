"""
GitHub MCP Server
Provides GitHub operations through MCP protocol
"""

import os
import json
import logging
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)


class GithubMCPServer:
    """
    MCP server for GitHub operations
    Provides tools for repository management, issues, and PRs
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GitHub server
        
        Args:
            config: Server configuration including token
        """
        self.config = config
        self.token = config.get("token", os.environ.get("GITHUB_TOKEN"))
        self.default_owner = config.get("default_owner")
        self.base_url = "https://api.github.com"
        
        if not self.token:
            logger.warning("No GitHub token provided. Some operations may be limited.")
            
        # Define available tools
        self.tools = {
            "get_repository": {
                "name": "get_repository",
                "description": "Get information about a repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            },
            "list_repositories": {
                "name": "list_repositories",
                "description": "List repositories for a user/org",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "User or organization name"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["all", "owner", "member"],
                            "description": "Repository type filter",
                            "default": "all"
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["created", "updated", "pushed", "full_name"],
                            "description": "Sort field",
                            "default": "updated"
                        }
                    },
                    "required": ["owner"]
                }
            },
            "create_repository": {
                "name": "create_repository",
                "description": "Create a new repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description"
                        },
                        "private": {
                            "type": "boolean",
                            "description": "Make repository private",
                            "default": False
                        },
                        "auto_init": {
                            "type": "boolean",
                            "description": "Initialize with README",
                            "default": True
                        }
                    },
                    "required": ["name"]
                }
            },
            "get_file": {
                "name": "get_file",
                "description": "Get file contents from repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "path": {
                            "type": "string",
                            "description": "File path"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Branch/tag/commit ref",
                            "default": "main"
                        }
                    },
                    "required": ["owner", "repo", "path"]
                }
            },
            "create_or_update_file": {
                "name": "create_or_update_file",
                "description": "Create or update a file in repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "path": {
                            "type": "string",
                            "description": "File path"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content"
                        },
                        "message": {
                            "type": "string",
                            "description": "Commit message"
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name",
                            "default": "main"
                        },
                        "sha": {
                            "type": "string",
                            "description": "SHA of file being replaced (for updates)"
                        }
                    },
                    "required": ["owner", "repo", "path", "content", "message"]
                }
            },
            "list_issues": {
                "name": "list_issues",
                "description": "List repository issues",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "Issue state",
                            "default": "open"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by labels"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Filter by assignee"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            },
            "create_issue": {
                "name": "create_issue",
                "description": "Create a new issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels"
                        },
                        "assignees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Assignees"
                        }
                    },
                    "required": ["owner", "repo", "title"]
                }
            },
            "update_issue": {
                "name": "update_issue",
                "description": "Update an existing issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "Issue number"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title"
                        },
                        "body": {
                            "type": "string",
                            "description": "New body"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed"],
                            "description": "Issue state"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels"
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                }
            },
            "list_pull_requests": {
                "name": "list_pull_requests",
                "description": "List repository pull requests",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "PR state",
                            "default": "open"
                        },
                        "base": {
                            "type": "string",
                            "description": "Filter by base branch"
                        },
                        "head": {
                            "type": "string",
                            "description": "Filter by head branch"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            },
            "create_pull_request": {
                "name": "create_pull_request",
                "description": "Create a new pull request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "title": {
                            "type": "string",
                            "description": "PR title"
                        },
                        "body": {
                            "type": "string",
                            "description": "PR body"
                        },
                        "head": {
                            "type": "string",
                            "description": "Head branch"
                        },
                        "base": {
                            "type": "string",
                            "description": "Base branch",
                            "default": "main"
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Create as draft",
                            "default": False
                        }
                    },
                    "required": ["owner", "repo", "title", "head"]
                }
            },
            "search_code": {
                "name": "search_code",
                "description": "Search for code across GitHub",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "language": {
                            "type": "string",
                            "description": "Filter by language"
                        },
                        "user": {
                            "type": "string",
                            "description": "Filter by user"
                        },
                        "org": {
                            "type": "string",
                            "description": "Filter by organization"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Filter by repository (owner/repo)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "github://": {
                "uri": "github://",
                "name": "GitHub",
                "description": "Access GitHub repositories and data",
                "mimeType": "application/json"
            }
        }
        
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for GitHub API"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Monkey-Coder-MCP"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        return headers
        
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
            # Apply default owner if not provided
            if "owner" in arguments and not arguments["owner"] and self.default_owner:
                arguments["owner"] = self.default_owner
                
            if tool_name == "get_repository":
                return await self._get_repository(arguments)
            elif tool_name == "list_repositories":
                return await self._list_repositories(arguments)
            elif tool_name == "create_repository":
                return await self._create_repository(arguments)
            elif tool_name == "get_file":
                return await self._get_file(arguments)
            elif tool_name == "create_or_update_file":
                return await self._create_or_update_file(arguments)
            elif tool_name == "list_issues":
                return await self._list_issues(arguments)
            elif tool_name == "create_issue":
                return await self._create_issue(arguments)
            elif tool_name == "update_issue":
                return await self._update_issue(arguments)
            elif tool_name == "list_pull_requests":
                return await self._list_pull_requests(arguments)
            elif tool_name == "create_pull_request":
                return await self._create_pull_request(arguments)
            elif tool_name == "search_code":
                return await self._search_code(arguments)
            else:
                return {"error": f"Tool not implemented: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
            
    async def _get_repository(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get repository information"""
        owner = args["owner"]
        repo = args["repo"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to get repository: {response.text}"}
                
            data = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(data, indent=2)
                }]
            }
            
    async def _list_repositories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List repositories"""
        owner = args["owner"]
        repo_type = args.get("type", "all")
        sort = args.get("sort", "updated")
        
        params = {
            "type": repo_type,
            "sort": sort,
            "per_page": 100
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{owner}/repos",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code != 200:
                # Try org endpoint
                response = await client.get(
                    f"{self.base_url}/orgs/{owner}/repos",
                    headers=self._get_headers(),
                    params=params
                )
                
            if response.status_code != 200:
                return {"error": f"Failed to list repositories: {response.text}"}
                
            repos = response.json()
            
            # Extract key information
            repo_list = []
            for repo in repos:
                repo_list.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "private": repo["private"],
                    "stars": repo["stargazers_count"],
                    "language": repo["language"],
                    "updated_at": repo["updated_at"]
                })
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(repo_list, indent=2)
                }],
                "metadata": {
                    "count": len(repo_list)
                }
            }
            
    async def _create_repository(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new repository"""
        data = {
            "name": args["name"],
            "description": args.get("description", ""),
            "private": args.get("private", False),
            "auto_init": args.get("auto_init", True)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/user/repos",
                headers=self._get_headers(),
                json=data
            )
            
            if response.status_code != 201:
                return {"error": f"Failed to create repository: {response.text}"}
                
            repo = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Repository created: {repo['full_name']}\nURL: {repo['html_url']}"
                }]
            }
            
    async def _get_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get file contents"""
        owner = args["owner"]
        repo = args["repo"]
        path = args["path"]
        ref = args.get("ref", "main")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                params={"ref": ref}
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to get file: {response.text}"}
                
            data = response.json()
            
            if data.get("type") != "file":
                return {"error": "Path is not a file"}
                
            # Decode base64 content
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }],
                "metadata": {
                    "path": path,
                    "sha": data["sha"],
                    "size": data["size"]
                }
            }
            
    async def _create_or_update_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update file"""
        owner = args["owner"]
        repo = args["repo"]
        path = args["path"]
        content = args["content"]
        message = args["message"]
        branch = args.get("branch", "main")
        sha = args.get("sha")
        
        # Encode content to base64
        import base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
            
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                json=data
            )
            
            if response.status_code not in [200, 201]:
                return {"error": f"Failed to create/update file: {response.text}"}
                
            result = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"File {'updated' if sha else 'created'}: {path}\nCommit: {result['commit']['sha']}"
                }]
            }
            
    async def _list_issues(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List issues"""
        owner = args["owner"]
        repo = args["repo"]
        state = args.get("state", "open")
        labels = args.get("labels", [])
        assignee = args.get("assignee")
        
        params = {
            "state": state,
            "per_page": 100
        }
        
        if labels:
            params["labels"] = ",".join(labels)
        if assignee:
            params["assignee"] = assignee
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to list issues: {response.text}"}
                
            issues = response.json()
            
            # Extract key information
            issue_list = []
            for issue in issues:
                # Skip pull requests
                if "pull_request" in issue:
                    continue
                    
                issue_list.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "author": issue["user"]["login"],
                    "labels": [label["name"] for label in issue["labels"]],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"]
                })
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(issue_list, indent=2)
                }],
                "metadata": {
                    "count": len(issue_list)
                }
            }
            
    async def _create_issue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create issue"""
        owner = args["owner"]
        repo = args["repo"]
        
        data = {
            "title": args["title"],
            "body": args.get("body", ""),
            "labels": args.get("labels", []),
            "assignees": args.get("assignees", [])
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self._get_headers(),
                json=data
            )
            
            if response.status_code != 201:
                return {"error": f"Failed to create issue: {response.text}"}
                
            issue = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Issue created: #{issue['number']} {issue['title']}\nURL: {issue['html_url']}"
                }]
            }
            
    async def _update_issue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update issue"""
        owner = args["owner"]
        repo = args["repo"]
        issue_number = args["issue_number"]
        
        data = {}
        if "title" in args:
            data["title"] = args["title"]
        if "body" in args:
            data["body"] = args["body"]
        if "state" in args:
            data["state"] = args["state"]
        if "labels" in args:
            data["labels"] = args["labels"]
            
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}",
                headers=self._get_headers(),
                json=data
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to update issue: {response.text}"}
                
            issue = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Issue updated: #{issue['number']} {issue['title']}"
                }]
            }
            
    async def _list_pull_requests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List pull requests"""
        owner = args["owner"]
        repo = args["repo"]
        state = args.get("state", "open")
        base = args.get("base")
        head = args.get("head")
        
        params = {
            "state": state,
            "per_page": 100
        }
        
        if base:
            params["base"] = base
        if head:
            params["head"] = head
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to list PRs: {response.text}"}
                
            prs = response.json()
            
            # Extract key information
            pr_list = []
            for pr in prs:
                pr_list.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "author": pr["user"]["login"],
                    "base": pr["base"]["ref"],
                    "head": pr["head"]["ref"],
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"]
                })
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(pr_list, indent=2)
                }],
                "metadata": {
                    "count": len(pr_list)
                }
            }
            
    async def _create_pull_request(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create pull request"""
        owner = args["owner"]
        repo = args["repo"]
        
        data = {
            "title": args["title"],
            "body": args.get("body", ""),
            "head": args["head"],
            "base": args.get("base", "main"),
            "draft": args.get("draft", False)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                headers=self._get_headers(),
                json=data
            )
            
            if response.status_code != 201:
                return {"error": f"Failed to create PR: {response.text}"}
                
            pr = response.json()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"PR created: #{pr['number']} {pr['title']}\nURL: {pr['html_url']}"
                }]
            }
            
    async def _search_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search code"""
        query = args["query"]
        
        # Build search query
        search_parts = [query]
        
        if "language" in args:
            search_parts.append(f"language:{args['language']}")
        if "user" in args:
            search_parts.append(f"user:{args['user']}")
        if "org" in args:
            search_parts.append(f"org:{args['org']}")
        if "repo" in args:
            search_parts.append(f"repo:{args['repo']}")
            
        search_query = " ".join(search_parts)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/code",
                headers=self._get_headers(),
                params={
                    "q": search_query,
                    "per_page": 30
                }
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to search code: {response.text}"}
                
            data = response.json()
            
            # Extract results
            results = []
            for item in data.get("items", []):
                results.append({
                    "repository": item["repository"]["full_name"],
                    "path": item["path"],
                    "url": item["html_url"],
                    "score": item["score"]
                })
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(results, indent=2)
                }],
                "metadata": {
                    "total_count": data.get("total_count", 0),
                    "returned": len(results)
                }
            }
            
    async def handle_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle resource request
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not uri.startswith("github://"):
            return {"error": f"Invalid URI scheme: {uri}"}
            
        # Parse URI: github://owner/repo/path
        parts = uri[9:].split("/", 2)  # Remove github:// prefix
        
        if len(parts) < 2:
            return {"error": "Invalid GitHub URI format"}
            
        owner = parts[0]
        repo = parts[1]
        path = parts[2] if len(parts) > 2 else ""
        
        if path:
            # Get specific file
            return await self._get_file({
                "owner": owner,
                "repo": repo,
                "path": path
            })
        else:
            # Get repository info
            return await self._get_repository({
                "owner": owner,
                "repo": repo
            })
