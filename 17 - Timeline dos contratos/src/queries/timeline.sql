select 
freight_id,
event_name, 
event_date,
f.created_at as contract_created_at,
f.start_at as contract_stat_at,
freights_type(f."type") as type 
from
freight_timeline ft
left join freights f on f.id = ft.freight_id
where freights_type(f."type") <> 'Viagem'
