SELECT 
    d.phone AS Telefone,
    d.name AS Nome, 
    d.state AS Estado,
    EXTRACT(MONTH FROM AGE(NOW(), MIN(f.start_at))) AS "Tempo de PX (meses)"
FROM drivers d
LEFT JOIN freights f ON d.id = f.driver_id
GROUP BY d.phone, d.name, d.state;
