select
f.id as freight_id,
fh.created_at as canceled_at,
f.start_at as start_at,
f.created_at as created_at
from freights f
join freight_histories fh on fh.freight_id = f.id and key = 'status' and fh.new_value = '900'
where f.reason = 1 and f.status = 900