from google import genai
from analytics.schema_loader import load_schema
import os

SCHEMA_DOC_PATH = "semantic_layer/schema_documentation.md"


def generate_sql(question, api_key):

    schema = load_schema()
    
    schema_doc = ""
    if os.path.exists(SCHEMA_DOC_PATH):
        with open(SCHEMA_DOC_PATH, "r") as f:
            schema_doc = f.read()

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a cricket analytics SQL expert.

Follow the semantic schema and documentation below carefully.

### Semantic Schema (YAML):
{schema}

### Detailed Documentation (Markdown):
{schema_doc}

User question:
{question}

Rules:
- Only generate raw SQL, no markdown formatting (no backticks)
- Only SELECT or WITH queries
- Use the balls table
- Follow cricket metric definitions
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text.strip()
    
    # Strip markdown code blocks if present
    if sql.startswith("```"):
        # Remove the first line (e.g., ```sql)
        lines = sql.splitlines()
        if len(lines) > 1 and lines[0].startswith("```"):
            sql = "\n".join(lines[1:])
        # Remove the last line if it's just closing backticks
        if sql.endswith("```"):
            sql = sql.rsplit("```", 1)[0]
        # Also handle one-liners like ```sql SELECT ... ```
        elif "```" in sql:
             sql = sql.replace("```sql", "").replace("```", "")
    
    return sql.strip()
