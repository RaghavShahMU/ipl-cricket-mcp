from google import genai
import os
import duckdb
import logging

logger = logging.getLogger("mcp-server")
DB_PATH = "data/ipl.duckdb"

def resolve_player_name_ai(name, column="batter", con=None):
    """
    Resolves a player name using dataset candidates and AI fallback.
    Returns a LIST of standardized names (handling multiple iterations/variants).
    """
    # 1. Get candidates from DB using the last part of the name
    parts = name.strip().split()
    search_term = parts[-1] if parts else name
    
    close_con = False
    if con is None:
        con = duckdb.connect(DB_PATH, read_only=True)
        close_con = True
        
    try:
        # Search for names containing the search term
        query = f"SELECT DISTINCT {column} FROM balls WHERE {column} ILIKE ? LIMIT 40"
        candidates = [row[0] for row in con.execute(query, [f"%{search_term}%"]).fetchall()]
    finally:
        if close_con:
            con.close()

    if not candidates:
        return [name]
    
    # AI Logic
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Simple fallback based on initials if input is full name
        if len(parts) > 1:
            initial = parts[0][0].upper()
            surname = parts[-1].capitalize()
            for cand in candidates:
                if cand.startswith(initial) and surname in cand:
                    return [cand]
        return [candidates[0]] if candidates else [name]

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are a cricket data expert. Match a user's input for a player name with one or more standardized names from a dataset.
The dataset often uses initials for first names (e.g., "V Kohli" for "Virat Kohli").
Sometimes a player might have multiple standardized entries (e.g. "V Kohli" and "Virat Kohli").

User Input: {name}
Dataset Candidates: {candidates}

Rules:
- Return ONLY the standardized name(s) from the candidates list, separated by commas if multiple.
- If it's ambiguous (e.g. "Sharma" and multiple Sharmas exist), pick the most likely one based on the full name provided.
- If none match, return the original User Input.
- No explanations.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        resolved_text = response.text.strip()
        resolved_list = [r.strip() for r in resolved_text.split(",") if r.strip() in candidates]
        
        if resolved_list:
            return resolved_list
            
    except Exception as e:
        logger.error(f"AI name resolution failed: {e}")
        # Secondary fallback logic without AI
        if len(parts) > 1:
            initial = parts[0][0].upper()
            surname = parts[-1].lower()
            filtered = [c for c in candidates if c.replace('.','').lower().endswith(surname) and c.startswith(initial)]
            if filtered: return filtered

    return [candidates[0]] if candidates else [name]
