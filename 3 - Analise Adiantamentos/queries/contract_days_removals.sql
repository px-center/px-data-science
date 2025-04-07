SELECT 
    f.created_at AS contract_created_at,
    f.end_at AS contract_end_at,
    fed.created_at AS fed_created_at,
    EXTRACT(EPOCH FROM (fed.created_at - f.end_at)) / 86400 AS days_to_contract_end,
    fed.days::float AS days,
    CASE fed.type
        WHEN 0 THEN 'add'
        WHEN 1 THEN 'remove'
    END AS action
FROM freight_extra_days fed
LEFT JOIN freights f 
    ON f.id = fed.freight_id
WHERE f.type = '1'
ORDER BY fed.type DESC
