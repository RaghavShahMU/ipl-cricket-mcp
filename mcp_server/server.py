from mcp.server.fastmcp import FastMCP
from analytics.ai_query_engine import ask_question

# Initialize FastMCP server
mcp = FastMCP("ipl-cricket-analytics")

@mcp.tool()
def ask_cricket_question(question: str):
    """
    Ask a natural language cricket analytics question.
    Returns generated SQL and results.
    """
    sql, result = ask_question(question)
    return {
        "sql": sql,
        "result": result.to_dict(orient="records")
    }

# Expose FastAPI app object for cloud deployment
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server.server:app", host="0.0.0.0", port=8000)
