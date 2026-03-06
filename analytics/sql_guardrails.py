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

    stripped_upper = upper_sql.strip()
    if not (stripped_upper.startswith("SELECT") or stripped_upper.startswith("WITH")):
        raise ValueError("Only SELECT and WITH queries are allowed.")

    return True
