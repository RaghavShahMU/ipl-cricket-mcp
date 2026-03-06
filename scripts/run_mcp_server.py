import os
import sys
import subprocess

# Add repository root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("Starting IPL Cricket MCP Server on http://0.0.0.0:8000")
    # Run the server module directly
    subprocess.run([sys.executable, "-m", "mcp_server.server"])
