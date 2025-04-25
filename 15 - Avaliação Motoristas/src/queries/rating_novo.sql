with notas as (
select 
dr.id,
dr.updated_at,
dr.rating,
f.contract_days,
f.id as contract_id,
dr.driver_id,
coalesce( dr.rating * f.contract_days, 0) as rating_weight
from driver_ratings dr 
left join freights f on f.id = dr.freight_id and f.driver_id = dr.driver_id
where f.updated_at >= CURRENT_DATE - INTERVAL '1 year'
and contract_days > 0
),
nova_nota as (
select 
driver_id,
sum(rating_weight) / sum(contract_days) as rating_weight
from notas
group by driver_id
) 
select
driver_id,
nn.rating_weight,
d.rating  from nova_nota nn
left join drivers d on d.id = nn.driver_id 