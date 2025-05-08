SELECT 
    f.company_id,
    ct.model,
    public.freights_type(f.type) AS contract_type,
    v.complexity_level,
    v.vehicle,
    s.supply,
    tl.load,
    f.start_at AS contract_start,
    f.end_at AS contract_end,
    f.contract_days,
    f.driver_id,
    dsc.score AS score_px_contract_start,
    dsc.tier AS nivel_px_contract_start

FROM freights f
JOIN company_addresses ca ON f.origin = ca.id
LEFT JOIN company_trucks ct ON f.company_id = ct.company_id AND ct.deleted_at IS NULL
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
LEFT JOIN public.companies co ON f.company_id = co.id
LEFT JOIN LATERAL (
    SELECT dsc.score, dsc.tier
    FROM driver_score_compositions dsc
    WHERE dsc.driver_id = f.driver_id
      AND dsc.created_at <= f.start_at
    ORDER BY dsc.created_at DESC
    LIMIT 1
) dsc ON true

WHERE f.status = 300
  AND f.created_at >= '2024-01-01'
  AND f.end_at < NOW()
  AND public.companies_client_status(co.status) != 'Churn';




