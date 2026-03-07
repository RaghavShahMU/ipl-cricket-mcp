from google import genai
import os
import duckdb
import logging

logger = logging.getLogger("mcp-server")
DB_PATH = "data/ipl.duckdb"

def resolve_player_name_ai(name, column="batter", con=None):
    """
    Resolves a player name using dataset candidates and AI fallback.
    """
    # 1. Get candidates from DB using the last part of the name
    parts = name.strip().split()
    search_term = parts[-1] if parts else name
    
    close_con = False
    if con is None:
        con = duckdb.connect(DB_PATH, read_only=True)
        close_con = True
        
    try:
        query = f"SELECT DISTINCT {column} FROM balls WHERE {column} ILIKE ? LIMIT 20"
        candidates = [row[0] for row in con.execute(query, [f"%{search_term}%"]).fetchall()]
    finally:
        if close_con:
            con.close()

    if not candidates:
        return name
    
    # If there's only one unambiguous match, return it
    if len(candidates) == 1:
        return candidates[0]

    # 2. If multiple candidates, try AI resolution
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return name

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are a cricket data expert. Given a user's input for a player name and a list of standardized names from an IPL dataset, identify the correct standardized name.
The dataset often uses initials for first names (e.g., "V Kohli" for "Virat Kohli").

User Input: {name}
Dataset Candidates: {candidates}

Rules:
- Return ONLY the exact standardized name from the candidates list.
- If none match, return the original User Input.
- No explanations.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        resolved = response.text.strip()
        if resolved in candidates:
            return resolved
    except Exception as e:
        logger.error(f"AI name resolution failed: {e}")
    
    return name
