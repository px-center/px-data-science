select 
f.created_at as created_at, 
f.company_id,
f.id as contract_id,
c."name" as city,
s."name" as state,
freights_type(f.type),
f.contract_days,
f.price / 100 as contract_value,
coalesce(v.name, 'Não Informado') as vehicle,
coalesce(s2."name", 'Não Informado')  as supply
from 
freights f 
left join company_addresses ca on ca.id = f.origin
left join cities c on ca.city_id = c.id
left join states s on ca.state_id = s.id 
left join vehicles v on f.vehicle_id = v.id
left join supplies s2 on f.supply_id = s2.id
-- where f.created_at >= now() - interval '1 year'
