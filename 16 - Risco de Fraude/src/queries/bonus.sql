with bonus as (
select
dcb.updated_at,
dcb.price / 100 as value,
dcb.contract_id as contract_id
from driver_contract_bonuses dcb 
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
select c.*,
bonus.updated_at,
bonus.value
 from bonus
left join contract c on c.contract_id = bonus.contract_id