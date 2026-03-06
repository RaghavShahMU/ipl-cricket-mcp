import duckdb
import pandas as pd

DB_PATH = "data/ipl.duckdb"


def run_sql(query: str):
    """
    Execute SQL query on IPL DuckDB database
    """
    con = duckdb.connect(DB_PATH)
    result = con.execute(query).fetchdf()
    con.close()
    return result


def get_top_batsmen(limit: int = 10):
    query = f"""
    SELECT batsman,
           SUM(runs_off_bat) AS total_runs
    FROM balls
    GROUP BY batsman
    ORDER BY total_runs DESC
    LIMIT {limit}
    """

    return run_sql(query)


def get_top_bowlers(limit: int = 10):
    query = f"""
    SELECT bowler,
           COUNT(*) AS balls_bowled
    FROM balls
    GROUP BY bowler
    ORDER BY balls_bowled DESC
    LIMIT {limit}
    """

    return run_sql(query)
