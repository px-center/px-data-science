SELECT 
    f.created_at,
    fh.freight_id,
    f.driver_id,
    f.company_id,
    f.contract_days as contract_days_final,
    freights_type(f.type) AS tipo,
    EXTRACT(EPOCH FROM (fh.old_value::timestamp - fh.new_value::timestamp)) / 86400 AS dias_reducao,
    driver_scores_group(ds."group") AS nivel_px
FROM freight_histories fh
JOIN freights f ON f.id = fh.freight_id
JOIN freight_extra_days fed
    ON fed.decided_at = fh.updated_at
    AND fed.status = 2
    AND fed."type" = 1
LEFT JOIN driver_scores ds ON ds.driver_id = f.driver_id
WHERE fh."key" = 'end_at'
  AND fh.old_value > fh.new_value
  AND f.status = '300'
  AND fh.created_at > fh.new_value::timestamp
  and f."type" <> '2'
ORDER BY fh.freight_id DESC;