from typing import Dict, List, Optional
import logging
from .mcp_connection import MCPConnection
from .mcp_tool_wrapper import MCPToolWrapper


class MCPIntegrator:
    """Integrates MCP servers with BSS agents."""
    
    def __init__(self):
        self.connections: Dict[str, MCPConnection] = {}
        self.tools: Dict[str, MCPToolWrapper] = {}
        self.logger = logging.getLogger(__name__)
    
    async def add_mcp_server(
        self,
        server_id: str,
        server_path: str,
        server_args: Optional[List[str]] = None
    ) -> bool:
        """Add and start an MCP server."""
        try:
            connection = MCPConnection(server_path, server_args)
            await connection.start()
            self.connections[server_id] = connection
            
            # Initialize the server
            await self._initialize_server(server_id)
            
            # Load tools from the server
            await self._load_tools(server_id)
            
            self.logger.info(f"Successfully added MCP server: {server_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add MCP server {server_id}: {e}")
            return False
    
    async def _initialize_server(self, server_id: str):
        """Initialize the MCP server."""
        connection = self.connections[server_id]
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "bss-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await connection.send_message(init_message)
        self.logger.info(f"Initialized MCP server {server_id}: {response}")
    
    async def _load_tools(self, server_id: str):
        """Load tools from the MCP server."""
        connection = self.connections[server_id]
        
        # List tools
        list_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = await connection.send_message(list_message)
        
        if "result" in response and "tools" in response["result"]:
            for tool_info in response["result"]["tools"]:
                tool_name = f"{server_id}.{tool_info['name']}"
                
                # Create tool wrapper
                tool_wrapper = MCPToolWrapper(
                    tool_name=tool_name,
                    tool_description=tool_info.get("description", ""),
                    mcp_connection=connection,
                    tool_schema=tool_info,
                    description=tool_info.get("description", "")
                )
                
                self.tools[tool_name] = tool_wrapper
                self.logger.info(f"Loaded MCP tool: {tool_name}")
    
    def get_tools(self) -> List[MCPToolWrapper]:
        """Get all available MCP tools."""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolWrapper]:
        """Get a specific MCP tool by name."""
        return self.tools.get(tool_name)
    
    def get_tools_by_server(self, server_id: str) -> List[MCPToolWrapper]:
        """Get all tools from a specific MCP server."""
        return [
            tool for name, tool in self.tools.items()
            if name.startswith(f"{server_id}.")
        ]
    
    async def remove_mcp_server(self, server_id: str) -> bool:
        """Remove and stop an MCP server."""
        try:
            if server_id in self.connections:
                # Stop the server
                await self.connections[server_id].stop()
                
                # Remove tools from this server
                tools_to_remove = [
                    name for name in self.tools.keys()
                    if name.startswith(f"{server_id}.")
                ]
                for tool_name in tools_to_remove:
                    del self.tools[tool_name]
                
                # Remove connection
                del self.connections[server_id]
                
                self.logger.info(f"Removed MCP server: {server_id}")
                return True
            else:
                self.logger.warning(f"MCP server {server_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove MCP server {server_id}: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown all MCP connections."""
        for server_id in list(self.connections.keys()):
            await self.remove_mcp_server(server_id)
        self.logger.info("Shutdown all MCP connections")
