create or replace procedure barber_shop.dw.carga_fact_servicos_barbearia()
language plpgsql
as $$
begin
truncate table barber_shop.dw.fact_servicos_barbearia restart identity;

insert into barber_shop.dw.fact_servicos_barbearia (
	dat_comp,
	dat_servico,
	sk_cliente,
	sk_servico,
	vl_servico,
	sk_pagamento,
	sk_funcionario,
	av_servico,
	av_comentario
)
select 
	sb.dat_comp,
	sb.dat_servico,
	dc.sk_cliente,
	ds.sk_servico,
	sb.vl_servico,
	dp.sk_pagamento,
	df.sk_funcionario,
	sb.av_servico,
	sb.av_comentario 
from barber_shop.staging.stg_barbearia sb 
	left join barber_shop.dw.dim_cliente dc on dc.id_origem_cliente = sb.id_origem_cliente 
	left join barber_shop.dw.dim_servico ds on ds.tp_servico = sb.tp_servico
	left join barber_shop.dw.dim_pagamento dp on dp.tp_pagamento = sb.tp_pagamento
	left join barber_shop.dw.dim_funcionario df on df.id_origem_funcionario = sb.id_origem_funcionario;
end; $$

--call barber_shop.dw.carga_fact_servicos_barbearia()
