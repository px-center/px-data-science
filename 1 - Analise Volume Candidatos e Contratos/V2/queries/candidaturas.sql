select dfh.candidate_at, 
dfh.driver_id,
c."name" as city,
s."name" as state,
freights_type(f.type),
f.contract_days,
coalesce(v.name, 'Não Informado') as vehicle,
coalesce(s2."name", 'Não Informado')  as supply
from driver_freight_history dfh
left join freights f on f.id  = dfh.freight_id 
left join company_addresses ca on ca.id = f.origin
left join cities c on ca.city_id = c.id
left join states s on ca.state_id = s.id 
left join vehicles v on f.vehicle_id = v.id
left join supplies s2 on f.supply_id = s2.id
where candidate_at is not null