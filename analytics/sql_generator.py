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
- Only generate SQL
- Only SELECT queries
- Use the balls table
- Follow cricket metric definitions
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()
