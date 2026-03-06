import google.generativeai as genai

from analytics.schema_loader import load_schema


def generate_sql(question, api_key):

    schema = load_schema()

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-pro")

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

    response = model.generate_content(prompt)

    return response.text.strip()
