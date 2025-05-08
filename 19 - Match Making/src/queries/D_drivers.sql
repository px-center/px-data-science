WITH experiencia_clt AS (
    SELECT
        driver_id,
        ROUND((COUNT(DISTINCT month_worked) / 6.0)) * 6 / 12.0 AS experiencia_clt_anos
    FROM (
        SELECT 
            driver_id,
            GENERATE_SERIES(
                DATE_TRUNC('month', started_date_at),
                DATE_TRUNC('month', finalized_date_at),
                '1 month'
            ) AS month_worked
        FROM driver_experiences
        WHERE started_date_at IS NOT NULL
          AND finalized_date_at IS NOT NULL
          AND started_date_at < finalized_date_at
          AND started_date_at > NOW() - INTERVAL '70 years'
          AND finalized_date_at > NOW() - INTERVAL '70 years'
          AND started_date_at < NOW()
          AND finalized_date_at < NOW()
    ) experiencia_mensal
    GROUP BY driver_id
),
experiencia_px AS (
    SELECT 
        f.driver_id,
        EXTRACT(YEAR FROM AGE(MAX(f.start_at), MIN(f.start_at))) * 12 +
        EXTRACT(MONTH FROM AGE(MAX(f.start_at), MIN(f.start_at))) AS experiencia_px_meses
    FROM freights f
    WHERE f.status = 300
      AND f.driver_id IS NOT NULL
    GROUP BY f.driver_id
),
cursos_agregados AS (
    SELECT 
        dc.driver_id,
        STRING_AGG(DISTINCT crs.name, ', ' ORDER BY crs.name) AS course_name
    FROM driver_courses dc
    LEFT JOIN courses crs ON dc.course_id = crs.id
    GROUP BY dc.driver_id
)

SELECT 
    d.id AS driver_id,
    d.name,
    d.marital_status,
    d.schooling,
    d.gender,
    d.cnh_category,
    public.drivers_status(d.status) AS driver_status,
    public.drivers_situation_enum(d.situation_enum) AS driver_situation,
    ct.name AS driver_city_name,
    ct.latitude AS driver_latitude,
    ct.longitude AS driver_longitude,
    s.uf AS driver_uf,
    ds.score AS score_nivel_px_atual,
    ds.tier AS nivel_px_atual,
    COALESCE(eclt.experiencia_clt_anos, 0) AS experiencia_clt_anos,
    COALESCE(epx.experiencia_px_meses, 0) AS driver_experiencia_px_meses,
    ca.course_name

FROM drivers d
LEFT JOIN experiencia_clt eclt ON d.id = eclt.driver_id
LEFT JOIN experiencia_px epx ON d.id = epx.driver_id
LEFT JOIN driver_addresses da ON d.id = da.driver_id AND da.type = 0
LEFT JOIN cities ct ON da.city_id = ct.id
LEFT JOIN states s ON ct.state_id = s.id
LEFT JOIN driver_scores ds ON d.id = ds.driver_id
LEFT JOIN cursos_agregados ca ON d.id = ca.driver_id

WHERE d.name IS NOT NULL
  AND d.name != 'anonymous';



