SELECT 
    f.created_at,
    f.id as freight_id,
    f.driver_id,
    freights_type(f.type) AS tipo,
    driver_scores_group(ds."group") AS nivel_px
FROM freights f
LEFT JOIN driver_scores ds ON ds.driver_id = f.driver_id
WHERE f.status = '300'
and f.star;