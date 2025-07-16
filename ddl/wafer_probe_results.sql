CREATE TABLE wafer_probe_results (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50),
    wafer_id VARCHAR(10),
    test_type VARCHAR(50),
    die_x INTEGER,
    die_y INTEGER,
    parameter VARCHAR(50),
    measured_value DOUBLE PRECISION,
    pass_fail VARCHAR(10),
    timestamp TIMESTAMP,
    fault_cause VARCHAR(50)
);

