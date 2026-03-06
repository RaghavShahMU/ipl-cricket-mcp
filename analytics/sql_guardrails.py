FORBIDDEN_KEYWORDS = [
    "DELETE",
    "UPDATE",
    "INSERT",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE"
]


def validate_sql(sql_query: str):

    upper_sql = sql_query.upper()

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in upper_sql:
            raise ValueError(
                f"Forbidden SQL operation detected: {keyword}"
            )

    if not upper_sql.strip().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    return True
