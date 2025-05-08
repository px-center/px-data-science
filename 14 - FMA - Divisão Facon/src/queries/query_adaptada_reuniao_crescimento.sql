SELECT 
  "Id contrato",
  "Data do evento",
  "Tipo do evento",
  "Sequência dos eventos"
FROM (
  WITH events_timeline AS (
    SELECT 
      freight_id,
      CASE
        WHEN ft.event_name = 'freight_change' THEN 'changed'
        WHEN ft.event_name = 'start_at_change' THEN 'postponed'
        WHEN ft.event_name = 'freight_created' THEN 'created'
        WHEN ft.event_name = 'canceled' AND (user_type IS NULL OR user_type = 'App\Models\User') THEN 'canceled_by_user'
        WHEN ft.event_name = 'canceled' AND user_type = 'App\Models\CompanyMultilevel' THEN 'canceled_by_company_multilevel'
        ELSE event_name
      END AS event_name,
      ft.event_date
    FROM freight_timeline ft
    WHERE ft.event_name IN ('freight_created', 'freight_change', 'canceled', 'start_at_change')

    UNION ALL

    -- Correção feita apenas aqui:
    SELECT 
      ft.freight_id,
      'expired' AS event_name,
      ft.event_date
    FROM freight_timeline ft
    LEFT JOIN freight_timeline ft2 
      ON ft2.freight_id = ft.freight_id
      AND ft2.event_date <= ft.event_date
      AND ft2.event_name IN ('has_driver', 'canceled', 'removed_driver')
    INNER JOIN freight_timeline ft_created
      ON ft_created.freight_id = ft.freight_id
      AND ft_created.event_name = 'freight_created'
      AND ft_created.event_date <= ft.event_date
    WHERE ft.event_date < NOW()
      AND ft.event_name = 'freight_start_at'
    GROUP BY ft.freight_id, ft.event_date, ft.event_name
    HAVING REGEXP_REPLACE(REPLACE(ARRAY_TO_STRING(ARRAY_AGG(ft2.event_name ORDER BY ft2.event_date, ft2.priority), ','), 'has_driver,removed_driver', ''), ',+', ',') IN (',', '')

    UNION ALL

    SELECT 
      ft.freight_id,
      'success' AS event_name,
      ft.event_date
    FROM freight_timeline ft
    LEFT JOIN freight_timeline ft2 
      ON ft2.freight_id = ft.freight_id
      AND ft2.event_date < ft.event_date
      AND ft2.event_name IN ('check_insurance', 'removed_driver')
    WHERE ft.event_date < NOW()
      AND ft.event_name = 'check_insurance'
    GROUP BY ft.freight_id, ft2.freight_id, ft.event_date, ft.event_name
    HAVING (ft2.freight_id IS NULL OR ARRAY_TO_STRING(ARRAY_AGG(ft2.event_name ORDER BY ft2.event_date, ft2.priority), ',') LIKE '%removed_driver')
  )
  
  SELECT 
    et.freight_id AS "Id contrato",
    et.event_date AS "Data do evento",
    CASE et.event_name
      WHEN 'canceled_by_company_multilevel' THEN 'cancelado_pelo_cliente'
      WHEN 'canceled_by_user' THEN 'cancelado_internamente'
      WHEN 'changed' THEN 'contrato_alterado'
      WHEN 'expired' THEN 'contrato_expirado'
      WHEN 'postponed' THEN 'contrato_postergado'
      WHEN 'success' THEN 'contrato_atendido'
      WHEN 'created' THEN 'contrato_criado'
    END AS "Tipo do evento",
    ROW_NUMBER() OVER (PARTITION BY et.freight_id ORDER BY et.event_date) AS "Sequência dos eventos"
  FROM events_timeline et
  JOIN freights f ON f.id = et.freight_id
  WHERE f.created_at >= '2024-01-01'
) AS virtual_table
ORDER BY "Id contrato", "Sequência dos eventos", "Data do evento";






