from analytics.ai_query_engine import ask_question


question = "When Bumrah bowls 19th Over of the 2nd innings, what is the probabilitiy that his team wins? Could you also bring stats around it? Like when how many times it worked or didn't worked. Also a basic distribution of the opponent team's score"

sql, result = ask_question(question)

print("Generated SQL:\n")
print(sql)

print("\nResult:\n")
print(result)
