create or replace procedure barber_shop.staging.carga_stg_barbearia()
language plpgsql
as  $$
begin
insert into barber_shop.staging.stg_barbearia (
	dat_comp,
	dat_servico,
	id_origem,
	id_origem_cliente,
	nm_cliente,
	tp_servico,
	vl_servico,
	tp_pagamento,
	id_origem_funcionario,
	nm_funcionario,
	av_servico,
	av_comentario,
	dat_carga
)
select * from (
	with staging_data as (
		select distinct id_origem from barber_shop.staging.stg_barbearia
	)
	select 
		date_trunc('month', "Data_Servico"::date)::date as dat_comp,
		"Data_Servico"::date as dat_servico,
		"ID_Transacao"::int as id_origem,
		"ID_Cliente"::int as id_origem_cliente,
		"Nome_Cliente"::varchar as nm_cliente,
		"Tipo_Servico"::varchar  as tp_servico,
		"Valor_Servico"::numeric(10,2) as vl_servico,
		"Forma_Pagamento"::varchar as tp_pagamento,
		"ID_Funcionario"::int as id_origem_funcionario,
		"Nome_Funcionario"::varchar as nm_funcionario,
		"Avaliacao_Servico"::int as av_servico,
		"Feedback"::varchar as av_comentario,
		now()::timestamp as dat_carga	
	from barber_shop.raw.source_barbearia_dataset sbd 
	where sbd."ID_Transacao" not in (select id_origem from staging_data)
) as insert_data;
end; $$

--call barber_shop.staging.carga_stg_barbearia()
