import random
import uuid
import time
import csv
import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
import numpy as np
import math

from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/datademo.log', level=logging.INFO)

load_dotenv()

# database connection variables
dbname = os.getenv("POSTGRES_DBNAME")
hostname = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
user = os.getenv("POSTGRES_USER")
pword = os.getenv("POSTGRES_PASSWORD")

# Configuration
NUM_LOTS = 1
WAFERS_PER_LOT = 20
SIZE_OF_DIE = 5     # this is an abitary unit of measurement
TEST_TYPES = ['Parametric', 'Functional']
PARAMETERS = {
    'Parametric': ['Vth', 'Idss', 'Ron', 'Ioff'],
    'Functional': ['Delay', 'Leakage', 'VoltageMargin']
}
ADD_DAYS = 0 # number of days to add to current time

CSV_DIR = Path("test_result_logs")
CSV_DIR.mkdir(exist_ok=True)


def get_timestamped_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return CSV_DIR / f"probe_log_{timestamp}.csv"

def enforce_csv_limit(directory, max_files=7):
    files = sorted(directory.glob("probe_log_*.csv"), key=os.path.getmtime, reverse=True)
    for old_file in files[max_files:]:
        try:
            old_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete old CSV file: {old_file} — {e}")


def generate_lot_id():
    return "LOT" + str(uuid.uuid4().hex[:8]).upper()

def generate_wafer_id(index):
    return f"W{index:02d}"


def generate_die_coordinates(die_size=1, wafer_diameter=200, edge_exclusion=5):
    """
    Simulate die positions on a circular wafer with edge exclusions.

    Parameters:
        die_size (int): Size of each die in arbitrary units.
        wafer_diameter (int): Diameter of the wafer in the same units.
        edge_exclusion (int): Margin from the edge where dies are excluded.

    Returns:
        List of (x, y) tuples representing valid die positions.
    """
    radius = wafer_diameter / 2
    coords = []

    # Define grid bounds
    grid_range = int(wafer_diameter / die_size)
    center = grid_range // 2

    for y in range(-center, center + 1):
        for x in range(-center, center + 1):
            # Convert grid coords to physical space
            phys_x = x * die_size
            phys_y = y * die_size
            dist_from_center = math.sqrt(phys_x**2 + phys_y**2)

            if dist_from_center <= (radius - edge_exclusion):
                coords.append((x + center, y + center))

    return coords


def generate_measure_value(param):
    # Tuned (mean, stddev) to stay within thresholds and create 90–95% pass rates
    normal_params = {
        'Vth': (0.525, 0.015),              # Threshold: 0.4–0.65
        'Idss': (3.5e-4, 1e-4),             # Threshold: 1e-5–1e-3
        'Ron': (4.5, 1.0),                  # Threshold: 2–8
        'Ioff': (5e-10, 1.5e-10),           # Threshold: 1e-11–1e-9
        'Delay': (310, 35),                 # Threshold: 120–450
        'Leakage': (5e-7, 1.5e-7),          # Threshold: 1e-8–1e-6
        'VoltageMargin': (0.35, 0.025)      # Threshold: 0.25–0.45
    }

    mean, stddev = normal_params.get(param, (0.5, 0.1))
    value = np.random.normal(loc=mean, scale=stddev)

    if param in ['Idss', 'Ioff', 'Leakage']:
        value = np.abs(value)  # Take absolute value instead of max(0)

    return round(value, 11)


def generate_measure_value_fails(param):
    # Updated (mean, stddev) to target ~30% fail rate
    # Adjusted means closer to threshold edges and increased stddev
    fail_bias_params = {
        'Vth': (0.39, 0.04),               # Pass: 0.4–0.65 → mean just below min
        'Idss': (1.1e-3, 2e-4),            # Pass: 1e-5–1e-3 → mean slightly above max
        'Ron': (8.5, 1.5),                 # Pass: 2–8 → mean above
        'Ioff': (8e-10, 2e-10),  # Still inside the pass range, allows mix of pass/fail
        'Delay': (470, 70),               # Pass: 120–450 → mean above
        'Leakage': (1.2e-6, 3e-7),         # Pass: 1e-8–1e-6 → mean above
        'VoltageMargin': (0.2, 0.05)       # Pass: 0.25–0.45 → mean below
    }

    mean, stddev = fail_bias_params.get(param, (0.5, 0.1))
    value = np.random.normal(loc=mean, scale=stddev)

    if param in ['Idss', 'Ioff', 'Leakage']:
        value = np.abs(value)  # Ensure non-negative values

    return round(value, 11)

