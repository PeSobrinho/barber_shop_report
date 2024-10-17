--drop table barber_shop.staging.stg_barbearia;


create table barber_shop.staging.stg_barbearia (
	id int generated always as identity,
	dat_comp date,
	dat_servico timestamp,
	id_origem int,
	id_origem_cliente int,
	nm_cliente varchar,
	tp_servico varchar,
	vl_servico numeric(10,2),
	tp_pagamento varchar,
	id_origem_funcionario int,
	nm_funcionario varchar,
	av_servico int,
	av_comentario varchar,
	dat_carga timestamp
);

--select * from barber_shop.staging.stg_barbearia;