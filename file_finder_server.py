import os
import json
import asyncio
from datetime import datetime
from mcp.server import Server # type: ignore
from mcp.types import Tool, TextContent # type: ignore

# Initialize the MCP server
app = Server("file-finder-mcp")

# Define the tool to find files based on a path fragment
@app.call_tool()
async def find_files(name: str, arguments: dict | None) -> list[TextContent]:
    """Find files in the filesystem based on a path fragment."""
    if not arguments or "path_fragment" not in arguments:
        raise ValueError("Missing 'path_fragment' in arguments")
    
    path_fragment = arguments["path_fragment"]
    results = []

    # Walk through the filesystem to find matching files
    for root, _, files in os.walk(os.getcwd()):  # Start from current working directory
        for file_name in files:
            full_path = os.path.join(root, file_name)
            if path_fragment.lower() in full_path.lower():
                file_stats = os.stat(full_path)
                file_info = {
                    "file_name": file_name,
                    "path": full_path,
                    "size": file_stats.st_size,  # Size in bytes
                    "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                }
                results.append(file_info)
    
    # Return results as JSON string wrapped in TextContent
    return [TextContent(text=json.dumps(results, indent=2))]

# Define the list of available tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the MCP server."""
    return [
        Tool(
            name="find_files",
            description="Find files in the filesystem by a path fragment",
            inputSchema={
                "type": "object",
                "properties": {
                    "path_fragment": {
                        "type": "string",
                        "description": "A fragment of the file path to search for"
                    }
                },
                "required": ["path_fragment"]
            }
        )
    ]

# Main function to run the server
async def main():
    from mcp.server.stdio import stdio_server # type: ignore
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())