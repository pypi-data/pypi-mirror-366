from bssagent.mcp import MCPIntegrator

integrator = MCPIntegrator()

# # Add servers
# await integrator.add_mcp_server("filesystem", "mcp-server-filesystem")
# await integrator.add_mcp_server("postgres", "mcp-server-postgres")

# # Get all tools
# tools = integrator.get_tools()

# # Use specific tool
# file_tool = integrator.get_tool("filesystem.read_file")
# result = file_tool.run(path="/tmp/test.txt")