create or replace procedure barber_shop.dw.carga_dim_pagamento()
language plpgsql
as $$
begin
-- Inserindo novas formas de pagamento
insert into barber_shop.dw.dim_pagamento (tp_pagamento)
select distinct 
	tp_pagamento
from barber_shop.staging.stg_barbearia sb
where tp_pagamento not in (select distinct tp_pagamento from barber_shop.dw.dim_pagamento)
order by tp_pagamento;

--select * from barber_shop.dw.dim_pagamento;

end; $$

-- call barber_shop.dw.carga_dim_pagamento()
