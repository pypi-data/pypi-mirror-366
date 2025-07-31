from typing import List, Optional
import logging
from .mcp_integrator import MCPIntegrator
from .mcp_tool_wrapper import MCPToolWrapper


class MCPEnhancedAgent:
    """Agent class that integrates with MCP servers."""
    
    def __init__(self, base_agent, mcp_integrator: MCPIntegrator):
        self.base_agent = base_agent
        self.mcp_integrator = mcp_integrator
        self.logger = logging.getLogger(__name__)
    
    async def add_mcp_server(
        self,
        server_id: str,
        server_path: str,
        server_args: Optional[List[str]] = None
    ) -> bool:
        """Add an MCP server to the agent."""
        success = await self.mcp_integrator.add_mcp_server(server_id, server_path, server_args)
        if success:
            # Update the agent's tools with new MCP tools
            self._update_agent_tools()
        return success
    
    def _update_agent_tools(self):
        """Update the agent's tools with MCP tools."""
        # This method would need to be implemented based on how the base agent
        # handles tool updates. For now, we'll log the available tools.
        mcp_tools = self.mcp_integrator.get_tools()
        self.logger.info(f"Available MCP tools: {[tool.name for tool in mcp_tools]}")
    
    def get_mcp_tools(self) -> List[MCPToolWrapper]:
        """Get all available MCP tools."""
        return self.mcp_integrator.get_tools()
    
    def get_mcp_tool(self, tool_name: str) -> Optional[MCPToolWrapper]:
        """Get a specific MCP tool."""
        return self.mcp_integrator.get_tool(tool_name)
    
    async def remove_mcp_server(self, server_id: str) -> bool:
        """Remove an MCP server from the agent."""
        success = await self.mcp_integrator.remove_mcp_server(server_id)
        if success:
            self._update_agent_tools()
        return success
    
    async def shutdown(self):
        """Shutdown the MCP integrator."""
        await self.mcp_integrator.shutdown()
    
    # Delegate other methods to base agent
    def __getattr__(self, name):
        return getattr(self.base_agent, name)