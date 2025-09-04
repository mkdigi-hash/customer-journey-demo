import pandas as pd
import psycopg2
import seaborn as sns
import matplotlib.pyplot as plt

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=15432,
    database="postgres",
    user="admin",
    password="ukdtc"
)

# Load measured values
query = """
SELECT measured_value
FROM wafer_probe_results
WHERE measured_value IS NOT NULL
AND parameter = 'Vth';
"""
df = pd.read_sql(query, conn)

# Plot histogram with KDE
plt.figure(figsize=(10, 6))
sns.histplot(df['measured_value'], kde=True, bins=50, color='steelblue')

plt.title("Distribution of Measured Values")
plt.xlabel("Measured Value")
plt.show()
