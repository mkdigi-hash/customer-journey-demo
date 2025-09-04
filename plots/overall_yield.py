import pandas as pd
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=15432,
    database="postgres",
    user="admin",
    password="ukdtc"
)

# Load relevant columns
query = """
SELECT die_x, die_y, pass_fail
FROM wafer_probe_results_midterm;
"""
df = pd.read_sql(query, conn)


# Calculate pass %
total_tests = len(df)
pass_count = (df['pass_fail'].str.upper() == 'PASS').sum()
pass_rate = pass_count/total_tests
# Print the result
print(f"Overall Pass Rate: {pass_rate:.20f}%")

