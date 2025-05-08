SELECT 
    f.id AS contract_id,
    driver_id,
    f.company_id,
    c.name AS course_name,
    public.freights_type(f.type) AS contract_type,
    f.destination,
    v.vehicle,
    s.supply,
    tl.load,
    f.created_at,
    f.start_at AS contract_start,
    f.end_at AS contract_end,
    f.contract_days,
    f.price / 100 AS price,
    ROUND((f.price / 100.0) / f.contract_days, 2) AS price_day,
    ca.latitude AS contract_latitude,
    ca.longitude AS contract_longitude

FROM freights f
JOIN company_addresses ca ON f.origin = ca.id
JOIN cities cty ON ca.city_id = cty.id 
JOIN course_freight cf ON cf.freight_id = f.id
JOIN courses c ON cf.course_id = c.id

LEFT JOIN (
    SELECT 
        v1.id AS veiculo_id, 
        v1.reference_id AS ref_veiculo_id, 
        v2.name AS vehicle,
        v2.complexity_level
    FROM vehicles v1
    LEFT JOIN vehicles v2 ON v1.reference_id = v2.id
) v ON f.vehicle_id = v.veiculo_id

LEFT JOIN (
    SELECT 
        v1.id AS supply_id, 
        v1.reference_id AS ref_supply_id,
        v2.name AS supply
    FROM supplies v1
    LEFT JOIN supplies v2 ON v1.reference_id = v2.id
) s ON f.supply_id = s.supply_id

LEFT JOIN (
    SELECT 
        tl.id AS load_id,
        tl.name AS load
    FROM truck_loads tl
) tl ON f.load_id = tl.load_id

WHERE f.status = 300
  AND f.created_at >= '2024-01-01'
  AND f.end_at < NOW()
  AND f.contract_days > 0;