def generate_pass_fail(value, param):
    thresholds = {
        'Vth': (0.4, 0.65),
        'Idss': (1e-5, 1e-3),
        'Ron': (2, 8),
        'Ioff': (1e-11, 1e-9),
        'Delay': (120, 450),
        'Leakage': (1e-8, 1e-6),
        'VoltageMargin': (0.25, 0.45)
    }
    min_val, max_val = thresholds.get(param, (0, 1))
    return 'PASS' if min_val <= value <= max_val else 'FAIL'

def init_csv(csv_file):
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'lot_id', 'wafer_id', 'test_type',
            'die_x', 'die_y', 'parameter',
            'measured_value', 'pass_fail', 'timestamp'
        ])

def append_to_csv(file, row_dict):
    with open(file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            row_dict['lot_id'], row_dict['wafer_id'], row_dict['test_type'],
            row_dict['die_x'], row_dict['die_y'], row_dict['parameter'],
            row_dict['measured_value'], row_dict['pass_fail'], row_dict['timestamp']
        ])

def connect_database(hostname: str, dbname: str, user: str, pword: str, port: int):
    logger.info(f"Connecting to database {hostname}.{dbname}...")
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=pword,
        host=hostname,
        port=15432
    )
    logger.info("Connected!")
    return conn


def stream_probe_data():
    csv_file = get_timestamped_filename()  # at the top of stream_probe_data()
    init_csv(csv_file)

    conn = connect_database(dbname=dbname, hostname=hostname, 
                              port=port, pword=pword, user=user)
    cursor = conn.cursor()

    for _ in range(NUM_LOTS):
        lot_id = generate_lot_id()

        for w in range(1, WAFERS_PER_LOT + 1):
            wafer_id = generate_wafer_id(w)
            test_type = random.choice(TEST_TYPES)
            parameters = PARAMETERS[test_type]
            die_coords = generate_die_coordinates(SIZE_OF_DIE)

            for die_x, die_y in die_coords:
                for param in parameters:
                    measured_value = generate_measure_value(param)
                    result = generate_pass_fail(measured_value, param)
                    timestamp = datetime.now() + timedelta(days=ADD_DAYS)

                    row = {
                        'lot_id': lot_id,
                        'wafer_id': wafer_id,
                        'test_type': test_type,
                        'die_x': die_x,
                        'die_y': die_y,
                        'parameter': param,
                        'measured_value': float(measured_value),
                        'pass_fail': result,
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Insert into DB
                    try:
                        logger.info("Inserting into wafer_probe_results: %s", row)

                        cursor.execute("""
                            INSERT INTO wafer_probe_results (
                                lot_id, wafer_id, test_type, die_x, die_y,
                                parameter, measured_value, pass_fail, timestamp
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row['lot_id'],
                            row['wafer_id'],
                            row['test_type'],
                            row['die_x'],
                            row['die_y'],
                            row['parameter'],
                            row['measured_value'],
                            row['pass_fail'],
                            row['timestamp']
                        ))

                    except psycopg2.Error as e:
                        logger.error("Database insertion error for row %s\nError: %s", row, e)
                        conn.rollback()
                    except Exception as ex:
                        logger.exception("Unexpected error while inserting row: %s", row)
                        conn.rollback()
                    else:
                        conn.commit()
                        logger.debug("Row inserted successfully.")

                    # commit to db
                    conn.commit()

                    # write to CSV
                    append_to_csv(csv_file, row)

                    # log file captures this but added for temp visibility
                    print(f"Inserted & logged: {row['lot_id']} / {row['wafer_id']} / {param} = {measured_value} ({result})")
                    # time.sleep(0.05)  # Simulate probe time, can remove for speed

    cursor.close()
    conn.close()
    print("Streaming and logging complete.")

if __name__ == "__main__":
    stream_probe_data()
