with ocorrencias as (
select
dbo.created_at as occurence_create,
f.start_at as contract_start,
dbo.driver_id,
dbo.contract_id,
dbot.description,
dbo.occurrence_status as observation
from driver_behavior_occurrence dbo
left join driver_behavior_occurrence_types dbots on dbots.driver_behavior_occurrence_id = dbo.id
left join driver_behavior_occurrence_type dbot on dbot.id = dbots.driver_behavior_occurrence_type_id
left join freights f on f.id = dbo.contract_id 
where dbo.occurrence_status = 'finished'
and dbot.description <> 'Pico de velocidade'
AND dbo.created_at >= CURRENT_DATE - INTERVAL '1 year'
order by dbo.driver_id asc, dbo.created_at asc
),
dias_agenciados as (
select 
f.end_at  as occurence_create,
f.start_at  as contract_start,
f.driver_id,
f.id as contract_id,
'Dia agenciado' as description,
cast(f.contract_days * 5  as TEXT) as observation
from freights f
where f.status = 300
AND f.end_at  >= CURRENT_DATE - INTERVAL '1 year'
order by f.driver_id asc, f.start_at  asc
),
resultado as (
select * from ocorrencias
union all
select * from dias_agenciados
)
select * from resultado r
order by r.driver_id asc, r.occurence_create  asc
