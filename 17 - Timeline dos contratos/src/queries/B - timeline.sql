select 
f.id,
f.created_at,
ft.event_date,
ft.event_name,
EXTRACT(EPOCH FROM (ft.event_date - f.created_at)) / 3600 AS tempo_decorrido
from freights f
left join freight_timeline ft on ft.freight_id = f.id
where ( event_name = 'freight_created'
or event_name = 'start_at_change'
or event_name = 'canceled'
or event_name = 'has_driver' ) 
and 
f.created_at >= CURRENT_DATE - INTERVAL '365 days'
and freights_type(f."type") = 'Ajudante'
order by f.id desc, event_date desc