select 
	fsb.dat_servico,
	fsb.dat_comp,
	dc.nm_cliente,
	df.nm_funcionario,
	dp.tp_pagamento,
	ds.tp_servico,
	sum(fsb.vl_servico) as total_vl_servico,
	count(fsb.fact_servicos_barbearia_id) as total_servicos 
from barber_shop.dw.fact_servicos_barbearia fsb 
	join barber_shop.dw.dim_cliente dc on fsb.sk_cliente = dc.sk_cliente 
	join barber_shop.dw.dim_funcionario df on df.sk_funcionario = fsb.sk_funcionario 
	join barber_shop.dw.dim_pagamento dp on dp.sk_pagamento = fsb.sk_pagamento 
	join barber_shop.dw.dim_servico ds on ds.sk_servico = fsb.sk_servico
group by 
	fsb.dat_servico,
	dc.nm_cliente,
	df.nm_funcionario,
	dp.tp_pagamento,
	ds.tp_servico,
	fsb.dat_comp
order by fsb.dat_servico 