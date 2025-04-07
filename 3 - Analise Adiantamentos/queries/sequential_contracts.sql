WITH cte AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY start_at) AS rn,
    ROW_NUMBER() OVER (PARTITION BY driver_id, company_id ORDER BY start_at) AS rn_company
  FROM freights
  where type = '1'
)
SELECT
  driver_id,
  company_id,
  MIN(start_at) AS inicio_periodo,      -- opcional: data de início do período
  MAX(end_at) AS fim_periodo,             -- opcional: data de fim do período
  SUM(contract_days) AS total_dias_agenciados,
  sum(price/100) as total_price,
  COUNT(*) AS contratos_consecutivos,
  SUM(contract_days) * 1.0 / COUNT(*) AS media_dias_por_contrato
FROM cte
GROUP BY
  driver_id,
  company_id,
  rn - rn_company    -- identificador da "ilha" de contratos consecutivos
having COUNT(*) > 1
  ORDER BY
  driver_id,
  inicio_periodo

  
  