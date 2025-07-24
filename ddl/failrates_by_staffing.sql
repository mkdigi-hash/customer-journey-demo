
create view failrates_by_staffing as (
-- Daily staffing levels
WITH daily_staffing AS (
    SELECT
        date,
        COUNT(DISTINCT employee_id) AS staffing_level
    FROM factory_staffing
    GROUP BY date
),

-- Daily failure rates
daily_fail_rates AS (
    SELECT
        DATE(timestamp) AS date,
        (COUNT(*) FILTER (WHERE pass_fail = 'FAIL')::float / COUNT(*))::float AS failure_rate,
        COUNT(*) AS total_tests
    FROM wafer_probe_results_midterm
    GROUP BY DATE(timestamp)
)

-- Match by date
SELECT
    s.date,
    s.staffing_level,
    f.failure_rate,
    f.total_tests
FROM daily_staffing s
JOIN daily_fail_rates f ON s.date = f.date
ORDER BY s.date
);