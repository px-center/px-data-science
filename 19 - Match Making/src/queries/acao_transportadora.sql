WITH favoritos_ranked AS (
    SELECT 
        NULL::BIGINT AS contract_id,
        driver_id, 
        company_id, 
        created_at, 
        'favoritado' AS action,
        'company_favorite_driver_histories' AS origem,
        ROW_NUMBER() OVER (
            PARTITION BY driver_id, company_id 
            ORDER BY created_at DESC
        ) AS rn
    FROM company_favorite_driver_histories
    WHERE driver_id IS NOT NULL
),
bloqueios_ranked AS (
    SELECT 
        NULL::BIGINT AS contract_id,
        driver_id, 
        company_id, 
        created_at, 
        'bloqueado' AS action,
        'company_driver_block' AS origem,
        ROW_NUMBER() OVER (
            PARTITION BY driver_id, company_id 
            ORDER BY created_at DESC
        ) AS rn
    FROM company_driver_block
    WHERE driver_id IS NOT NULL
),
eventos_unificados AS (
    SELECT 
        id AS contract_id, 
        driver_id, 
        company_id, 
        created_at, 
        'selecionado' AS action,
        'freights' AS origem
    FROM freights
    WHERE driver_id IS NOT NULL

    UNION ALL

    SELECT 
        freight_id AS contract_id, 
        driver_id, 
        company_id, 
        created_at, 
        'Like' AS action,
        'driver_ratings' AS origem
    FROM driver_ratings 
    WHERE rating = 5 AND freight_id IS NOT NULL

    UNION ALL

    SELECT 
        freight_id AS contract_id, 
        driver_id, 
        company_id, 
        created_at, 
        'Dislike' AS action,
        'driver_ratings' AS origem
    FROM driver_ratings 
    WHERE rating < 4 AND freight_id IS NOT NULL

    UNION ALL

    SELECT 
        b.contract_id, 
        f.driver_id, 
        f.company_id, 
        b.created_at, 
        b.action,
        'driver_contract_bonuses' AS origem
    FROM (
        SELECT 
            contract_id,  
            created_at,  
            'Bonus' AS action
        FROM driver_contract_bonuses
    ) b
    LEFT JOIN freights f ON b.contract_id = f.id

    UNION ALL

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
)

SELECT *
FROM eventos_unificados
WHERE created_at >= '2024-01-01'
ORDER BY company_id, driver_id, created_at;


