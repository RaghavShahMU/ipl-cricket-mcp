from analytics.ai_query_engine import ask_question


question = "Compare Rohit Sharma, Virat Kohli, and MS Dhoni's batting performance in every year"

sql, result = ask_question(question)

print("Generated SQL:\n")
print(sql)

print("\nResult:\n")
print(result)
