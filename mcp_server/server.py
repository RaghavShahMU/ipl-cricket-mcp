from mcp.server.fastmcp import FastMCP
from analytics.ai_query_engine import ask_question
from analytics.player_resolver import resolve_player_name_ai
from starlette.responses import JSONResponse
from starlette.requests import Request
import duckdb
import logging

# Configure logging
logger = logging.getLogger("mcp-server")
DB_PATH = "data/ipl.duckdb"

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

@mcp.tool()
def batsman_bowler_matchup(batsman: str, bowler: str):
    """
    Analyze the historical matchup between a batsman and a bowler.
    Resolves player names before querying and handles name iterations/variants.
    """
    logger.info(f"Matchup query: {batsman} vs {bowler}")
    
    con = duckdb.connect(DB_PATH, read_only=True)
    
    # 1. Resolve Player Names (returns list of variants)
    def resolve_name(name, column):
        search_term = name.strip()
        # Find exact or close matches
        results = con.execute(f"SELECT DISTINCT {column} FROM balls WHERE {column} ILIKE ?", [f"%{search_term}%"]).fetchall()
        
        # If we find an exact match string-wise among variants, prioritize it if it's the only one 
        # But user wants AI to handle the "iterations" logic.
        
        # If the user input is already in initials format and matches exactly, use it.
        # Otherwise, fall back to AI to resolve full name to dataset initials.
        
        if len(results) == 1:
            return [results[0][0]]
            
        logger.info(f"Simple resolution found {len(results)} variants or failed for {name}, using AI/Reasoning")
        # Handle iterations/fallbacks in the resolver
        return resolve_player_name_ai(name, column, con=con)

    resolved_batsmen = resolve_name(batsman, "batter")
    resolved_bowlers = resolve_name(bowler, "bowler")
    
    logger.info(f"Resolved batsman variants: {resolved_batsmen}")
    logger.info(f"Resolved bowler variants: {resolved_bowlers}")
    
    def get_matchup_stats(b_names, bo_names):
        # b_names and bo_names are lists
        query = f"""
        SELECT 
            COUNT(DISTINCT match_id) as matches,
            CAST(SUM(runs_batter) AS INTEGER) as runs_scored_by_batsman,
            COUNT(*) as balls_faced,
            CAST(COUNT(CASE WHEN player_out IS NOT NULL AND player_out IN ({','.join(['?' for _ in b_names])}) THEN 1 END) AS INTEGER) as dismissals,
            ROUND(SUM(valid_ball) / 6.0, 2) as overs_bowled,
            CAST(SUM(runs_bowler) AS INTEGER) as runs_conceded
        FROM balls 
        WHERE batter IN ({','.join(['?' for _ in b_names])}) 
          AND bowler IN ({','.join(['?' for _ in bo_names])})
        """
        # Parameters: [all_b_names_for_dismissals, all_b_names_for_batter, all_bo_names_for_bowler]
        params = b_names + b_names + bo_names
        res = con.execute(query, params).fetchone()
        
        if not res or res[2] == 0:
            return None
            
        matches, runs, balls, dismissals, overs, runs_conceded = res
        
        sr = round((runs / balls) * 100, 2) if balls > 0 else 0
        econ = round(runs_conceded / overs, 2) if overs > 0 else 0
        
        return {
            "matches": matches,
            "runs": runs,
            "balls": balls,
            "strike_rate": sr,
            "dismissals": dismissals,
            "overs": overs,
            "runs_conceded": runs_conceded,
            "wickets": dismissals,
            "economy": econ
        }

    # Direction 1: resolved_batsmen batting, resolved_bowlers bowling
    v1 = get_matchup_stats(resolved_batsmen, resolved_bowlers)
    
    # Direction 2: resolved_bowlers batting, resolved_batsmen bowling
    v2 = get_matchup_stats(resolved_bowlers, resolved_batsmen)
    
    con.close()
    
    final_resp = {
        "batsman": ", ".join(resolved_batsmen),
        "bowler": ", ".join(resolved_bowlers),
        "original_input": {
            "batsman": batsman,
            "bowler": bowler
        }
    }
    
    if v1:
        final_resp["batsman_vs_bowler"] = {
            "matches": v1["matches"],
            "runs": v1["runs"],
            "balls": v1["balls"],
            "strike_rate": v1["strike_rate"],
            "dismissals": v1["dismissals"],
            "overs_bowled": v1["overs"],
            "runs_conceded": v1["runs_conceded"],
            "economy_rate": v1["economy"]
        }
    
    if v2:
        final_resp["bowler_vs_batsman"] = {
            "matches": v2["matches"],
            "runs": v2["runs"],
            "balls": v2["balls"],
            "strike_rate": v2["strike_rate"],
            "dismissals": v2["dismissals"],
            "overs_bowled": v2["overs"],
            "runs_conceded": v2["runs_conceded"],
            "economy_rate": v2["economy"]
        }
        
    return final_resp

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
