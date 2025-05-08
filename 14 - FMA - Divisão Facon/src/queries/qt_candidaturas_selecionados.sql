SELECT
  freight_id,
  COUNT(*) FILTER (WHERE key = 'status' AND new_value::int = 100) AS qt_candidaturas,
  COUNT(*) FILTER (WHERE key = 'status' AND new_value::int = 200) AS qt_selecionados,
  CASE 
    WHEN COUNT(*) FILTER (WHERE key = 'status' AND new_value::int = 200) = 0 THEN 'nao'
    ELSE 'sim'
  END AS houve_selecionado
FROM freight_histories
GROUP BY freight_id;