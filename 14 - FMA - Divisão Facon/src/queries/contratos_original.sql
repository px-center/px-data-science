SELECT 
		f.id AS freight_id,
        public.freights_type(f.type) AS de_type,
        public.freights_status(f.status) AS de_status,
        f.start_at,
        f.contract_days,
        f.company_id,
        f.driver_id,
        ct.name as city,
        s.uf
    FROM freights f
    LEFT JOIN (
        SELECT DISTINCT freight_id
        FROM user_working_freights
    ) uwf ON uwf.freight_id = f.id
    LEFT JOIN companies c ON c.id = f.company_id
    LEFT JOIN company_addresses ca ON ca.id = f.origin
    LEFT JOIN public.states s ON ca.state_id = s.id
    LEFT JOIN public.cities ct ON ca.city_id = ct.id
    WHERE f.start_at >= '2025-01-01' and f.end_at < now()
    ORDER BY f.start_at ASC;

