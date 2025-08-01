"""
Browser MCP Server
Provides web browsing and scraping capabilities through MCP protocol
"""

import json
import logging
from typing import Dict, Optional, Any
import httpx
from bs4 import BeautifulSoup
import html2text

logger = logging.getLogger(__name__)


class BrowserMCPServer:
    """
    MCP server for browser operations
    Provides tools for web navigation, scraping, and interaction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the browser server
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.headless = config.get("headless", True)
        self.timeout = config.get("timeout", 30000)
        self.user_agent = config.get("user_agent", "Monkey-Coder-MCP/1.0")
        self._session: Optional[httpx.AsyncClient] = None
        self._html2text = html2text.HTML2Text()
        self._html2text.ignore_links = False
        self._html2text.ignore_images = False
        
        # Define available tools
        self.tools = {
            "navigate": {
                "name": "navigate",
                "description": "Navigate to a URL and get content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["html", "markdown", "text"],
                            "description": "Output format",
                            "default": "markdown"
                        },
                        "wait_for": {
                            "type": "string",
                            "description": "CSS selector to wait for"
                        }
                    },
                    "required": ["url"]
                }
            },
            "scrape": {
                "name": "scrape",
                "description": "Scrape specific content from a page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to scrape"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for content"
                        },
                        "attribute": {
                            "type": "string",
                            "description": "Attribute to extract (default: text)"
                        },
                        "multiple": {
                            "type": "boolean",
                            "description": "Extract multiple elements",
                            "default": False
                        }
                    },
                    "required": ["url", "selector"]
                }
            },
            "extract_links": {
                "name": "extract_links",
                "description": "Extract all links from a page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to extract links from"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Filter links by pattern"
                        },
                        "internal_only": {
                            "type": "boolean",
                            "description": "Only return internal links",
                            "default": False
                        }
                    },
                    "required": ["url"]
                }
            },
            "extract_metadata": {
                "name": "extract_metadata",
                "description": "Extract page metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to extract metadata from"
                        }
                    },
                    "required": ["url"]
                }
            },
            "screenshot": {
                "name": "screenshot",
                "description": "Take a screenshot of a page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to screenshot"
                        },
                        "full_page": {
                            "type": "boolean",
                            "description": "Capture full page",
                            "default": False
                        },
                        "width": {
                            "type": "integer",
                            "description": "Viewport width",
                            "default": 1280
                        },
                        "height": {
                            "type": "integer",
                            "description": "Viewport height",
                            "default": 720
                        }
                    },
                    "required": ["url"]
                }
            },
            "submit_form": {
                "name": "submit_form",
                "description": "Submit a form on a page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL containing the form"
                        },
                        "form_selector": {
                            "type": "string",
                            "description": "CSS selector for the form"
                        },
                        "data": {
                            "type": "object",
                            "description": "Form data to submit"
                        },
                        "submit_selector": {
                            "type": "string",
                            "description": "Submit button selector"
                        }
                    },
                    "required": ["url", "data"]
                }
            },
            "download": {
                "name": "download",
                "description": "Download a file from URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to download"
                        },
                        "save_as": {
                            "type": "string",
                            "description": "Filename to save as"
                        }
                    },
                    "required": ["url"]
                }
            },
            "search": {
                "name": "search",
                "description": "Search the web using a search engine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "engine": {
                            "type": "string",
                            "enum": ["google", "bing", "duckduckgo"],
                            "description": "Search engine to use",
                            "default": "duckduckgo"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "http://": {
                "uri": "http://",
                "name": "HTTP Web",
                "description": "Access HTTP websites",
                "mimeType": "text/html"
            },
            "https://": {
                "uri": "https://",
                "name": "HTTPS Web",
                "description": "Access HTTPS websites",
                "mimeType": "text/html"
            }
        }
        
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session"""
        if not self._session:
            self._session = httpx.AsyncClient(
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout / 1000,  # Convert to seconds
                follow_redirects=True
            )
        return self._session
        
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
            if tool_name == "navigate":
                return await self._navigate(arguments)
            elif tool_name == "scrape":
                return await self._scrape(arguments)
            elif tool_name == "extract_links":
                return await self._extract_links(arguments)
            elif tool_name == "extract_metadata":
                return await self._extract_metadata(arguments)
            elif tool_name == "screenshot":
                return await self._screenshot(arguments)
            elif tool_name == "submit_form":
                return await self._submit_form(arguments)
            elif tool_name == "download":
                return await self._download(arguments)
            elif tool_name == "search":
                return await self._search(arguments)
            else:
                return {"error": f"Tool not implemented: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
            
    async def _navigate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to URL and get content"""
        url = args["url"]
        format_type = args.get("format", "markdown")
        
        session = await self._get_session()
        
        try:
            response = await session.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "").lower()
            
            if "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                    
                if format_type == "html":
                    content = str(soup)
                elif format_type == "markdown":
                    content = self._html2text.handle(str(soup))
                else:  # text
                    content = soup.get_text()
                    
            else:
                content = response.text
                
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }],
                "metadata": {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "content_type": content_type
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to navigate: {e}"}
            
    async def _scrape(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape specific content"""
        url = args["url"]
        selector = args["selector"]
        attribute = args.get("attribute", "text")
        multiple = args.get("multiple", False)
        
        session = await self._get_session()
        
        try:
            response = await session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            if multiple:
                elements = soup.select(selector)
                results = []
                
                for elem in elements:
                    if attribute == "text":
                        results.append(elem.get_text(strip=True))
                    else:
                        results.append(elem.get(attribute, ""))
                        
                content = json.dumps(results, indent=2)
            else:
                elem = soup.select_one(selector)
                if elem:
                    if attribute == "text":
                        content = elem.get_text(strip=True)
                    else:
                        content = elem.get(attribute, "")
                else:
                    content = "No element found"
                    
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }],
                "metadata": {
                    "url": url,
                    "selector": selector
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to scrape: {e}"}
            
    async def _extract_links(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract links from page"""
        url = args["url"]
        pattern = args.get("pattern")
        internal_only = args.get("internal_only", False)
        
        session = await self._get_session()
        
        try:
            response = await session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            base_url = str(response.url)
            
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                
                # Resolve relative URLs
                if href.startswith("/"):
                    from urllib.parse import urljoin
                    href = urljoin(base_url, href)
                elif not href.startswith(("http://", "https://")):
                    continue
                    
                # Apply filters
                if internal_only:
                    from urllib.parse import urlparse
                    if urlparse(href).netloc != urlparse(base_url).netloc:
                        continue
                        
                if pattern and pattern not in href:
                    continue
                    
                links.append({
                    "url": href,
                    "text": a.get_text(strip=True),
                    "title": a.get("title", "")
                })
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(links, indent=2)
                }],
                "metadata": {
                    "url": url,
                    "count": len(links)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract links: {e}"}
            
    async def _extract_metadata(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract page metadata"""
        url = args["url"]
        
        session = await self._get_session()
        
        try:
            response = await session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            metadata = {
                "title": "",
                "description": "",
                "keywords": "",
                "author": "",
                "og": {},
                "twitter": {}
            }
            
            # Extract title
            title_tag = soup.find("title")
            if title_tag:
                metadata["title"] = title_tag.get_text(strip=True)
                
            # Extract meta tags
            for meta in soup.find_all("meta"):
                name = meta.get("name", "").lower()
                property_attr = meta.get("property", "").lower()
                content = meta.get("content", "")
                
                if name == "description":
                    metadata["description"] = content
                elif name == "keywords":
                    metadata["keywords"] = content
                elif name == "author":
                    metadata["author"] = content
                elif property_attr.startswith("og:"):
                    metadata["og"][property_attr[3:]] = content
                elif property_attr.startswith("twitter:"):
                    metadata["twitter"][property_attr[8:]] = content
                    
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(metadata, indent=2)
                }],
                "metadata": {
                    "url": url
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract metadata: {e}"}
            
    async def _screenshot(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Take screenshot (simulated - would need real browser)"""
        url = args["url"]
        
        # This is a placeholder - real implementation would use Playwright/Puppeteer
        return {
            "content": [{
                "type": "text",
                "text": f"Screenshot functionality requires a real browser engine. URL: {url}"
            }],
            "metadata": {
                "url": url,
                "note": "Use browser_action tool in Cline for real screenshots"
            }
        }
        
    async def _submit_form(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Submit form data"""
        url = args["url"]
        data = args["data"]
        form_selector = args.get("form_selector")
        
        session = await self._get_session()
        
        try:
            # First get the page to find form action
            response = await session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find form
            if form_selector:
                form = soup.select_one(form_selector)
            else:
                form = soup.find("form")
                
            if not form:
                return {"error": "No form found"}
                
            # Get form action
            action = form.get("action", url)
            if not action.startswith(("http://", "https://")):
                from urllib.parse import urljoin
                action = urljoin(url, action)
                
            method = form.get("method", "post").lower()
            
            # Submit form
            if method == "post":
                response = await session.post(action, data=data)
            else:
                response = await session.get(action, params=data)
                
            response.raise_for_status()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Form submitted successfully to {action}"
                }],
                "metadata": {
                    "url": str(response.url),
                    "status_code": response.status_code
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to submit form: {e}"}
            
    async def _download(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Download file"""
        url = args["url"]
        save_as = args.get("save_as")
        
        if not save_as:
            from urllib.parse import urlparse
            save_as = urlparse(url).path.split("/")[-1] or "download"
            
        session = await self._get_session()
        
        try:
            response = await session.get(url)
            response.raise_for_status()
            
            # In a real implementation, we'd save to disk
            # For MCP, we'll return file info
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"File downloaded: {save_as} ({len(response.content)} bytes)"
                }],
                "metadata": {
                    "url": url,
                    "filename": save_as,
                    "size": len(response.content),
                    "content_type": response.headers.get("content-type")
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to download: {e}"}
            
    async def _search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web"""
        query = args["query"]
        engine = args.get("engine", "duckduckgo")
        max_results = args.get("max_results", 10)
        
        session = await self._get_session()
        
        try:
            if engine == "duckduckgo":
                # DuckDuckGo HTML search
                url = "https://html.duckduckgo.com/html/"
                params = {"q": query}
                
                response = await session.post(url, data=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                
                for result in soup.select(".result")[:max_results]:
                    title_elem = result.select_one(".result__title")
                    snippet_elem = result.select_one(".result__snippet")
                    url_elem = result.select_one(".result__url")
                    
                    if title_elem and url_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": url_elem.get_text(strip=True),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                        })
                        
            else:
                return {"error": f"Search engine '{engine}' not implemented"}
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(results, indent=2)
                }],
                "metadata": {
                    "query": query,
                    "engine": engine,
                    "count": len(results)
                }
            }
            
        except Exception as e:
            return {"error": f"Search failed: {e}"}
            
    async def handle_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle resource request
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not uri.startswith(("http://", "https://")):
            return {"error": f"Invalid URI scheme: {uri}"}
            
        # Navigate to the URL and return content
        return await self._navigate({"url": uri, "format": "markdown"})
        
    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.aclose()
            self._session = None
