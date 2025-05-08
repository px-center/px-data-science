WITH company_base AS (
    SELECT 
        c.id AS company_id,
        c.created_at,
        ceg.name AS economic_group,
        cm.name AS company_multitenancy,
        c.qtd_trucks,
        companies_client_status(c.client_status) AS client_status
    FROM companies c
    LEFT JOIN company_economic_groups ceg 
        ON c.company_economic_group_id = ceg.id
    LEFT JOIN company_multitenancy cm 
        ON c.company_multitenancy_id = cm.id
    WHERE c.created_at > '2024-01-01'
      AND c.client_status IS NOT NULL
),

products_pivot AS (
    SELECT 
        company_id,
        CASE 
            WHEN BOOL_OR(status) FILTER (WHERE product = 'personalized_content') THEN 'sim'
            ELSE 'nao'
        END AS personalized_content,
        
        MIN(created_at) FILTER (WHERE product = 'personalized_content') AS personalized_content_start,

        CASE 
            WHEN BOOL_OR(status) FILTER (WHERE product = 'telemetry') THEN 'sim'
            ELSE 'nao'
        END AS telemetry,
        
        MIN(created_at) FILTER (WHERE product = 'telemetry') AS telemetry_start
    FROM academy_product_sells
    GROUP BY company_id
)

SELECT 
    cb.*,
    pp.personalized_content,
    pp.personalized_content_start,
    pp.telemetry,
    pp.telemetry_start
FROM company_base cb
LEFT JOIN products_pivot pp ON cb.company_id = pp.company_id;





