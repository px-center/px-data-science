WITH driver_start AS (
  SELECT 
    driver_id,
    DATE_TRUNC('month', MIN(start_at)) AS first_month
  FROM freights
  WHERE status = 300
  and freights_type("type") = 'Coleta/Entrega'
  GROUP BY driver_id
),
contracts_with_month AS (
  SELECT 
    f.driver_id,
    f.start_at,
    -- Calcula a diferença em meses entre o mês do contrato e o mês inicial do motorista.
    (DATE_PART('year', f.start_at) * 12 + DATE_PART('month', f.start_at)) -
    (DATE_PART('year', ds.first_month) * 12 + DATE_PART('month', ds.first_month)) AS activity_month
  FROM freights f
  JOIN driver_start ds 
    ON f.driver_id = ds.driver_id
  WHERE f.status = 300
  and freights_type("type") = 'Coleta/Entrega'
),
contracts_by_driver AS (
  SELECT 
    driver_id,
    activity_month,
    COUNT(*) AS contracts_count
  FROM contracts_with_month
  GROUP BY driver_id, activity_month
)
SELECT 
  activity_month,
  AVG(contracts_count) AS avg_contracts_per_month
FROM contracts_by_driver
GROUP BY activity_month
ORDER BY activity_month;






