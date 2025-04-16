WITH qualified_freights AS (
    SELECT 
        f.driver_id,
        f.company_id,
        d.qualified_at,
        f.end_at,
        f.price / 100 AS price,
        CASE 
            WHEN drivers_situation_enum(d.situation_enum) IN ('Rodando', 'Indisponível temporariamente', 'Disponível') THEN 'Active'
            WHEN drivers_situation_enum(d.situation_enum) = 'Indisponível' THEN 'Churn'
        END AS status,
        freights_type(f.type) AS type,
        FLOOR(EXTRACT(EPOCH FROM (f.end_at - d.qualified_at)) / (60 * 60 * 24 * 7)) AS weeks_from_qualification_to_end
    FROM freights f
    JOIN drivers d ON d.id = f.driver_id
    WHERE f.status = 300
      AND d.qualified_at IS NOT NULL
      AND d.qualified_at >= CURRENT_DATE - INTERVAL '1 year'
      AND drivers_situation_enum(d.situation_enum) IN ('Indisponível', 'Indisponível temporariamente', 'Disponível', 'Rodando')
      AND freights_type(f.type) = 'Coleta/Entrega'
)
SELECT 
    driver_id,
    MAX(weeks_from_qualification_to_end) AS week_max,
    COUNT(*) AS total_contracts,
    SUM(price) AS total_value,
    
    2.6 AS aha_week,
    2.7 AS aha_qt_contracts,
    1519.78 AS aha_value,

    CASE WHEN MAX(weeks_from_qualification_to_end) > 2.6 THEN 'yes' ELSE 'no' END AS crossed_aha_week,
    CASE WHEN COUNT(*) > 2.7 THEN 'yes' ELSE 'no' END AS crossed_aha_contracts,
    CASE WHEN SUM(price) > 1519.78 THEN 'yes' ELSE 'no' END AS crossed_aha_value,

    CEIL(GREATEST(2.6 - MAX(weeks_from_qualification_to_end), 0) * 7) AS days_to_aha,
    CEIL(GREATEST(2.7 - COUNT(*), 0)) AS contracts_gap_to_aha,
    GREATEST(1519.78 - SUM(price), 0) AS value_gap_to_aha,

    CASE 
        WHEN 
            MAX(weeks_from_qualification_to_end) > 2.6 AND 
            COUNT(*) > 2.7 AND 
            SUM(price) > 1519.78 
        THEN 'yes'
        ELSE 'no'
    END AS full_aha

FROM qualified_freights
GROUP BY driver_id
ORDER BY driver_id;

