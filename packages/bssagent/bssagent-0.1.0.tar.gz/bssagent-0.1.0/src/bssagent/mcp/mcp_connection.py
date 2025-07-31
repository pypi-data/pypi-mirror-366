from typing import Dict, List, Any, Optional, Callable
import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
import subprocess
import os
from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


class MCPToolType(Enum):
    """Types of MCP tools."""
    FUNCTION = "function"
    RESOURCE = "resource"
    COMMAND = "command"


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    tool_type: MCPToolType
    server_id: str


class MCPConnection:
    """Manages connection to an MCP server."""
    
    def __init__(self, server_path: str, server_args: Optional[List[str]] = None):
        self.server_path = server_path
        self.server_args = server_args or []
        self.process: Optional[subprocess.Popen] = None
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the MCP server process."""
        try:
            cmd = [self.server_path] + self.server_args
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.logger.info(f"Started MCP server: {self.server_path}")
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.logger.info("Stopped MCP server")
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("MCP server not started or invalid process")
        
        try:
            # Send message
            message_str = json.dumps(message) + "\n"
            self.process.stdin.write(message_str)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
            else:
                raise RuntimeError("No response from MCP server")
        except Exception as e:
            self.logger.error(f"Error communicating with MCP server: {e}")
            raise

