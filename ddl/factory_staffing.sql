CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS factory_staffing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    shift CHAR(1) NOT NULL CHECK (shift IN ('A', 'B', 'C')),
    employee_id VARCHAR(10) NOT NULL,
    employee_level INT NOT NULL CHECK (employee_level BETWEEN 1 AND 5),
    area TEXT NOT NULL,
    UNIQUE (date, shift, employee_id)
);

-- Indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_factory_staffing_date ON factory_staffing (date);
CREATE INDEX IF NOT EXISTS idx_factory_staffing_shift ON factory_staffing (shift);
CREATE INDEX IF NOT EXISTS idx_factory_staffing_area ON factory_staffing (area);
