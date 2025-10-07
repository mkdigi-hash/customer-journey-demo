import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=15432,
    database="postgres",
    user="admin",
    password="ukdtc"
)

# Load data
query = """
SELECT * FROM wafer_probe_results;
"""
df = pd.read_sql(query, conn)


# Ensure required columns are present
required_cols = ['id', 'parameter', 'pass_fail']
if not all(col in df.columns for col in required_cols) or df.empty:
    print("Missing required columns or empty dataset.")
else:
    # Total tests per parameter
    total_tests = df.groupby("parameter")["id"].count()

    # Fails per parameter
    fails = df[df["pass_fail"] == "FAIL"].groupby("parameter")["id"].count()

    # Combine and compute fail %
    fail_percentage = (fails / total_tests * 100).round(2)

# Plot
plt.figure(figsize=(10, 5))
fail_percentage.plot(kind="bar", color="tomato", edgecolor="black")
plt.title("FAIL Rate by Test Parameter (%)")
plt.xlabel("Test Parameter")
plt.ylabel("FAIL Rate (%)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()