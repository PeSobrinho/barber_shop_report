-- dimensões

-- dim_cliente
create table barber_shop.dw.dim_cliente(
	sk_cliente int generated always as identity,
	nm_cliente varchar,
	id_origem_cliente int	
);

-- dim_servico
create table barber_shop.dw.dim_servico(
	sk_servico int generated always as identity,
	tp_servico varchar	
);

-- dim_pagamento
create table barber_shop.dw.dim_pagamento(
	sk_pagamento int generated always as identity,
	tp_pagamento varchar
);

-- dim_funcionario
create table barber_shop.dw.dim_funcionario(
	sk_funcionario int generated always as identity,
	nm_funcionario varchar,
	id_origem_funcionario int
);

--fato
create table barber_shop.dw.fact_servicos_barbearia (
	fact_servicos_barbearia_id int generated always as identity,
	dat_comp date,
	dat_servico timestamp,
	sk_cliente int,
	sk_servico int,
	vl_servico numeric(10,2),
	sk_pagamento int,
	sk_funcionario int,
	av_servico int,
	av_comentario varchar
);