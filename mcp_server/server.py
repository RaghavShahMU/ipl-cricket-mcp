import os
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, EmbeddedResource
from analytics.ai_query_engine import ask_question

# Initialize MCP server
server = Server("ipl-cricket-analytics")

@server.list_tools()
async def handle_list_tools():
    """List available tools."""
    return [
        Tool(
            name="ask_cricket_question",
            description="Ask a natural language question about IPL cricket statistics. Returns the SQL generated and the result data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The cricket analytics question (e.g., 'Who scored the most runs in 2023?')"
                    }
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool execution."""
    if name == "ask_cricket_question":
        question = arguments.get("question")
        if not question:
            return [TextContent(type="text", text="Error: Question is required.")]
        
        try:
            sql, result = ask_question(question)
            
            # Convert result to string for display
            result_str = result.to_string() if hasattr(result, 'to_string') else str(result)
            
            return [
                TextContent(
                    type="text", 
                    text=f"Generated SQL:\n{sql}\n\nResult:\n{result_str}"
                )
            ]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing query: {str(e)}")]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
