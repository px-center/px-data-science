SELECT 
    f.created_at,
    f.id AS freight_id,
    f.company_id,
    c.name AS company_name,
    f.contract_days, 
    f.driver_id,
    freights_type(f.type) AS tipo,
    driver_scores_group(ds."group") AS nivel_px
FROM freights f
LEFT JOIN driver_scores ds ON ds.driver_id = f.driver_id
LEFT JOIN companies c ON c.id = f.company_id
WHERE f.status = '300'
  AND f.start_at > '2025-01-31'
  AND driver_scores_group(ds."group") IS NOT NULL
  AND f."type" <> '2';