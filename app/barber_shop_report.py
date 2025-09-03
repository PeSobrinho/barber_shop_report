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
#ssl_cert= config.ssl_cert
schema = config.schema

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require&channel_binding=require')


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

col_logo, col_title = st.columns([1, 3])

with col_logo:
    st.image("./design/logo.png", width=250)  # Ajuste o caminho e a largura conforme necessário

with col_title:
    st.title('Análise de atendimentos: Barbearia Ponto do Corte')

paginas = ['Visão Geral', 'Avaliações', 'Clientes']

## Filters and navegation
with st.sidebar:

    st.title('Navegação')
    pagina = st.selectbox('Selecione a página: ', paginas)

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

## Métricas e gráficos
def pagina_geral():
    st.title('Visão geral dos atendimentos')

    col0, col00, col000 = st.columns(3)
    col1 = st.columns(1)
    col2, col3, col4 = st.columns(3)
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)

    ### Total de atendimentos
    total_atendimentos = df_agg_vl_qtd_filtred['total_servicos'].sum()
    col0.metric('Total de atendimentos', f'{total_atendimentos:,}')

    ### Total faturado
    total_vl = df_agg_vl_qtd_filtred['total_vl_servico'].sum()
    col00.metric('Total faturado', f'R$ {total_vl:,.2f}')

    ### Ticket médio
    tckt_medio = total_vl/total_atendimentos if total_atendimentos > 0 else 0
    col000.metric('Ticket médio', f'R$ {tckt_medio:,.2f}')

    ### Evolução da total de atendimentos
    df_agg_vl_comp = df_agg_vl_qtd_filtred.groupby('dat_comp')['total_servicos'].sum().reset_index()
    fig_agg_vl_comp = px.line(df_agg_vl_comp, x='dat_comp', y='total_servicos', markers='o')
    fig_agg_vl_comp.update_layout(
        title = 'Evolução da total de atendimentos',
        xaxis_title = 'Competência',
        yaxis_title = 'Atendimentos'
    )
    col1[0].plotly_chart(fig_agg_vl_comp)

    ### Total de atendimentos por mês
    df_agg_vl_mes = df_agg_vl_qtd_filtred.groupby('nome_mes')['total_servicos'].sum().reset_index()
    df_agg_vl_mes['ordem_mes'] = df_agg_vl_mes['nome_mes'].map(ordem_meses_serie)
    df_agg_vl_mes = df_agg_vl_mes.sort_values('ordem_mes')
    fig_agg_vl_mes = px.bar(df_agg_vl_mes, x='nome_mes', y='total_servicos', text='total_servicos')
    fig_agg_vl_mes.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_mes.update_layout(
        title = 'Total de atendimentos por mês',
        xaxis_title = 'Mês',
        yaxis_title = 'Atendimentos'
    )
    col2.plotly_chart(fig_agg_vl_mes)

    ### Total de atendimentos por dia da semana
    df_agg_vl_semana = df_agg_vl_qtd_filtred.groupby('nome_dia_semana')['total_servicos'].sum().reset_index()
    df_agg_vl_semana['ordem_semana'] = df_agg_vl_semana['nome_dia_semana'].map(ordem_dias_semana_serie)
    df_agg_vl_semana = df_agg_vl_semana.sort_values('ordem_semana')
    fig_agg_vl_semana = px.bar(df_agg_vl_semana, x='nome_dia_semana', y='total_servicos', text='total_servicos')
    fig_agg_vl_semana.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_semana.update_layout(
        title = 'Total de atendimentos por dia da semana',
        xaxis_title = 'Dia da semana',
        yaxis_title = 'Atendimentos'
    )
    col3.plotly_chart(fig_agg_vl_semana)

    ### Total de atendimentos por dia do mês
    df_agg_vl_dia = df_agg_vl_qtd_filtred.groupby('dia')['total_servicos'].sum().reset_index()
    df_agg_vl_dia = df_agg_vl_dia.sort_values('dia')
    fig_agg_vl_dia = px.bar(df_agg_vl_dia, x='dia', y='total_servicos', text='total_servicos')
    fig_agg_vl_dia.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_dia.update_layout(
        title = 'Total de atendimentos por dia do mês',
        xaxis_title = 'Dia do mês',
        yaxis_title = 'Atendimentos'
    )
    col4.plotly_chart(fig_agg_vl_dia)

    ### Total de atendimentos por funcionário
    df_agg_vl_func = df_agg_vl_qtd_filtred.groupby('nm_funcionario')['total_servicos'].sum().reset_index()
    fig_agg_vl_funcionario = px.bar(df_agg_vl_func, y='nm_funcionario', x='total_servicos', orientation='h', text='total_servicos')
    fig_agg_vl_funcionario.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_funcionario.update_layout(
        title = 'Total de atendimentos por funcionário',
        yaxis_title = 'Funcionário',
        xaxis_title = 'Atendimentos',
        yaxis = {'categoryorder':'total ascending'}
    )
    col5.plotly_chart(fig_agg_vl_funcionario)

    ### Total de atendimentos por tipo de serviço
    df_agg_vl_serv = df_agg_vl_qtd_filtred.groupby('tp_servico')['total_servicos'].sum().reset_index()
    fig_agg_vl_servico = px.bar(df_agg_vl_serv, y='tp_servico', x='total_servicos', orientation='h', text='total_servicos')
    fig_agg_vl_servico.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_servico.update_layout(
        title = 'Total de atendimentos por tipo de serviço',
        yaxis_title = 'Serviço',
        xaxis_title = 'Atendimentos',
        yaxis = {'categoryorder':'total ascending'}
    )
    col6.plotly_chart(fig_agg_vl_servico)

    ### Total de atendimentos por tipo de pagamento
    df_agg_vl_pg = df_agg_vl_qtd_filtred.groupby('tp_pagamento')['total_servicos'].sum().reset_index()
    fig_agg_vl_pagamento = px.bar(df_agg_vl_pg, y='tp_pagamento', x='total_servicos', orientation='h', text='total_servicos')
    fig_agg_vl_pagamento.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_pagamento.update_layout(
        title = 'Total de atendimentos por tipo de pagamento',
        yaxis_title = 'Pagamento',
        xaxis_title = 'Atendimentos',
        yaxis = {'categoryorder':'total ascending'}
    )
    col7.plotly_chart(fig_agg_vl_pagamento)

    df_agg_vl_cl = df_agg_vl_qtd_filtred.groupby('nm_cliente')['total_servicos'].sum().reset_index()
    df_agg_vl_cl = df_agg_vl_cl.sort_values('total_servicos', ascending = False).head(5)
    fig_agg_vl_cliente = px.bar(df_agg_vl_cl, y='nm_cliente', x='total_servicos', orientation='h', text='total_servicos')
    fig_agg_vl_cliente.update_traces(texttemplate='%{text}', textposition='outside')
    fig_agg_vl_cliente.update_layout(
        title = 'Top 5 clientes mais atendidos',
        yaxis_title = 'Cliente',
        xaxis_title = 'Atendimentos',
        yaxis = {'categoryorder':'total ascending'}
    )
    col8.plotly_chart(fig_agg_vl_cliente)

    # Display the filtered DataFrame
    st.write('Analítico')
    st.write(df_agg_vl_qtd_filtred)
    
