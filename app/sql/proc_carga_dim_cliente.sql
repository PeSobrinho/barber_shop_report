create or replace procedure barber_shop.dw.carga_dim_cliente()
language plpgsql
as $$
begin
-- Inserindo novos clientes
insert into barber_shop.dw.dim_cliente (id_origem_cliente, nm_cliente)
select distinct 
	id_origem_cliente, 
	nm_cliente 
from barber_shop.staging.stg_barbearia sb
where id_origem_cliente not in (select distinct id_origem_cliente from barber_shop.dw.dim_cliente)
order by id_origem_cliente;

--select * from barber_shop.dw.dim_cliente;
end; $$

--call barber_shop.dw.carga_dim_cliente()