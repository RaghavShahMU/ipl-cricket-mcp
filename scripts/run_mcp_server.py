import uvicorn
import os
import sys

# Add repository root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("Starting IPL Cricket MCP Server on http://0.0.0.0:8000")
    uvicorn.run("mcp_server.server:app", host="0.0.0.0", port=8000, reload=True)
