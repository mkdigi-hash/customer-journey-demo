import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys


import psycopg2
conn = psycopg2.connect(
    dbname="postgres", user="admin", password="ukdtc", host="127.0.0.1", port=15432
)
df = pd.read_sql("SELECT * FROM wafer_probe_results;", conn)

plt.figure(figsize=(8, 6))

sns.boxplot(data=df, x="parameter", y="measured_value")
plt.tight_layout()
plt.show()