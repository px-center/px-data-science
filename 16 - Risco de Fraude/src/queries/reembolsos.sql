with reembolso as (
select 
r.id as "ID do Reembolso",
r.created_at as  "Data da criação do reembolso",
r.updated_at as "Data da ultima atualização do reembolso",
r.decided_at as "Data da aprovação ou rejeição do reembolso",
reimbursements_status(r.status) as "Status do reembolso",
r.freight_id as "ID do contrato",
r.amount /100 as "Valor total do reembolso",
coalesce (r.reason, '') as  "Motivo do reembolso",
coalesce (r.reason_description, '') as  "Descrição do motivo do reembolso",
r.type as  "Tipo do reembolso",
coalesce (r.description, '') as "Descrição do reembolso"
from reimbursements r
where r.decided_at is not null
),
contract as (
select
f.id as  "ID do contrato",
f.contract_days as "Número de dias agenciados do contrato",
f.price/100 as "Valor do contrato",
f.day_of_week as "Dia da semana do contrato",
d.id as "ID do motorista",
d.name as "Nome do motorista",
d.service_supplier as "Ajudante (1) ou Motorista (0)",
c.name as "Nome da transportadora"
from freights f
left join companies c on c.id = f.company_id
left join drivers d on d.id = f.driver_id 
)
select * from reembolso r
left join contract c on c."ID do contrato" = r."ID do contrato"