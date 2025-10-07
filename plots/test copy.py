import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys


import psycopg2
conn = psycopg2.connect(
    dbname="postgres", user="admin", password="ukdtc", host="127.0.0.1", port=15432
)
df = pd.read_sql("SELECT * FROM wafer_probe_results;", conn)
# Check for required columns
required_cols = ['die_x', 'die_y', 'pass_fail', 'parameter']
if df.empty or not all(col in df.columns for col in required_cols):
    print("Missing required columns or empty dataset.")
else:

    # Convert pass/fail to numeric
    df['pass_numeric'] = df['pass_fail'].map({"PASS": 1, "FAIL": 0})

    # Group by die location and average across all wafers
    mean_yield = df.groupby(['die_y', 'die_x'])['pass_numeric'].mean().unstack()

    # Plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        mean_yield.sort_index(ascending=False),
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        square=True,
        linewidths=0.5,
        linecolor='gray',
        cbar_kws={'label': 'Mean Yield (Pass Rate)'}
    )
    plt.title(f"Average Yield Map – Parameter")
    plt.xlabel("Die X")
    plt.ylabel("Die Y")
    plt.tight_layout()
    plt.show()