import duckdb
import os

from analytics.sql_generator import generate_sql
from analytics.sql_guardrails import validate_sql


DB_PATH = "data/ipl.duckdb"


def ask_question(question):

    api_key = os.getenv("GEMINI_API_KEY")

    sql_query = generate_sql(question, api_key)

    validate_sql(sql_query)

    con = duckdb.connect(DB_PATH)

    result = con.execute(sql_query).fetchdf()

    con.close()

    return sql_query, result
