SELECT
  table_schema,
  table_name,
  string_agg(
    column_name
    || ' ' || data_type
    || COALESCE('('||character_maximum_length||')','')
    || CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
    ', ' ORDER BY ordinal_position
  ) AS columns_summary
FROM information_schema.columns
WHERE table_schema NOT IN ('information_schema','pg_catalog')
GROUP BY table_schema, table_name
ORDER BY table_schema, table_name;

