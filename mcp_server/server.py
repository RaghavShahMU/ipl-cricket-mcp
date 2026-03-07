from mcp.server.fastmcp import FastMCP
from analytics.ai_query_engine import ask_question
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
    """
    logger.info(f"Matchup query: {batsman} vs {bowler}")
    
    con = duckdb.connect(DB_PATH, read_only=True)
    
    def get_matchup_stats(b_name, bo_name):
        query = f"""
        SELECT 
            COUNT(DISTINCT match_id) as matches,
            CAST(SUM(runs_batter) AS INTEGER) as runs_scored_by_batsman,
            COUNT(*) as balls_faced,
            CAST(COUNT(CASE WHEN player_out IS NOT NULL AND player_out = batter THEN 1 END) AS INTEGER) as dismissals,
            ROUND(SUM(valid_ball) / 6.0, 2) as overs_bowled,
            CAST(SUM(runs_bowler) AS INTEGER) as runs_conceded
        FROM balls 
        WHERE batter = ? AND bowler = ?
        """
        res = con.execute(query, [b_name, bo_name]).fetchone()
        
        if not res or res[2] == 0: # balls_faced is 0
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
            "wickets": dismissals, # In a specific head-to-head, dismissals = bowler's wickets
            "economy": econ
        }

    # Direction 1: batsman batting, bowler bowling
    v1 = get_matchup_stats(batsman, bowler)
    
    # Direction 2: bowler batting, batsman bowling
    v2 = get_matchup_stats(bowler, batsman)
    
    con.close()
    
    response = {
        "batsman": batsman,
        "bowler": bowler
    }
    
    if v1:
        response["batsman_vs_bowler"] = {
            "matches": v1["matches"],
            "runs": v1["runs"],
            "balls": v1["balls"],
            "strike_rate": v1["strike_rate"],
            "dismissals": v1["dismissals"]
        }
        # Also include bowler stats for consistency if you want, 
        # but the prompt example shows bowler_vs_batsman for the other way.
        # Wait, the prompt example shows bowler_vs_batsman as a separate section.
        # Let's align exactly with the example.
        
    if v1: # The example shows one way's bowler stats too? 
           # Ah, the example shows:
           # "batsman_vs_bowler": { "matches": 14, "runs": 142, "balls": 108, "strike_rate": 131.48, "dismissals": 4 },
           # "bowler_vs_batsman": { "overs": 18.0, "runs_conceded": 142, "wickets": 4, "economy": 7.88 }
           # This means v1 (batsman vs bowler) contains BOTH batsman batting and bowler bowling perspectives.
        
        # In v1: batsman is batter, bowler is bowler.
        # So v1 stats cover batsman's performance AND bowler's performance against that batsman.
        pass

    # Re-arranging to match the user's specific example structure exactly.
    final_resp = {
        "batsman": batsman,
        "bowler": bowler
    }
    
    if v1:
        final_resp["batsman_vs_bowler"] = {
            "matches": v1["matches"],
            "runs": v1["runs"],
            "balls": v1["balls"],
            "strike_rate": v1["strike_rate"],
            "dismissals": v1["dismissals"]
        }
        final_resp["bowler_stats_against_batsman"] = { # The example uses "bowler_vs_batsman" for the reverse?
                                                        # No, look at the values: 142 runs, 4 wickets.
                                                        # These are the same runs/wickets as in batsman_vs_bowler.
                                                        # So "bowler_vs_batsman" in the example refers to the bowler's stats in that SAME matchup.
            "overs": v1["overs"],
            "runs_conceded": v1["runs_conceded"],
            "wickets": v1["wickets"],
            "economy": v1["economy"]
        }
        # To avoid confusion, I'll name it exactly as in example if possible, 
        # but the user said "If both players have bowled to each other... return both sections".
        # This implies "batsman_vs_bowler" is one "pair" of directions, and "bowler_vs_batsman" is the reverse "pair".
        
    # Let's pivot:
    # If batsman vs bowler exists:
    #   create 'batsman_vs_bowler' summary
    # If bowler vs batsman exists:
    #   create 'bowler_vs_batsman' summary
    
    final_resp = {
        "batsman": batsman,
        "bowler": bowler
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
