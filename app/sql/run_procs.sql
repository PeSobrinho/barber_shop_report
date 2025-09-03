call barber_shop.staging.carga_stg_barbearia();

call barber_shop.dw.carga_dim_cliente();

call barber_shop.dw.carga_dim_funcionario();

call barber_shop.dw.carga_dim_pagamento();

call barber_shop.dw.carga_dim_servico();

call barber_shop.dw.carga_fact_servicos_barbearia();