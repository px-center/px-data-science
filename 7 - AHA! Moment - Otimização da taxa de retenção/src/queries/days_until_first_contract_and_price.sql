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
)
SELECT
    q.type,
    q.status,
    q.driver_id,
    q.weeks_from_qualification_to_end AS week,
    COUNT(*) OVER (
        PARTITION BY q.driver_id 
        ORDER BY q.weeks_from_qualification_to_end 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS total_contracts_until_week,
    SUM(q.price) OVER (
        PARTITION BY q.driver_id 
        ORDER BY q.weeks_from_qualification_to_end 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS total_value_until_week
FROM qualified_freights q
ORDER BY q.driver_id, week;
