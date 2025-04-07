select
d.id as driver_id,
s.name
from drivers d 
join driver_addresses da on da.driver_id = d.id
join states s on s.id = da.state_id 
