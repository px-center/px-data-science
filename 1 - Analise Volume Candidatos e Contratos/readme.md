SELECT
  date,
  weight,
  JSON_EXTRACT_SCALAR(data_json, "$.month") AS month,
  JSON_EXTRACT_SCALAR(data_json, "$.day_of_week") AS day_of_week,
  JSON_EXTRACT_SCALAR(data_json, "$.region") AS region,
  JSON_EXTRACT_SCALAR(data_json, "$.state") AS state,
  JSON_EXTRACT_SCALAR(data_json, "$.city") AS city,
  JSON_EXTRACT_SCALAR(data_json, "$.freights_type") AS freights_type,
  JSON_EXTRACT_SCALAR(data_json, "$.vehicle") AS vehicle
FROM  `formal-purpose-354320.datascience.simulated_future_contracts`



SELECT
  date,
  weight,
  JSON_EXTRACT_SCALAR(data_json, "$.month") AS month,
  JSON_EXTRACT_SCALAR(data_json, "$.day_of_week") AS day_of_week,
  JSON_EXTRACT_SCALAR(data_json, "$.region") AS region,
  JSON_EXTRACT_SCALAR(data_json, "$.state") AS state,
  JSON_EXTRACT_SCALAR(data_json, "$.city") AS city,
  JSON_EXTRACT_SCALAR(data_json, "$.freights_type") AS freights_type,
  JSON_EXTRACT_SCALAR(data_json, "$.vehicle") AS vehicle
FROM  `formal-purpose-354320.datascience.simulated_future_candidates
SELECT
  date,
  weight,
  JSON_EXTRACT_SCALAR(data_json, "$.month") AS month,
  JSON_EXTRACT_SCALAR(data_json, "$.day_of_week") AS day_of_week,
  JSON_EXTRACT_SCALAR(data_json, "$.region") AS region,
  JSON_EXTRACT_SCALAR(data_json, "$.state") AS state,
  JSON_EXTRACT_SCALAR(data_json, "$.city") AS city,
  JSON_EXTRACT_SCALAR(data_json, "$.freights_type") AS freights_type,
  JSON_EXTRACT_SCALAR(data_json, "$.vehicle") AS vehicle
FROM  `formal-purpose-354320.datascience.simulated_future_contracts`



SELECT
  date,
  weight,
  JSON_EXTRACT_SCALAR(data_json, "$.month") AS month,
  JSON_EXTRACT_SCALAR(data_json, "$.day_of_week") AS day_of_week,
  JSON_EXTRACT_SCALAR(data_json, "$.region") AS region,
  JSON_EXTRACT_SCALAR(data_json, "$.state") AS state,
  JSON_EXTRACT_SCALAR(data_json, "$.city") AS city,
  JSON_EXTRACT_SCALAR(data_json, "$.freights_type") AS freights_type,
  JSON_EXTRACT_SCALAR(data_json, "$.vehicle") AS vehicle
FROM  `formal-purpose-354320.datascience.simulated_future_candidates
