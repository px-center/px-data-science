WITH meses AS (
  SELECT
    generate_series(
      date_trunc('month', current_date) - INTERVAL '11 months',
      date_trunc('month', current_date),
      INTERVAL '1 month'
    ) AS mes
),
advances AS (
  SELECT
    date_trunc('month', created_at) AS mes,
    COUNT(*) AS cnt
  FROM payment_advances
  WHERE created_at >= date_trunc('month', current_date) - INTERVAL '11 months'
  GROUP BY mes
),
allowance AS (
  SELECT
    date_trunc('month', created_at) AS mes,
    COUNT(*) AS cnt
  FROM financial_allowance
  WHERE created_at >= date_trunc('month', current_date) - INTERVAL '11 months'
  GROUP BY mes
),
reimb AS (
  SELECT
    date_trunc('month', created_at) AS mes,
    COUNT(*) AS cnt
  FROM reimbursements
  WHERE created_at >= date_trunc('month', current_date) - INTERVAL '11 months'
  GROUP BY mes
),
credits AS (
  SELECT
    date_trunc('month', created_at) AS mes,
    COUNT(*) AS cnt
  FROM financial_orders
  WHERE created_at >= date_trunc('month', current_date) - INTERVAL '11 months'
  GROUP BY mes
)
SELECT
  to_char(m.mes, 'YYYY-MM')           AS mes,
  COALESCE(a.cnt, 0)                  AS qtde_adiantamentos,
  COALESCE(f.cnt, 0)                  AS qtde_ajudas_de_custo,
  COALESCE(r.cnt, 0)                  AS qtde_reembolsos,
  COALESCE(c.cnt, 0)                  AS qtde_creditos,
  (COALESCE(a.cnt, 0)
   + COALESCE(f.cnt, 0)
   + COALESCE(r.cnt, 0)
   + COALESCE(c.cnt, 0))              AS total_transacoes_mes
FROM meses m
LEFT JOIN advances a   ON a.mes = m.mes
LEFT JOIN allowance f  ON f.mes = m.mes
LEFT JOIN reimb r      ON r.mes = m.mes
LEFT JOIN credits c    ON c.mes = m.mes
ORDER BY m.mes;
