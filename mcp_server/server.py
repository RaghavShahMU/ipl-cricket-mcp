from mcp.server.fastmcp import FastMCP
from analytics.ai_query_engine import ask_question
from starlette.responses import JSONResponse
from starlette.requests import Request

# Initialize FastMCP server with the desired host and port
mcp = FastMCP(
    "ipl-cricket-analytics",
    host="0.0.0.0",
    port=8000
)

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

# Using native custom_route to provide health check and discovery without FastAPI
@mcp.custom_route("/", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "running", 
        "service": "ipl-cricket-analytics",
        "mcp_endpoint": "/mcp"
    })

@mcp.custom_route("/.well-known/mcp", methods=["GET"])
async def discovery(request: Request) -> JSONResponse:
    return JSONResponse({
        "mcp_endpoint": "/mcp"
    })

if __name__ == "__main__":
    # The 'streamable-http' transport natively exposes the /mcp endpoint
    mcp.run(transport="streamable-http")
