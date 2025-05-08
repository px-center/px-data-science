WITH cursos_por_contrato AS (
    SELECT 
        cf.freight_id AS contract_id,
        STRING_AGG(DISTINCT c.name, ', ' ORDER BY c.name) AS course_name
    FROM course_freight cf
    JOIN courses c ON cf.course_id = c.id
    GROUP BY cf.freight_id
)

SELECT 
    f.id AS contract_id,
    cpc.course_name,
    ct.model,
    public.freights_type(f.type) AS contract_type,
    v.vehicle,
    s.supply,
    tl.name AS load,
    f.created_at,
    f.start_at AS contract_start,
    f.end_at AS contract_end,
    f.contract_days,
    ROUND((f.price / 100.0) / f.contract_days, 2) AS price_day,
    ca.latitude AS contract_latitude,
    ca.longitude AS contract_longitude

FROM freights f
LEFT JOIN cursos_por_contrato cpc ON f.id = cpc.contract_id
LEFT JOIN company_addresses ca ON f.origin = ca.id
LEFT JOIN cities cty ON ca.city_id = cty.id
LEFT JOIN company_trucks ct ON f.company_id = ct.company_id AND ct.deleted_at IS NULL

-- Veículo
LEFT JOIN (
    SELECT 
        v1.id AS veiculo_id, 
        v2.name AS vehicle
    FROM vehicles v1
    LEFT JOIN vehicles v2 ON v1.reference_id = v2.id
) v ON f.vehicle_id = v.veiculo_id

-- Suprimento
LEFT JOIN (
    SELECT 
        s1.id AS supply_id,
        s2.name AS supply
    FROM supplies s1
    LEFT JOIN supplies s2 ON s1.reference_id = s2.id
) s ON f.supply_id = s.supply_id

-- Carga
LEFT JOIN truck_loads tl ON f.load_id = tl.id

WHERE f.status = 300
  AND f.created_at >= '2024-01-01'
  AND f.end_at < NOW()
  AND f.contract_days > 0;



