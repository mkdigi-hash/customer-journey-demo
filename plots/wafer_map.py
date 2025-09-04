import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys


import psycopg2
conn = psycopg2.connect(
    dbname="postgres", user="admin", password="ukdtc", host="127.0.0.1", port=15432
)
df = pd.read_sql("SELECT * FROM wafer_probe_results_midterm;", conn)

# === Override these to select a wafer and parameter ===
# wafer_id = None
# parameter = "Delay"

# # === Filter the data ===
# if wafer_id and parameter:
#     filtered_df = df[(df["wafer_id"] == wafer_id) & (df["parameter"] == parameter)]
# else:
#     print("Missing wafer_id or parameter in dataset.")
#     sys.exit()
filtered_df = df
# === Validate required columns ===
required_cols = ['die_x', 'die_y', 'measured_value']
if filtered_df.empty or not all(col in filtered_df.columns for col in required_cols):
    print("Missing required data or columns.")
    sys.exit()

# === Pivot table for heatmap ===
heatmap_data = filtered_df.pivot_table(
    index='die_y', columns='die_x', values='measured_value', aggfunc='mean'
)

# === Plot the wafer map ===
plt.figure(figsize=(8, 6))
sns.heatmap(
    heatmap_data.sort_index(ascending=False),
    cmap='coolwarm',
    cbar_kws={'label': 'Measured Value'},
    square=True
)

# plt.title(f"Wafer Map: {wafer_id} – {parameter}")
plt.xlabel("Die X")
plt.ylabel("Die Y")
plt.tight_layout()
plt.show()




"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys

# Power BI automatically loads the dataset into `dataset`
df = dataset.copy()

# === Parameters ===
wafer_id = df['wafer_id'].iloc[0]
parameter = df['parameter'].iloc[0]


# === Filter ===
filtered_df = df[(df["wafer_id"] == wafer_id) & (df["parameter"] == parameter)]

required_cols = ['die_x', 'die_y', 'measured_value']
if filtered_df.empty or not all(col in filtered_df.columns for col in required_cols):
    print("Missing required data or columns.")
    sys.exit()

# === Pivot ===
heatmap_data = filtered_df.pivot_table(
    index='die_y', columns='die_x', values='measured_value', aggfunc='mean'
)

# === Plot ===
plt.figure(figsize=(8, 6))
sns.heatmap(
    heatmap_data.sort_index(ascending=False),
    cmap='coolwarm',
    cbar_kws={'label': 'Measured Value'},
    square=True
)

plt.title(f"Wafer Map: {wafer_id} – {parameter}")
plt.xlabel("Die X")
plt.ylabel("Die Y")
plt.tight_layout()

# === Important: Save to Power BI image output ===
plt.show()


"""