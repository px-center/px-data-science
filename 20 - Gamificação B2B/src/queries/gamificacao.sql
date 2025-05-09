WITH avaliacao_empresa AS (
  SELECT company_id, ROUND(AVG(rating)::numeric, 2) AS score
  FROM company_ratings
  GROUP BY company_id
),
contratos_menos_90_dias AS (
	SELECT company_id,
	       100 * SUM(CASE WHEN contract_days < 90 THEN 1 ELSE 0 END) / COUNT(id) AS porcent_menos_90_dias
	FROM freights
	WHERE true
	-- and created_at >= '2025-01-01'
	-- and company_id = 5
	GROUP BY company_id
),
cancelamentos AS (
  SELECT company_id,
         round(COUNT(*) FILTER (WHERE status = '900') * 100.0 / NULLIF(COUNT(*), 2),2) AS indice_cancelamento
  FROM freights
  GROUP BY company_id
),
sinistralidade AS (
  SELECT c.company_id,
         ROUND(COALESCE(o.total_ocorrencias, 0) * 100.0 / NULLIF(c.total_contratos, 0), 2) AS indice_sinistralidade
  FROM (
    SELECT company_id, COUNT(DISTINCT id) AS total_contratos
    FROM freights
    GROUP BY company_id
  ) c
  LEFT JOIN (
    SELECT company_id, COUNT(DISTINCT id) AS total_ocorrencias
    FROM occurrences
    WHERE status = 9 AND type = 1
    GROUP BY company_id
  ) o ON o.company_id = c.company_id
),
seguro_prime AS (
	SELECT f.company_id,
		   CASE WHEN (SUM(CASE WHEN fis.id IS NOT NULL THEN 1 ELSE 0 END)::numeric / COUNT(f.id)) >= 0.2 THEN 1 ELSE 0 END AS seguro_prime
	FROM freights f
	LEFT JOIN freight_insurance_statements fis ON f.id = fis.freight_id
	-- WHERE f.created_at >= '2025-01-01'
	GROUP BY f.company_id
),
kpi_empresa AS (
  SELECT
    (company_ids ->> 0)::bigint AS company_id,
    BOOL_OR(has_telemetry)::int AS has_telemetry,
    BOOL_OR(has_personalized_content)::int AS has_personalized_content,
    BOOL_OR(has_px_control)::int AS has_px_control,
    BOOL_OR(status = 'Recorrente')::int AS recorrente,
    MAX(created_at) AS data_criacao
  FROM kpi_company
  GROUP BY (company_ids ->> 0)::bigint
  ORDER BY company_id
),
ajudante_motorista AS (
  SELECT
    company_id,
    CASE 
      WHEN COUNT(*) FILTER (WHERE freights_type(f."type") = 'Ajudante') > 0 AND
           COUNT(*) FILTER (WHERE freights_type(f."type") <> 'Ajudante') > 0 THEN 1
      ELSE 0
    END AS ambos_tipos
  FROM freights f
  GROUP BY company_id
),
tempo_medio_selecao AS (
  SELECT 
    f.company_id,
    ROUND(AVG(EXTRACT(EPOCH FROM (fh.created_at - f.created_at)) / 60))::int AS tempo_medio_selecao_min
  FROM freight_histories fh
  LEFT JOIN freights f ON f.id = fh.freight_id
  WHERE fh."key" = 'driver_id'
  GROUP BY f.company_id
)
SELECT
  COALESCE(k.company_id, a.company_id, c.company_id, s.company_id, sp.company_id, am.company_id, t.company_id) AS company_id,
  COALESCE(k.recorrente, 0) AS recorrente,
  COALESCE(k.has_telemetry, 0) AS has_telemetry,
  COALESCE(k.has_personalized_content, 0) AS has_personalized_content,
  COALESCE(k.has_px_control, 0) AS has_px_control,
  COALESCE(a.score, 0) AS score,
  COALESCE(c.porcent_menos_90_dias, 0) AS porcent_menos_90_dias,
  COALESCE(can.indice_cancelamento, 0) AS indice_cancelamento,
  COALESCE(s.indice_sinistralidade, 0) AS indice_sinistralidade,
  COALESCE(sp.seguro_prime, 0) AS seguro_prime,
  COALESCE(am.ambos_tipos, 0) AS ajudante_e_motorista,
  COALESCE(t.tempo_medio_selecao_min, 0) AS tempo_medio_selecao_min
FROM kpi_empresa k
LEFT JOIN avaliacao_empresa a ON a.company_id = (k.company_id)::bigint
LEFT JOIN contratos_menos_90_dias c ON c.company_id = (k.company_id)::bigint
LEFT JOIN cancelamentos can ON can.company_id = (k.company_id)::bigint
LEFT JOIN sinistralidade s ON s.company_id = (k.company_id)::bigint
LEFT JOIN seguro_prime sp ON sp.company_id = (k.company_id)::bigint
LEFT JOIN ajudante_motorista am ON am.company_id = (k.company_id)::bigint
LEFT JOIN tempo_medio_selecao t ON t.company_id = (k.company_id)::bigint