import pandas as pd
import random
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

# Load DB credentials
load_dotenv()
dbname = os.getenv("POSTGRES_DBNAME")
hostname = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
user = os.getenv("POSTGRES_USER")
pword = os.getenv("POSTGRES_PASSWORD")

# Configuration
shifts = ['A', 'B', 'C']
areas = ['Etching', 'Lithography', 'Metrology', 'Implantation', 'Chemical Mechanical Planarization']
level_to_years = {1: 0.5, 2: 1.5, 3: 3.0, 4: 5.0, 5: 7.5}

start_date = datetime(2025, 7, 1)
end_date = datetime(2025, 9, 12)

# --- Create pool of 250 unique employees ---
employee_pool = []
for i in range(250):
    emp_id = f"E{i+1}"
    emp_level = random.choices([2, 3, 4, 5], weights=[0.2, 0.3, 0.3, 0.2])[0]
    area = random.choice(areas)
    employee_pool.append({
        'employee_id': emp_id,
        'employee_level': emp_level,
        'area': area
    })

records = []

for day in pd.date_range(start_date, end_date):
    for shift in shifts:
        # Define two separate low staffing periods
        low_period_1 = datetime(2025, 7, 9) <= day <= datetime(2025, 7, 14)
        low_period_2 = datetime(2025, 8, 1) <= day <= datetime(2025, 8, 14)
        is_low_period = low_period_1 or low_period_2

        if is_low_period:
            num_staff = random.randint(8, 10)
        else:
            num_staff = random.randint(16, 20)

        # Sample employees from the pool
        selected_employees = random.sample(employee_pool, num_staff)

        for emp in selected_employees:
            records.append({
                'date': day.date(),
                'shift': shift,
                'employee_id': emp['employee_id'],
                'employee_level': emp['employee_level'],
                'area': emp['area']
            })

# Convert to DataFrame
df_hr = pd.DataFrame(records)

# Save to CSV
df_hr.to_csv("hr_staffing_log.csv", index=False)

# Insert into PostgreSQL
def insert_hr_data_to_db(df):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=pword,
            host=hostname,
            port=port
        )
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO factory_staffing (
                date, shift, employee_id, employee_level, area
            ) VALUES (%s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['date'],
                row['shift'],
                row['employee_id'],
                row['employee_level'],
                row['area']
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print("HR staffing data inserted into database.")

    except Exception as e:
        print("Error inserting HR data into DB:", e)

# Run the insert
insert_hr_data_to_db(df_hr)
