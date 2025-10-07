import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=15432,
    database="postgres",
    user="admin",
    password="ukdtc"
)

# Load data (you can filter wafer_id/lot_id if needed)
query = """
SELECT die_x, die_y, parameter, measured_value
FROM wafer_probe_results
WHERE wafer_id = 'W01' AND lot_id = 'LOTEDA55E56';
"""
df = pd.read_sql(query, conn)

# Combine die_x and die_y to form a unique identifier for each die
df['die_xy'] = df['die_x'].astype(str) + '_' + df['die_y'].astype(str)

# Pivot so each row is a die, columns are parameters
pivot_df = df.pivot_table(
    index='die_xy',
    columns='parameter',
    values='measured_value',
    aggfunc='mean'  # use mean if duplicates exist
)

# Drop rows with missing values to ensure clean correlation
pivot_df = pivot_df.dropna()

# Compute correlation matrix
corr_matrix = pivot_df.corr(method='pearson')

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', square=True, linewidths=0.5)
plt.title("Test Parameter Correlation Matrix")
plt.tight_layout()
plt.show()
