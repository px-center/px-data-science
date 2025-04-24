WITH adiamentos AS (
    SELECT 
        f.created_at,
        fh.id AS id_adiamento,
        fh.created_at as dt_alteracao,
        fh.freight_id, 
        fh.old_value::timestamp AS old_value_start,
        fh.new_value::timestamp AS new_value_start,
        EXTRACT(EPOCH FROM (fh.new_value::timestamp - fh.old_value::timestamp)) / 3600 AS horas_adicionadas,
        freights_type(f.type) AS tipo,
        f.driver_id,
        CASE 
            WHEN f.status = '300' THEN 'Sim'
            ELSE 'Não'
        END AS concluido
    FROM freight_histories fh
    LEFT JOIN freights f ON f.id = fh.freight_id
    WHERE fh.key = 'start_at'
      AND fh.old_value::timestamp < fh.new_value::timestamp
),

candidaturas_por_adiamento AS (
    SELECT 
        a.id_adiamento,
        COUNT(*) AS qt_candidaturas_antes_adiamento
    FROM adiamentos a
    JOIN freight_histories fh ON fh.freight_id = a.freight_id
    WHERE fh.key = 'status'
      AND fh.new_value = '100'
      AND fh.created_at::timestamp < a.old_value_start
    GROUP BY a.id_adiamento
),

selecoes_por_adiamento AS (
    SELECT 
        a.id_adiamento,
        COUNT(*) AS qt_selecionados_antes_adiamento
    FROM adiamentos a
    JOIN freight_histories fh ON fh.freight_id = a.freight_id
    WHERE fh.key = 'status'
      AND fh.new_value = '200'
      AND fh.created_at::timestamp < a.old_value_start
    GROUP BY a.id_adiamento
)

SELECT 
    a.*,
    COALESCE(c.qt_candidaturas_antes_adiamento, 0) AS qt_candidaturas_antes_adiamento,
    COALESCE(s.qt_selecionados_antes_adiamento, 0) AS qt_selecionados_antes_adiamento
FROM adiamentos a
LEFT JOIN candidaturas_por_adiamento c ON a.id_adiamento = c.id_adiamento
LEFT JOIN selecoes_por_adiamento s     ON a.id_adiamento = s.id_adiamento;

