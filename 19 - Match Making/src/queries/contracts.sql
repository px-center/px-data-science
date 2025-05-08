WITH favoritos_bloqueios AS (
    SELECT
        COALESCE(fav.driver_id, blk.driver_id) AS driver_id,
        COALESCE(fav.company_id, blk.company_id) AS company_id,
        COALESCE(fav.favorite_driver, 0) AS favorite_driver,
        COALESCE(blk.block_driver, 0) AS block_driver,
        fav.dt_first_favorite,
        blk.dt_first_block
    FROM (
        SELECT 
            driver_id, 
            company_id, 
            MIN(created_at) AS dt_first_favorite,
            1 AS favorite_driver
        FROM company_favorite_drivers
        GROUP BY driver_id, company_id
    ) fav
    FULL OUTER JOIN (
        SELECT 
            driver_id, 
            company_id, 
            MIN(created_at) AS dt_first_block,
            1 AS block_driver
        FROM company_driver_block
        WHERE deleted_at IS NULL
        GROUP BY driver_id, company_id
    ) blk
    ON fav.driver_id = blk.driver_id AND fav.company_id = blk.company_id
)

SELECT 
    f.company_id,
    cf.course_id,
    public.companies_client_status(co.status) AS company_status,
    f.id AS contract_id,
    public.freights_status(f.status) AS contract_status,
    public.freights_type(f.type) AS contract_type,
    v.complexity_level,
    v.vehicle,
    s.supply,
    tl.load,
    f.created_at,
    f.start_at AS contract_start,
    f.end_at AS contract_end,
    f.contract_days,
    c.name AS contract_city,
    ca.latitude AS contract_latitude,
    ca.longitude AS contract_longitude,
    f.driver_id,
    dsc.score AS score_px_contract_start,
    dsc.tier AS nivel_px_contract_start,
    COALESCE(fb.favorite_driver, 0) AS favorite_driver,
    COALESCE(fb.block_driver, 0) AS block_driver,
    fb.dt_first_favorite,
    fb.dt_first_block

FROM freights f
JOIN company_addresses ca ON f.origin = ca.id
JOIN cities c ON ca.city_id = c.id 
join course_freight cf on cf.freight_id = f.id
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

LEFT JOIN favoritos_bloqueios fb 
  ON f.driver_id = fb.driver_id AND f.company_id = fb.company_id

WHERE f.status = 300
  AND f.created_at >= '2024-08-01'
  AND f.end_at < NOW();

select * from course_freight cf 
