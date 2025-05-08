SELECT DATE_TRUNC('week', "Data do evento") AS "Data do evento",
       case "Tipo do evento"
           when 'canceled_by_company_multilevel' then 'Cancelados pelo cliente'
           when 'canceled_by_user' then 'Cancelados internamente'
           when 'changed' then 'Contratos alterados'
           when 'expired' then 'Contratos expirados'
           when 'postponed' then 'Contratos postergados'
           when 'success' then 'Contratos atendidos'
           when 'created' then 'Contrato criado'
       end AS event_name,
       COUNT(DISTINCT ("Id contrato", "Sequência dos eventos")) AS "COUNT(DISTINCT (""Id contrato"", ""Sequência dos eventos""))"
FROM
  (with events_timeline as
     (select freight_id,
             case
                 when ft.event_name = 'freight_change' then 'changed'
                 when ft.event_name = 'start_at_change' then 'postponed'
                 when ft.event_name = 'freight_created' then 'created'
                 when ft.event_name = 'canceled'
                      and (user_type is null
                           or user_type = 'App\Models\User') then 'canceled_by_user'
                 when ft.event_name = 'canceled'
                      and user_type = 'App\Models\CompanyMultilevel' then 'canceled_by_company_multilevel'
                 else event_name
             end as event_name,
             ft.event_date
      from freight_timeline ft
      where ft.event_name in ('freight_created',
                              'freight_change',
                              'canceled',
                              'start_at_change')
      union all select ft.freight_id,
                       'expired' as event_name,
                       ft.event_date
      from freight_timeline ft
      left join freight_timeline ft2 on ft2.freight_id = ft.freight_id
      and ft2.event_date <= ft.event_date
      and ft2.event_name in ('has_driver',
                             'canceled',
                             'removed_driver')
      where ft.event_date < now()
        and ft.event_name = 'freight_start_at'
      group by ft.freight_id,
               ft.event_date,
               ft.event_name
      having regexp_replace(replace(array_to_string(array_agg(ft2.event_name
                                                              order by ft2.event_date, ft2.priority), ','), 'has_driver,removed_driver', ''), ',+', ',') in (',',
                                                                                                                                                             '')
      union all select ft.freight_id,
                       'success' as event_name,
                       ft.event_date
      from freight_timeline ft
      left join freight_timeline ft2 on ft2.freight_id = ft.freight_id
      and ft2.event_date < ft.event_date
      and ft2.event_name in ('check_insurance',
                             'removed_driver')
      where ft.event_date < now()
        and ft.event_name = 'check_insurance'
      group by ft.freight_id,
               ft2.freight_id,
               ft.event_date,
               ft.event_name
      having (ft2.freight_id is null
              or array_to_string(array_agg(ft2.event_name
                                           order by ft2.event_date, ft2.priority), ',') like '%removed_driver')) select et.freight_id "Id contrato",
                                                                                                                        et.event_name "Tipo do evento",
                                                                                                                        et.event_date "Data do evento",
                                                                                                                        date_trunc('month', et.event_date) "Mês",
                                                                                                                        f.created_at "Contrato criado",
                                                                                                                        c.id "Id cliente",
                                                                                                                        c.name "Cliente",
                                                                                                                        c.company_multitenancy_id "Id cliente master",
                                                                                                                        cm.name "Cliente master",
                                                                                                                        ceg.name "Grupo econômico",
                                                                                                                        freights_type(f."type")"Tipo de contrato",
                                                                                                                        rank()over(partition by (et.event_name, et.freight_id)
                                                                                                                                   order by date_trunc('day', et.event_date)) "Sequência dos eventos"
   from events_timeline et
   join freights f on f.id = et.freight_id
   join companies c on c.id = f.company_id
   left join company_multitenancy cm on cm.id = c.company_multitenancy_id
   left join company_economic_groups ceg on ceg.id = c.company_economic_group_id
   where f.created_at >= '2023-01-01') AS virtual_table
WHERE "Mês" IN (TO_TIMESTAMP('2025-04-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US'))
GROUP BY DATE_TRUNC('week', "Data do evento"),
         case "Tipo do evento"
             when 'canceled_by_company_multilevel' then 'Cancelados pelo cliente'
             when 'canceled_by_user' then 'Cancelados internamente'
             when 'changed' then 'Contratos alterados'
             when 'expired' then 'Contratos expirados'
             when 'postponed' then 'Contratos postergados'
             when 'success' then 'Contratos atendidos'
             when 'created' then 'Contrato criado'
         end
ORDER BY "COUNT(DISTINCT (""Id contrato"", ""Sequência dos eventos""))" DESC
LIMIT 10000;