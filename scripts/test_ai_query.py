from analytics.ai_query_engine import ask_question


question = "Top 10 run scorers in IPL history"

sql, result = ask_question(question)

print("Generated SQL:\n")
print(sql)

print("\nResult:\n")
print(result)
