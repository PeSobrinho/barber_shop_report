create or replace procedure barber_shop.dw.carga_dim_funcionario()
language plpgsql
as $$
begin
-- Inserindo novos funcionarios
insert into barber_shop.dw.dim_funcionario (id_origem_funcionario , nm_funcionario)
select distinct 
	id_origem_funcionario , 
	nm_funcionario 
from barber_shop.staging.stg_barbearia sb
where id_origem_funcionario not in (select distinct id_origem_funcionario from barber_shop.dw.dim_funcionario)
order by id_origem_funcionario;

--select * from barber_shop.dw.dim_funcionario;

end; $$

--call barber_shop.dw.carga_dim_funcionario()

