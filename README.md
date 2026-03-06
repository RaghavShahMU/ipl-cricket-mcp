# ipl-cricket-mcp
This would be used to connect clickup to github using an MCP connector and perform cricket analytics using AI semantic layers from historical data points.

Structure
ipl-cricket-mcp
│
├ data/
│   └ ipl.duckdb
│
├ analytics/
│   ├ query_engine.py
│   ├ metrics.py
│   └ ai_sql_agent.py
│
├ semantic_layer/
│   └ schema.yaml
│
├ mcp_server/
│   └ server.py
│
├ scripts/
│   └ create_db.py
│
├ requirements.txt
└ README.md

# IPL Cricket Analytics MCP

AI-powered cricket analytics engine using:

- DuckDB
- Gemini LLM
- MCP Server
- ClickUp integration

Dataset: 18 years IPL ball-by-ball data.

Purpose:
Learning MCP architecture and building a cricket analytics platform.
