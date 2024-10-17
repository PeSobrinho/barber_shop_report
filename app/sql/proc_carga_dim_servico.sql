create or replace procedure barber_shop.dw.carga_dim_servico()
language plpgsql
as $$
begin

-- Inserindo novos serviços
insert into barber_shop.dw.dim_servico (tp_servico)
select distinct 
	tp_servico
from barber_shop.staging.stg_barbearia sb
where tp_servico not in (select distinct tp_servico from barber_shop.dw.dim_servico)
order by tp_servico;

--select * from barber_shop.dw.dim_servico;

end; $$

-- call barber_shop.dw.carga_dim_servico();