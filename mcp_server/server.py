from fastapi import FastAPI
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

# Create FastAPI app
app = FastAPI()

@app.get("/")
def health():
    return {"status": "running", "service": "ipl-cricket-analytics"}

# Mount the MCP server - This is the critical fix for routing
# The internal app from streamable_http_app() handles the protocol endpoints
app.mount("/mcp", mcp.streamable_http_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server.server:app", host="0.0.0.0", port=8000)
