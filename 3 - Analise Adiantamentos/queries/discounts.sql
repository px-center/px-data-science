select 
f.id as freight_id,
f.price / 100 as value,
coalesce (d.value / 100, 0) as discount,
pa.amount / 100 as adiantamento
from freights f 
left join discounts d on d.freight_id = f.id
left join freights_payment_orders pa on pa.freight_id = f.id
where freight_payment_orders_status(pa.status) = 'Pago'
