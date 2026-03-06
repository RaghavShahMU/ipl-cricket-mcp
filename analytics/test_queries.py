import sys
sys.path.append(".")

from analytics.query_engine import test

df = test()

print(df)