def pagina_avaliacoes():
    st.title('Análise de avaliações')

    col0, col00 = st.columns(2)
    col000 = st.columns(1)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    total_avaliacoes = df_agg_vl_qtd_filtred['av_servico'].count()
    col0.metric('Serviços avaliados ', f'{total_avaliacoes:,}')

    media_avaliacoes = df_agg_vl_qtd_filtred['av_servico'].mean()
    col00.metric('Avaliação média dos estabelicimento ', f'{media_avaliacoes:,.2f}')

    df_media_tempo = df_agg_vl_qtd_filtred.groupby('dat_comp')['av_servico'].mean().reset_index()
    fig_media_tempo = px.line(df_media_tempo, x='dat_comp', y='av_servico', markers='o')
    fig_media_tempo.update_layout(
        title = 'Evolução da satisfação',
        xaxis_title = 'Competência',
        yaxis_title = 'Média das avaliações'
    )
    col000[0].plotly_chart(fig_media_tempo)

    df_media_funcionario = df_agg_vl_qtd_filtred.groupby('nm_funcionario')['av_servico'].mean().reset_index()
    fig_media_funcionario = px.bar(df_media_funcionario, y = 'nm_funcionario', x = 'av_servico', orientation= 'h', text = 'av_servico')
    fig_media_funcionario.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_media_funcionario.update_layout(
        title = 'Avaliação média por funcionário',
        yaxis_title = 'Funcionário',
        xaxis_title = 'Média das avaliações',
        yaxis = {'categoryorder':'total ascending'}
    )
    col1.plotly_chart(fig_media_funcionario)

    df_media_servico = df_agg_vl_qtd_filtred.groupby('tp_servico')['av_servico'].mean().reset_index()
    fig_media_servico = px.bar(df_media_servico, y = 'tp_servico', x = 'av_servico', orientation= 'h', text = 'av_servico')
    fig_media_servico.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_media_servico.update_layout(
        title = 'Avaliação média por serviço',
        yaxis_title = 'Serviço',
        xaxis_title = 'Média das avaliações',
        yaxis = {'categoryorder':'total ascending'}
    )
    col2.plotly_chart(fig_media_servico)

    df_media_cliente = df_agg_vl_qtd_filtred.groupby('nm_cliente')['av_servico'].mean().reset_index()
    df_media_cliente = df_media_cliente.sort_values('av_servico', ascending = True).head(5)
    fig_media_cliente = px.bar(df_media_cliente, y = 'nm_cliente', x = 'av_servico', orientation= 'h', text = 'av_servico')
    fig_media_cliente.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_media_cliente.update_layout(
        title = 'Top 5 clientes mais insatisfeitos',
        yaxis_title = 'Cliente',
        xaxis_title = 'Média das avaliações',
        yaxis = {'categoryorder':'total ascending'}
    )
    col3.plotly_chart(fig_media_cliente)

    df_media_cliente2 = df_agg_vl_qtd_filtred.groupby('nm_cliente')['av_servico'].mean().reset_index()
    df_media_cliente2 = df_media_cliente2.sort_values('av_servico', ascending = False).head(5)
    fig_media_cliente2 = px.bar(df_media_cliente2, y = 'nm_cliente', x = 'av_servico', orientation= 'h', text = 'av_servico')
    fig_media_cliente2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_media_cliente2.update_layout(
        title = 'Top 5 clientes mais satisfeitos',
        yaxis_title = 'Cliente',
        xaxis_title = 'Média das avaliações',
        yaxis = {'categoryorder':'total ascending'}
    )
    col4.plotly_chart(fig_media_cliente2)

