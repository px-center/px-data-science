-- Visitou
SELECT 
    dfh.freight_id AS contract_id,
    dfh.driver_id,
    f.company_id,
    dfh.created_at,
    'visitou' AS action,
    'driver_freight_history' AS origem
FROM driver_freight_history dfh
JOIN freights f 
  ON dfh.freight_id = f.id AND dfh.driver_id = f.driver_id
WHERE dfh.count_visit <> 0 
  AND dfh.created_at >= '2024-01-01'

UNION ALL

-- Candidatou
SELECT 
    dfh.freight_id AS contract_id,
    dfh.driver_id,
    f.company_id,
    dfh.created_at,
    'candidatou' AS action,
    'driver_freight_history' AS origem
FROM driver_freight_history dfh
JOIN freights f 
  ON dfh.freight_id = f.id AND dfh.driver_id = f.driver_id
WHERE dfh.candidate_at IS NOT NULL 
  AND dfh.created_at >= '2024-01-01'

UNION ALL

-- Like
SELECT 
    freight_id AS contract_id, 
    driver_id, 
    company_id, 
    created_at, 
    'Like' AS action,
    'company_ratings' AS origem
FROM company_ratings cr  
WHERE rating = 5 
  AND freight_id IS NOT NULL 
  AND created_at >= '2024-01-01'

UNION ALL

-- Dislike
SELECT 
    freight_id AS contract_id, 
    driver_id, 
    company_id, 
    created_at, 
    'dislike' AS action,
    'company_ratings' AS origem
FROM company_ratings cr  
WHERE rating < 4 
  AND freight_id IS NOT NULL 
  AND created_at >= '2024-01-01'
ORDER BY contract_id, created_at, driver_id;

select * driver_behavior_occurrence_type() from driver_behavior_occurrence dbo 


