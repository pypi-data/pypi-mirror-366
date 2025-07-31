import json
import asyncio
from typing import Dict, Any
from langchain_core.tools import BaseTool
from pydantic import Field
from .mcp_connection import MCPConnection


class MCPToolWrapper(BaseTool):
    """Wrapper for MCP tools to make them compatible with LangChain."""
    
    tool_name: str = Field(description="The name of the MCP tool")
    tool_description: str = Field(description="The description of the MCP tool")
    mcp_connection: MCPConnection = Field(description="MCP connection to use")
    tool_schema: Dict[str, Any] = Field(description="Tool schema from MCP")
    
    @property
    def name(self) -> str:
        return self.tool_name
    
    @property
    def description(self) -> str:
        return self.tool_description
    
    def _run(
        self,
        *args,
        **kwargs
    ) -> str:
        """Execute the MCP tool."""
        try:
            # Prepare the call message
            call_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": self.name,
                    "arguments": kwargs
                }
            }
            
            # Send the call
            response = asyncio.run(self.mcp_connection.send_message(call_message))
            
            # Handle the response
            if "result" in response:
                return json.dumps(response["result"])
            elif "error" in response:
                return f"Error: {response['error']}"
            else:
                return "Unknown response format"
                
        except Exception as e:
            return f"Error executing MCP tool: {str(e)}"
    
    async def _arun(
        self,
        *args,
        **kwargs
    ) -> str:
        """Async version of tool execution."""
        try:
            # Prepare the call message
            call_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": self.name,
                    "arguments": kwargs
                }
            }
            
            # Send the call
            response = await self.mcp_connection.send_message(call_message)
            
            # Handle the response
            if "result" in response:
                return json.dumps(response["result"])
            elif "error" in response:
                return f"Error: {response['error']}"
            else:
                return "Unknown response format"
                
        except Exception as e:
            return f"Error executing MCP tool: {str(e)}"

