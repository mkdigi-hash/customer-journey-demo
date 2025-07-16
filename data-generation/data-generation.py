import random
import uuid
import pandas as pd
from datetime import datetime, timedelta

# Configuration
NUM_LOTS = 10
WAFERS_PER_LOT = 25
DIES_PER_WAFER = 100
TEST_TYPES = ['Parametric', 'Functional']
PARAMETERS = {
    'Parametric': ['Vth', 'Idss', 'Ron', 'Ioff'],
    'Functional': ['Delay', 'Leakage', 'VoltageMargin']
}

def generate_lot_id():
    return "LOT" + str(uuid.uuid4().hex[:8]).upper()

def generate_wafer_id(index):
    return f"W{index:02d}"

def generate_die_coordinates(n):
    return [(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)]

def generate_measure_value(param):
    # Simulated measurement value ranges
    ranges = {
        'Vth': (0.3, 0.7),
        'Idss': (1e-6, 1e-3),
        'Ron': (1.0, 10.0),
        'Ioff': (1e-12, 1e-9),
        'Delay': (100, 500),
        'Leakage': (1e-9, 1e-6),
        'VoltageMargin': (0.2, 0.5)
    }
    low, high = ranges.get(param, (0, 1))
    return round(random.uniform(low, high), 6)

def generate_pass_fail(value, param):
    # Simple thresholding logic
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

def generate_data():
    records = []
    base_time = datetime.now()

    for _ in range(NUM_LOTS):
        lot_id = generate_lot_id()
        for w in range(1, WAFERS_PER_LOT + 1):
            wafer_id = generate_wafer_id(w)
            test_type = random.choice(TEST_TYPES)
            parameters = PARAMETERS[test_type]
            die_coords = generate_die_coordinates(DIES_PER_WAFER)

            for die_x, die_y in die_coords:
                for param in parameters:
                    measured_value = generate_measure_value(param)
                    result = generate_pass_fail(measured_value, param)
                    timestamp = base_time + timedelta(seconds=random.randint(0, 100000))
                    records.append({
                        'lot_id': lot_id,
                        'wafer_id': wafer_id,
                        'test_type': test_type,
                        'die_x': die_x,
                        'die_y': die_y,
                        'parameter': param,
                        'measured_value': measured_value,
                        'pass_fail': result,
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = generate_data()
    df.to_csv("synthetic_wafer_probe_data.csv", index=False)
    print("Synthetic wafer probe data generated and saved to 'synthetic_wafer_probe_data.csv'")
