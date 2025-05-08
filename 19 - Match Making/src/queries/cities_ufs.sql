SELECT 
    c.id AS city_id,
    c.name AS city,
    c.latitude,
    c.longitude,
    s.uf
FROM cities c
JOIN states s ON c.state_id = s.id;


selec
