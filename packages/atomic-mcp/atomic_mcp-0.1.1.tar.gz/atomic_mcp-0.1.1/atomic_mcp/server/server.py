"""Main MCP Server coordinator for atomic-mcp framework."""

import asyncio
import logging
import os
import sys
from typing import List, Optional

from fastmcp import FastMCP
from atomic_mcp.server.interfaces.tool import Tool
from atomic_mcp.server.interfaces.resource import Resource
from atomic_mcp.server.services.tool import ToolService
from atomic_mcp.server.services.resource import ResourceService


logger = logging.getLogger(__name__)


class MCPServer:
    """
    Main MCP Server coordinator that provides a simple interface for registering
    tools and resources, then running the server with FastMCP.
    
    Supports STDIO and HTTP transports only (SSE is deprecated).
    """
    
    def __init__(self, name: str = "atomic-mcp-server", description: str = ""):
        """
        Initialize the MCP Server.
        
        Args:
            name: Server name identifier
            description: Server description
        """
        self.name = name
        self.description = description
        
        # Initialize services
        self.tool_service = ToolService()
        self.resource_service = ResourceService()
        
        # FastMCP instance (created when server runs)
        self._mcp_server: Optional[FastMCP] = None
        
    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool instance to the server.
        
        Args:
            tool: Tool instance that implements the Tool interface
        """
        self.tool_service.register_tool(tool)
        logger.debug(f"Registered tool: {tool.name}")
        
    def add_tools(self, tools: List[Tool]) -> None:
        """
        Add multiple tool instances to the server.
        
        Args:
            tools: List of Tool instances
        """
        self.tool_service.register_tools(tools)
        logger.debug(f"Registered {len(tools)} tools")
        
    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource instance to the server.
        
        Args:
            resource: Resource instance that implements the Resource interface
        """
        self.resource_service.register_resource(resource)
        logger.debug(f"Registered resource: {resource.name}")
        
    def add_resources(self, resources: List[Resource]) -> None:
        """
        Add multiple resource instances to the server.
        
        Args:
            resources: List of Resource instances
        """
        self.resource_service.register_resources(resources)
        logger.debug(f"Registered {len(resources)} resources")
        
    def _setup_mcp_server(self) -> FastMCP:
        """Setup and configure the underlying FastMCP server."""
        if self._mcp_server is None:
            self._mcp_server = FastMCP(self.name)
            
            # Register all tools and resources with FastMCP
            self.tool_service.register_mcp_handlers(self._mcp_server)
            self.resource_service.register_mcp_handlers(self._mcp_server)
                
        return self._mcp_server
        
    def _detect_transport(self) -> str:
        """
        Auto-detect the appropriate transport method.
        
        Returns:
            "stdio" if running in STDIO mode, "http" otherwise
        """
        # Check if we're running in STDIO mode (common MCP client pattern)
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return "stdio"
            
        # Check environment variables that might indicate STDIO mode
        if os.getenv("MCP_STDIO_MODE") or os.getenv("MCP_TRANSPORT") == "stdio":
            return "stdio"
            
        # Default to HTTP for development/testing
        return "http"
        
    async def run_async(self, transport: str = "auto", host: str = "localhost", 
                       port: int = 8000) -> None:
        """
        Run the server asynchronously.
        
        Args:
            transport: Transport method ("auto", "stdio", or "http")
            host: Host for HTTP transport
            port: Port for HTTP transport
        """
        if transport == "auto":
            transport = self._detect_transport()
            
        mcp_server = self._setup_mcp_server()
        
        if transport == "stdio":
            logger.info(f"Starting {self.name} with STDIO transport")
            await mcp_server.run_async(transport="stdio")
        elif transport == "http":
            logger.info(f"Starting {self.name} with HTTP transport on {host}:{port}")
            await mcp_server.run_async(transport="http", http_port=port, host=host)
        else:
            raise ValueError(f"Unknown transport: {transport}. Only 'stdio' and 'http' are supported.")
            
    def run(self, transport: str = "auto", host: str = "localhost", 
            port: int = 8000) -> None:
        """
        Run the server (blocking call).
        
        Args:
            transport: Transport method ("auto", "stdio", or "http") 
            host: Host for HTTP transport
            port: Port for HTTP transport
        """
        try:
            asyncio.run(self.run_async(transport, host, port))
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
            
    def run_stdio(self) -> None:
        """Run the server with STDIO transport."""
        self.run(transport="stdio")
        
    def run_http(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Run the server with HTTP transport.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.run(transport="http", host=host, port=port)
        
    def get_registered_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.tool_service._tools.keys())
        
    def get_registered_resources(self) -> List[str]:
        """Get list of registered resource URI patterns."""
        return list(self.resource_service._uri_patterns.keys())
        
    def __repr__(self) -> str:
        tools_count = len(self.tool_service._tools)
        resources_count = len(self.resource_service._uri_patterns)
        return (f"MCPServer(name='{self.name}', "
                f"tools={tools_count}, "
                f"resources={resources_count})")