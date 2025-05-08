WITH favoritos_bloqueios AS (
    SELECT
        COALESCE(fav.driver_id, blk.driver_id) AS driver_id,
        COALESCE(fav.company_id, blk.company_id) AS company_id,
        fav.dt_first_favorite,
        blk.dt_first_block
    FROM (
        SELECT 
            driver_id, 
            company_id, 
            MIN(created_at) AS dt_first_favorite
        FROM company_favorite_drivers
        GROUP BY driver_id, company_id
    ) fav
    FULL OUTER JOIN (
        SELECT 
            driver_id, 
            company_id, 
            MIN(created_at) AS dt_first_block
        FROM company_driver_block
        WHERE deleted_at IS NULL
        GROUP BY driver_id, company_id
    ) blk
    ON fav.driver_id = blk.driver_id AND fav.company_id = blk.company_id
),
contratos_empresa_motorista AS (
    SELECT
        company_id,
        driver_id,
        COUNT(*) AS qt_contracts
    FROM freights
    WHERE driver_id IS NOT NULL
    GROUP BY company_id, driver_id
)

SELECT 
    cem.company_id,
    cem.driver_id,
    cem.qt_contracts,
    fb.dt_first_favorite,
    fb.dt_first_block
FROM contratos_empresa_motorista cem
LEFT JOIN favoritos_bloqueios fb
    ON cem.company_id = fb.company_id AND cem.driver_id = fb.driver_id;

select driver_id, company_id, created_at, 'favoritado' as "action"  from company_favorite_driver_histories cfdh  where driver_id is not null order by company_id, driver_id 

------------------------------------------------------------------------------------------------------------------------------


WITH favoritos_ranked AS (
    SELECT 
        NULL AS contract_id,
        driver_id, 
        company_id, 
        created_at, 
        'favoritado' AS action,
        'company_favorite_driver_histories' AS origem,
        ROW_NUMBER() OVER (PARTITION BY driver_id, company_id ORDER BY created_at DESC) AS rn
    FROM company_favorite_driver_histories
    WHERE driver_id IS NOT NULL
),
bloqueios_ranked AS (
    SELECT 
        NULL AS contract_id,
        driver_id, 
        company_id, 
        created_at, 
        'bloqueado' AS action,
        'company_driver_block' AS origem,
        ROW_NUMBER() OVER (PARTITION BY driver_id, company_id ORDER BY created_at DESC) AS rn
    FROM company_driver_block
    WHERE driver_id IS NOT NULL
)

SELECT 
    contract_id,
    driver_id, 
    company_id, 
    created_at, 
    action,
    origem
FROM favoritos_ranked
WHERE rn = 1

UNION ALL

SELECT 
    contract_id,
    driver_id, 
    company_id, 
    created_at, 
    action,
    origem
FROM bloqueios_ranked
WHERE rn = 1

ORDER BY company_id, driver_id, created_at;

occurrences_type()


