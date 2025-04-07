select
	f.id "Id contrato",
	f.created_at "Data de criação do contrato",
	ch.created_at "Data de vinculo do analista de sucesso",
	c.id "Id cliente",
	c.name "Cliente",
	c.responsable_name "responsavel",
	c.phone,
	c.qtd_trucks,
	companies_client_status(c.client_status)"Status cliente",
	freights_status(f.status) "Status do contrato",
	c.company_multitenancy_id "Id cliente master",
	smt.name "Time",
	u.id "Id analista",
	u.name "Analista",
	case
		when al.causer_type = 'App\Models\User' then 'Usuario interno'
		when al.causer_type = 'App\Models\CompanyMultilevel' then 'Cliente'
	else 'Desconhecido'
	end,
	u2.id "Id usuario interno",
	u2.name "Usuario interno que criou o contrato"
from freights f
join companies c on c.id = f.company_id
join company_histories ch on ch.company_id = c.id and key = 'analyst_success_id' and old_value is null
left join success_manager_teams smt on smt.success_manager_id = c.success_manager_id
left join users u on u.id = c.analyst_success_id
join activity_log al on al.subject_id = f.id and subject_type = 'App\Models\Freight' and al.description = 'created'
left join users u2 on u2.id = al.causer_id
where f.created_at >= ch.created_at
and f.created_at >= CURRENT_DATE - INTERVAL '1 YEAR'
order by f.created_at desc