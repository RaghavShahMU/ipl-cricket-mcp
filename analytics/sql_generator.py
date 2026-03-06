from genai import Client
from analytics.schema_loader import load_schema


def generate_sql(question, api_key):

    schema = load_schema()

    client = Client(api_key=api_key)

    prompt = f"""
You are a cricket analytics SQL expert.

Follow the semantic schema below carefully.

{schema}

User question:
{question}

Rules:
- Only generate SQL
- Only SELECT queries
- Use the balls table
- Follow cricket metric definitions
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()