def pagina_clientes():
    st.title('Análise de clientes')

    col1 = st.columns(1)
    col2 = st.columns(1)
    
    df_cliente_primeiro_mes = df_agg_vl_qtd_filtred.groupby('nm_cliente')['dat_comp'].min().reset_index()
    df_novos_clientes_por_mes = df_cliente_primeiro_mes.groupby('dat_comp')['nm_cliente'].count().reset_index()
    fig_novos_clientes_por_mes = px.line(df_novos_clientes_por_mes, x = 'dat_comp', y = 'nm_cliente', markers='o')
    fig_novos_clientes_por_mes.update_layout(
        title = 'Novos clientes por mês',
        xaxis_title = 'Competência',
        yaxis_title = 'Novos clientes'
    )
    col1[0].plotly_chart(fig_novos_clientes_por_mes)

    # Cohort analysis
    # Passo 1: Identificar o primeiro mês de cada cliente
    df_primeiro_mes = df_agg_vl_qtd_filtred.groupby('nm_cliente')['dat_comp'].min().reset_index()
    df_primeiro_mes.columns = ['nm_cliente', 'primeiro_mes']


    # Passo 2: Mesclar com o dataframe original
    df_cohort = pd.merge(df_agg_vl_qtd_filtred, df_primeiro_mes, on='nm_cliente')

    # Passo 3: Calcular o número de meses desde a primeira visita
    df_cohort['meses_desde_primeira_visita'] = (
        ((pd.to_datetime(df_cohort['dat_comp']) - pd.to_datetime(df_cohort['primeiro_mes'])
          ).dt.days)/30).round(0)
    
    
    # Passo 4: Criar a tabela de cohort
    cohort_table = pd.pivot_table(df_cohort, 
                                 values='nm_cliente', 
                                index='primeiro_mes', 
                               columns='meses_desde_primeira_visita', 
                              aggfunc='count', 
                             fill_value=0)

    # Passo 5: Calcular as taxas de retenção
    cohort_sizes = cohort_table.iloc[:, 0]
    retention_table = cohort_table.divide(cohort_sizes, axis=0)

    # Passo 6: Criar a tabela triangular
    retention_table_styled = retention_table.style.format("{:.2%}")
    retention_table_styled = retention_table_styled.background_gradient(cmap='YlOrRd')

    # Exibir a tabela
    col2[0].write('Retenção de Clientes')
    col2[0].write('Mês de aquisição (linhas) vs. Meses desde a primeira visita (colunas)')
    col2[0].dataframe(retention_table_styled)

    col2[0].write("""
    Esta tabela mostra a taxa de retenção de clientes ao longo do tempo. 
    Cada linha representa um grupo de clientes que fizeram sua primeira visita em um determinado mês. 
    As colunas mostram a porcentagem desses clientes que retornaram nos meses seguintes.
    Por exemplo, um valor de 0.50 na coluna '2' significa que 50% dos clientes daquele grupo retornaram 2 meses após sua primeira visita.
    """)

if pagina == 'Visão Geral':
    pagina_geral()
elif pagina == 'Avaliações':
    pagina_avaliacoes()
elif pagina == 'Clientes':
    pagina_clientes()


