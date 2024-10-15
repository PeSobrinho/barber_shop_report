import streamlit as st
import pandas as pd
import os
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import config

# Connection configuration
user = config.user
password = config.password
host = config.host
port = config.port
database = config.database
ssl_cert= config.ssl_cert
schema = config.schema

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=verify-full&sslrootcert={ssl_cert}')

# Data queries
queries_paths = [
    '../sql/select_distinct_funcionarios.sql', 
    '../sql/select_distinct_clientes.sql',
    '../sql/select_distinct_pagamento.sql',
    '../sql/select_distinct_servico.sql',
    '../sql/select_distinct_dat_servico.sql'
    ]

data_frames = {}

for path in queries_paths:

    df_name = os.path.splitext(os.path.basename(path))[0]

    with open(path, 'r') as file:
        query = file.read()
    
    data_frames[df_name] = pd.read_sql(query, engine)

## Filters dataframes
df_funcionarios = data_frames['select_distinct_funcionarios']
df_servico = data_frames['select_distinct_servico']
df_pagamento = data_frames['select_distinct_pagamento']
df_cliente = data_frames['select_distinct_clientes']

df_dat_servico = data_frames['select_distinct_dat_servico']
df_dat_servico['dat_servico'] = pd.to_datetime(df_dat_servico['dat_servico'])
min_date = df_dat_servico['dat_servico'].min().date()
max_date = df_dat_servico['dat_servico'].max().date()

## Data dataframes

#teste

query_teste = '''
select 
	fsb.dat_comp,
	dc.nm_cliente,
	df.nm_funcionario,
	dp.tp_pagamento,
	ds.tp_servico 
from barber_shop.dw.fact_servicos_barbearia fsb 
	join barber_shop.dw.dim_cliente dc on fsb.sk_cliente = dc.sk_cliente 
	join barber_shop.dw.dim_funcionario df on df.sk_funcionario = fsb.sk_funcionario 
	join barber_shop.dw.dim_pagamento dp on dp.sk_pagamento = fsb.sk_pagamento 
	join barber_shop.dw.dim_servico ds on ds.sk_servico = fsb.sk_servico 
'''

df_teste = pd.read_sql(query_teste, engine)
df_teste['dat_comp'] = pd.to_datetime(df_teste['dat_comp'])
#Fim teste


# Dashboard
st.set_page_config(layout='wide')


with st.sidebar:
    st.title('Filtros')
    periodo_selecionado = st.date_input('Período: ', [min_date, max_date], min_value = min_date, max_value = max_date)
    funcionarios_selecionados = st.multiselect('Funcionários: ', df_funcionarios['nm_funcionario'])
    servicos_selecionados = st.multiselect('Servicos: ', df_servico['tp_servico'])
    pagamentos_selecionados = st.multiselect('Formas de pagamento: ', df_pagamento['tp_pagamento'])
    clientes_selecionados = st.multiselect('Clientes: ', df_cliente['nm_cliente'])

filtered_df = df_teste.copy()

if len(periodo_selecionado) == 2:
    start_date, end_date = periodo_selecionado
    filtered_df = filtered_df[(filtered_df['dat_comp'].dt.date >= start_date) & 
                              (filtered_df['dat_comp'].dt.date <= end_date)]

if funcionarios_selecionados:
    filtered_df = filtered_df[filtered_df['nm_funcionario'].isin(funcionarios_selecionados)]

if servicos_selecionados:
    filtered_df = filtered_df[filtered_df['tp_servico'].isin(servicos_selecionados)]

if pagamentos_selecionados:
    filtered_df = filtered_df[filtered_df['tp_pagamento'].isin(pagamentos_selecionados)]

if clientes_selecionados:
    filtered_df = filtered_df[filtered_df['nm_cliente'].isin(clientes_selecionados)]

# Display the filtered DataFrame
st.write(filtered_df)

