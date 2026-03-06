from mcp.server.fastmcp import FastMCP
from analytics.ai_query_engine import ask_question
import os

mcp = FastMCP("ipl-cricket-analytics")

@mcp.tool()
def ask_cricket_question(question: str):
    """
    Ask a natural language cricket analytics question.
    """
    sql, result = ask_question(question)

    return {
        "sql": sql,
        "result": result.to_dict(orient="records")
    }

if __name__ == "__main__":
    # FastMCP uses environment variables for host and port
    os.environ["FASTMCP_SERVER_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_SERVER_PORT"] = "8000"
    # Use SSE transport to expose the HTTP endpoints ClickUp requires
    mcp.run(transport="sse")
