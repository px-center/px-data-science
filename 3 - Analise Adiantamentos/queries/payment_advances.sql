select 
pa.created_at,
pa.driver_id,
pa.amount / 100 as value_advance,
f.price / 100 as value,
f.id as freight_id,
d.name,
d.cnh_category,
EXTRACT(YEAR FROM age(now(), d.birthday)) AS age,
d.marital_status,
s.name as state,
c.name as city,
tpx.px_time as px_time,
ds.level_px
from freights_payment_orders pa left join drivers d on d.id = pa.driver_id
left join driver_addresses da on da.driver_id = pa.driver_id and da.type = 0
left join cities c on c.id = da.city_id
left join states s on s.id = da.state_id
left join freights f on f.id = pa.freight_id
left join 
(
SELECT 
  driver_id, 
  (EXTRACT(YEAR FROM age(now(), MIN(f.created_at))) * 12 +
   EXTRACT(MONTH FROM age(now(), MIN(f.created_at)))) AS px_time
FROM freights f
GROUP BY f.driver_id
) as tpx on tpx.driver_id = pa.driver_id
left join
(
select ds.driver_id, 
driver_scores_group(ds."group") as level_px from
driver_scores ds 
) as ds on ds.driver_id = pa.driver_id
where pa.type = 1
and freight_payment_orders_status(pa.status) = 'Pago'
order by created_at desc


