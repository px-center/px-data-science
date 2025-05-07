WITH drivers_base AS (
    SELECT 
        d.id AS "Driver ID",
        d.qualified_at,
        CASE 
            WHEN drivers_situation_enum(d.situation_enum) IN ('Rodando', 'Indisponível temporariamente', 'Disponível') THEN 'Active'
            WHEN drivers_situation_enum(d.situation_enum) = 'Indisponível' THEN 'Churn'
        END AS status_motorista
    FROM drivers d
    WHERE d.qualified_at IS NOT NULL
      AND drivers_situation_enum(d.situation_enum) IN (
          'Indisponível', 'Indisponível temporariamente', 'Disponível', 'Rodando'
      )
),
diarias AS (
    SELECT
        db."Driver ID",
        db.qualified_at,
        db.status_motorista,
        COALESCE(SUM(f.price / 100.0), 0) AS valor_total_diaria,
        COUNT(f.id) AS contagem_total_diaria
    FROM drivers_base db
    LEFT JOIN freights f ON f.driver_id = db."Driver ID" AND freights_type(f.type) = 'Diária'
    GROUP BY db."Driver ID", db.qualified_at, db.status_motorista
),
coletas AS (
    SELECT
        db."Driver ID",
        db.qualified_at,
        db.status_motorista,
        COALESCE(SUM(f.price / 100.0), 0) AS valor_total_coleta_entrega,
        COUNT(f.id) AS contagem_total_coleta_entrega
    FROM drivers_base db
    LEFT JOIN freights f ON f.driver_id = db."Driver ID" AND freights_type(f.type) = 'Coleta/Entrega'
    GROUP BY db."Driver ID", db.qualified_at, db.status_motorista
),
estatisticas_aha AS (
    SELECT
        di."Driver ID",
        di.status_motorista,
        di.valor_total_diaria,
        di.contagem_total_diaria,
        co.valor_total_coleta_entrega,
        co.contagem_total_coleta_entrega,
        EXTRACT(EPOCH FROM (NOW() - di.qualified_at)) / (7 * 24 * 60 * 60) AS semanas_desde_qualificacao,
        
        -- Dias e gaps
        CEIL(GREATEST(2.8 - EXTRACT(EPOCH FROM (NOW() - di.qualified_at)) / (7 * 24 * 60 * 60), 0) * 7) AS days_to_aha_diaria,
        CEIL(GREATEST(2.1 - di.contagem_total_diaria, 0)) AS contracts_gap_to_aha_diaria,
        GREATEST(2954.92 - di.valor_total_diaria, 0) AS value_gap_to_aha_diaria,
        CEIL(GREATEST(2.6 - EXTRACT(EPOCH FROM (NOW() - co.qualified_at)) / (7 * 24 * 60 * 60), 0) * 7) AS days_to_aha_coleta_entrega,
        CEIL(GREATEST(2.7 - co.contagem_total_coleta_entrega, 0)) AS contracts_gap_to_aha_coleta_entrega,
        GREATEST(1519.78 - co.valor_total_coleta_entrega, 0) AS value_gap_to_aha_coleta_entrega,
        
        -- Nova coluna: Motorista coleta entrega
        CASE 
            WHEN co.valor_total_coleta_entrega = 0 AND co.contagem_total_coleta_entrega = 0 THEN 'não'
            ELSE 'sim'
        END AS "Motorista coleta entrega",
        
        -- Atingiu AHA coleta entrega
        CASE
            WHEN EXTRACT(EPOCH FROM (NOW() - co.qualified_at)) / (7 * 24 * 60 * 60) > 2.6
             AND co.contagem_total_coleta_entrega > 2.7
             AND co.valor_total_coleta_entrega > 1519.78
            THEN 'sim'
            ELSE 'não'
        END AS "Atingiu AHA! coleta entrega",
        
        -- Nova coluna: Motorista diária
        CASE 
            WHEN di.valor_total_diaria = 0 AND di.contagem_total_diaria = 0 THEN 'não'
            ELSE 'sim'
        END AS "Motorista diária",
        
        -- Atingiu AHA diária
        CASE
            WHEN EXTRACT(EPOCH FROM (NOW() - di.qualified_at)) / (7 * 24 * 60 * 60) > 2.8
             AND di.contagem_total_diaria > 2.1
             AND di.valor_total_diaria > 2954.92
            THEN 'sim'
            ELSE 'não'
        END AS "Atingiu AHA! diária",
        
        -- Nova coluna: Atingiu AHA! geral
        CASE
            WHEN (EXTRACT(EPOCH FROM (NOW() - co.qualified_at)) / (7 * 24 * 60 * 60) > 2.6
                  AND co.contagem_total_coleta_entrega > 2.7
                  AND co.valor_total_coleta_entrega > 1519.78)
             OR (EXTRACT(EPOCH FROM (NOW() - di.qualified_at)) / (7 * 24 * 60 * 60) > 2.8
                  AND di.contagem_total_diaria > 2.1
                  AND di.valor_total_diaria > 2954.92)
            THEN 'sim'
            ELSE 'não'
        END AS "Atingiu AHA!",
        
        -- Nova coluna: Já realizou contrato
        CASE
            WHEN (co.valor_total_coleta_entrega = 0 AND co.contagem_total_coleta_entrega = 0)
             AND (di.valor_total_diaria = 0 AND di.contagem_total_diaria = 0)
            THEN 'não'
            ELSE 'sim'
        END AS "ja_realizou_contrato"
        
    FROM diarias di
    LEFT JOIN coletas co ON co."Driver ID" = di."Driver ID"
)
SELECT *
FROM estatisticas_aha
WHERE status_motorista = 'Active';


