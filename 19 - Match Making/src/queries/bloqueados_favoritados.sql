SELECT
    COALESCE(cfd.driver_id, cdb.driver_id) AS driver_id,
    COALESCE(cfd.company_id, cdb.company_id) AS company_id,
    cfd.created_at AS dt_favorite,
    cdb.created_at AS dt_company_driver_block
FROM company_favorite_drivers cfd
FULL OUTER JOIN company_driver_block cdb
  ON cfd.driver_id = cdb.driver_id
 AND cfd.company_id = cdb.company_id
WHERE cdb.deleted_at IS NULL OR cdb.deleted_at IS NULL;