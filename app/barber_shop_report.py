import streamlit as st
import pandas as pd
import os
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
import plotly.express as px

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
    './sql/select_distinct_funcionarios.sql', 
    './sql/select_distinct_clientes.sql',
    './sql/select_distinct_pagamento.sql',
    './sql/select_distinct_servico.sql',
    './sql/select_distinct_dat_servico.sql',
    './sql/select_agregacao_vl_qtd.sql'
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
df_agg_vl_qtd = data_frames['select_agregacao_vl_qtd']
df_agg_vl_qtd['dat_servico'] = pd.to_datetime(df_agg_vl_qtd['dat_servico'])
df_agg_vl_qtd['mes-ano'] = df_agg_vl_qtd['dat_servico'].apply(lambda x: str(x.year) + '-' + str(x.month))

df_agg_vl_qtd['nome_mes'] = df_agg_vl_qtd['dat_servico'].dt.strftime('%B')  # Nome do mês
df_agg_vl_qtd['dia'] = df_agg_vl_qtd['dat_servico'].dt.day  # Dia do mês
df_agg_vl_qtd['nome_dia_semana'] = df_agg_vl_qtd['dat_servico'].dt.strftime('%A')  # Nome do dia da semana

meses_pt = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
    'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
    'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
}
dias_pt = {
    'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

df_agg_vl_qtd['nome_mes'] = df_agg_vl_qtd['nome_mes'].map(meses_pt)
df_agg_vl_qtd['nome_dia_semana'] = df_agg_vl_qtd['nome_dia_semana'].map(dias_pt)

ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

ordem_meses_serie = pd.Series(range(len(ordem_meses)), index=ordem_meses)

ordem_dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

ordem_dias_semana_serie = pd.Series(range(len(ordem_dias_semana)), index=ordem_dias_semana)



# Dashboard
st.set_page_config(layout='wide')

col1 = st.columns(1)
col2, col3, col4 = st.columns(3)
col5, col6 = st.columns(2)
col7, col8 = st.columns(2)


## Filters
with st.sidebar:
    st.title('Filtros')
    periodo_selecionado = st.date_input('Período: ', [min_date, max_date], min_value = min_date, max_value = max_date)
    funcionarios_selecionados = st.multiselect('Funcionários: ', df_funcionarios['nm_funcionario'])
    servicos_selecionados = st.multiselect('Servicos: ', df_servico['tp_servico'])
    pagamentos_selecionados = st.multiselect('Formas de pagamento: ', df_pagamento['tp_pagamento'])
    clientes_selecionados = st.multiselect('Clientes: ', df_cliente['nm_cliente'])

df_agg_vl_qtd_filtred = df_agg_vl_qtd.copy()

if len(periodo_selecionado) == 2:
    start_date, end_date = periodo_selecionado
    df_agg_vl_qtd_filtred = df_agg_vl_qtd_filtred[(df_agg_vl_qtd_filtred['dat_servico'].dt.date >= start_date) & 
                              (df_agg_vl_qtd_filtred['dat_servico'].dt.date <= end_date)]

if funcionarios_selecionados:
    df_agg_vl_qtd_filtred = df_agg_vl_qtd_filtred[df_agg_vl_qtd_filtred['nm_funcionario'].isin(funcionarios_selecionados)]

if servicos_selecionados:
    df_agg_vl_qtd_filtred = df_agg_vl_qtd_filtred[df_agg_vl_qtd_filtred['tp_servico'].isin(servicos_selecionados)]

if pagamentos_selecionados:
    df_agg_vl_qtd_filtred = df_agg_vl_qtd_filtred[df_agg_vl_qtd_filtred['tp_pagamento'].isin(pagamentos_selecionados)]

if clientes_selecionados:
    df_agg_vl_qtd_filtred = df_agg_vl_qtd_filtred[df_agg_vl_qtd_filtred['nm_cliente'].isin(clientes_selecionados)]

## Charts agg vl
df_agg_vl_comp = df_agg_vl_qtd_filtred.groupby('dat_comp')['total_vl_servico'].sum().reset_index()
fig_agg_vl_comp = px.line(df_agg_vl_comp, x='dat_comp', y='total_vl_servico', markers='o')
col1[0].plotly_chart(fig_agg_vl_comp)

df_agg_vl_mes = df_agg_vl_qtd_filtred.groupby('nome_mes')['total_vl_servico'].sum().reset_index()
df_agg_vl_mes['ordem_mes'] = df_agg_vl_mes['nome_mes'].map(ordem_meses_serie)
df_agg_vl_mes = df_agg_vl_mes.sort_values('ordem_mes')
fig_agg_vl_mes = px.line(df_agg_vl_mes, x='nome_mes', y='total_vl_servico')
col2.plotly_chart(fig_agg_vl_mes)

df_agg_vl_semana = df_agg_vl_qtd_filtred.groupby('nome_dia_semana')['total_vl_servico'].sum().reset_index()
df_agg_vl_semana['ordem_semana'] = df_agg_vl_semana['nome_dia_semana'].map(ordem_dias_semana_serie)
df_agg_vl_semana = df_agg_vl_semana.sort_values('ordem_semana')
fig_agg_vl_semana = px.line(df_agg_vl_semana, x='nome_dia_semana', y='total_vl_servico')
col3.plotly_chart(fig_agg_vl_semana)

df_agg_vl_dia = df_agg_vl_qtd_filtred.groupby('dia')['total_vl_servico'].sum().reset_index()
df_agg_vl_dia = df_agg_vl_dia.sort_values('dia')
fig_agg_vl_dia = px.line(df_agg_vl_dia, x='dia', y='total_vl_servico')
col4.plotly_chart(fig_agg_vl_dia)

df_agg_vl_func = df_agg_vl_qtd_filtred.groupby('nm_funcionario')['total_vl_servico'].sum().reset_index()
fig_agg_vl_funcionario = px.bar(df_agg_vl_func, y='nm_funcionario', x='total_vl_servico', orientation='h')
fig_agg_vl_funcionario.update_layout(yaxis = {'categoryorder':'total ascending'})
col5.plotly_chart(fig_agg_vl_funcionario)

df_agg_vl_serv = df_agg_vl_qtd_filtred.groupby('tp_servico')['total_vl_servico'].sum().reset_index()
fig_agg_vl_servico = px.bar(df_agg_vl_serv, y='tp_servico', x='total_vl_servico', orientation='h')
fig_agg_vl_servico.update_layout(yaxis = {'categoryorder':'total ascending'})
col6.plotly_chart(fig_agg_vl_servico)

df_agg_vl_pg = df_agg_vl_qtd_filtred.groupby('tp_pagamento')['total_vl_servico'].sum().reset_index()
fig_agg_vl_pagamento = px.bar(df_agg_vl_pg, y='tp_pagamento', x='total_vl_servico', orientation='h')
fig_agg_vl_pagamento.update_layout(yaxis = {'categoryorder':'total ascending'})
col7.plotly_chart(fig_agg_vl_pagamento)

df_agg_vl_cl = df_agg_vl_qtd_filtred.groupby('nm_cliente')['total_vl_servico'].sum().reset_index()
df_agg_vl_cl = df_agg_vl_cl.sort_values('total_vl_servico', ascending = False).head(5)
fig_agg_vl_cliente = px.bar(df_agg_vl_cl, y='nm_cliente', x='total_vl_servico', orientation='h')
fig_agg_vl_cliente.update_layout(yaxis = {'categoryorder':'total ascending'})
col8.plotly_chart(fig_agg_vl_cliente)

# Display the filtered DataFrame
st.write(df_agg_vl_qtd_filtred)
#st.write(fig_agg_vl_funcionario)
#st.write(fig_agg_vl_servico)
#st.write(fig_agg_vl_pagamento)
#st.write(fig_agg_vl_cliente)


