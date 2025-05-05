SELECT 
    fh.freight_id,
    freights_type(f."type") as type,
    EXTRACT(EPOCH FROM (new_value::timestamp - old_value::timestamp)) / 3600 AS hours_diff
FROM freight_histories fh 
left join freights f on f.id = fh.freight_id
WHERE fh.key = 'start_at'
AND new_value::timestamp > old_value::timestamp
order by hours_diff desc