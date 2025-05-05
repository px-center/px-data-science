with coordenadas as (
select vr.id as id_checklist,
       f.id as id_contrato,
       d.name as nome_motorista,
       vr.latitude as latitude_checklist,
       vr.longitude as longitude_checklist,
       ca.latitude as latitude_endereco_origem,
       ca.longitude as longitude_endereco_origem,
       da.latitude as latitude_residencia,
       da.longitude as longitude_residencia,
       ROUND((6371 * acos(cos(radians(vr.latitude)) * cos(radians(ca.latitude)) * cos(radians(ca.longitude) - radians(vr.longitude)) + sin(radians(vr.latitude)) * sin(radians(ca.latitude))))) AS distancia_km_contrato,
       ROUND((6371 * acos(cos(radians(vr.latitude)) * cos(radians(da.latitude)) * cos(radians(da.longitude) - radians(vr.longitude)) + sin(radians(vr.latitude)) * sin(radians(da.latitude))))) AS distancia_km_residencia
FROM vehicle_reviews vr
JOIN freights f ON f.id = vr.freight_id
JOIN company_addresses ca on f.origin = ca.id
JOIN drivers d on d.id = f.driver_id
JOIN driver_addresses da on da.driver_id = d.id
and da.type = 0
order by f.id asc
),
checklist as (
select
id,
updated_at,
plate,
driver_id as driver_id,
freight_id as contract_id,
vr."type"
from vehicle_reviews vr 
where vr."type" = 1 --Inicial
or vr."type" = 2 --Final
order by freight_id 
),
contract as (
select
f.id as contract_id,
f.contract_days as contract_days,
f.price/100 as price,
f.day_of_week as contract_day_of_week,
d.id as driver_id,
d.name as driver_name,
d.service_supplier as service_supplier,
c.name as company_name
from freights f
left join companies c on c.id = f.company_id
left join drivers d on d.id = f.driver_id 
)
select * from checklist ch
left join contract c on c.contract_id = ch.contract_id
left join coordenadas on coordenadas.id_contrato = ch.contract_id
