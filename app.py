import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def calculate():
    meses = st.session_state['anosfinanciamento'] * 12
    df = pd.DataFrame(index = list(range(meses + 1)))
    df['Ano'] = [0] + [int(i / 12) for i in df.index][:-1]
    valorimovel = st.session_state['valorimovel']
    entrada = st.session_state['entrada']
    financiamento = valorimovel - entrada
    taxa = st.session_state['taxafinanciamento'] / 100
    taxa_mes = ((1 + taxa) ** (1 / 12)) - 1
    depreciacao = st.session_state['depreciacao'] / 100
    depreciacao_mes = ((1 + depreciacao) ** (1 / 12)) - 1
    valorizacao = st.session_state['valorizacao'] / 100
    valorizacao_mes = ((1 + valorizacao) ** (1 / 12)) - 1
    aluguel = st.session_state['aluguel']
    ipca = st.session_state['ipca'] / 100
    selic = st.session_state['taxabase'] / 100
    selic_mes = ((1 + selic) ** (1 / 12)) - 1
    if st.session_state['metodo'] == 'SAC':
        amort = np.array([0] + [financiamento / meses for i in range(meses)])
        saldo_devedor = np.array([financiamento] * (meses + 1)) - amort.cumsum()
        juros = np.array([0] + list(saldo_devedor[:-1] * taxa_mes))
        prestacao = juros + amort
    elif st.session_state['metodo'] == 'PRICE':
        prestacao = [0] + [financiamento * (taxa_mes * ((1 + taxa_mes) ** meses)) / (((1 + taxa_mes) ** meses) - 1)] * meses
        saldo_devedor = [financiamento]
        juros = [0]
        amort = [0]
        for _ in range(meses):
            juros.append(saldo_devedor[-1] * taxa_mes)
            amort.append(prestacao[-1] - juros[-1])
            saldo_devedor.append(saldo_devedor[-1] - amort[-1])
    df['Saldo Devedor'] = saldo_devedor
    df['Prestação'] = prestacao
    df['Juros'] = juros
    df['Amortização'] = amort
    df['Depreciação'] = [0] + [(valorimovel * (((1 + depreciacao_mes) ** i) - 1)) - (valorimovel * (((1 + depreciacao_mes) ** (i - 1)) - 1)) for i in range(1,meses + 1)]
    df['Valorização'] = [0] + [(valorimovel * (((1 + valorizacao_mes) ** i) - 1)) - (valorimovel * (((1 + valorizacao_mes) ** (i - 1)) - 1)) for i in range(1,meses + 1)]
    df['Resultado Imóvel'] = df['Valorização'] - df['Depreciação']
    df['Valor Imóvel'] = df['Resultado Imóvel'].cumsum() + valorimovel
    df['Aluguel'] = [0] + list(aluguel * ((1 + ipca) ** df['Ano']))[1:]
    df['Investimento'] = [entrada * ((1 + selic_mes) ** i) for i in range(meses + 1)]
    df['Juros Investimento'] = df['Investimento'].diff().fillna(0)
    df['Financiamento'] = [financiamento] + ([0] * meses)
    anual_df = df.groupby('Ano').sum()
    st.session_state['dataframe'] = df
    st.session_state['anual_df'] = anual_df

st.title('Simulador Alugar ou Comprar')
st.header('Aruã Viggiano Souza')
if 'dataframe' in st.session_state:
    df = st.session_state['dataframe']
    fig = make_subplots(rows = 2,cols = 1)
    fig.add_trace(go.Scatter(x = df.iloc[1:].index,y = df['Prestação'].iloc[1:],name = 'Prestação'),row = 1,col = 1)
    fig.add_trace(go.Scatter(x = df.iloc[1:].index,y = df['Juros'].iloc[1:],name = 'Juros'),row = 1,col = 1)
    fig.add_trace(go.Scatter(x = df.iloc[1:].index,y = df['Amortização'].iloc[1:],name = 'Amortização'),row = 1,col = 1)
    fig.add_trace(go.Scatter(x = df.iloc[1:].index,y = df['Saldo Devedor'].iloc[1:],name = 'Saldo Devedor'),row = 2,col = 1)
    fig.update_layout(title = 'Financiamento',margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig)
    anual_df = st.session_state['anual_df']
    st.header('Fluxos Anuais')
    fig = go.Figure()
    fig.add_trace(go.Bar(x = anual_df.index,y = anual_df['Financiamento'],name = 'Financiamento'))
    fig.add_trace(go.Bar(x = anual_df.index,y = -anual_df['Prestação'],name = 'Prestação'))
    fig.add_trace(go.Bar(x = anual_df.index,y = anual_df['Valorização'],name = 'Valorização'))
    fig.add_trace(go.Bar(x = anual_df.index,y = -anual_df['Depreciação'],name = 'Depreciação'))
    fig.update_layout(title = 'Comprar',barmode = 'group',margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig)
    fig = go.Figure()
    fig.add_trace(go.Bar(x = anual_df.index,y = -anual_df['Aluguel'],name = 'Aluguel'))
    fig.add_trace(go.Bar(x = anual_df.index,y = anual_df['Juros Investimento'],name = 'Juros Investimento'))
    fig.update_layout(title = 'Alugar',barmode = 'group',margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig)
    st.header('Fluxos Anuais Total')
    fig = go.Figure()
    fig.add_trace(go.Bar(x = anual_df.index,y = anual_df['Financiamento'] - anual_df['Prestação'] + anual_df['Valorização'] - anual_df['Depreciação'],name = 'Comprar'))
    fig.add_trace(go.Bar(x = anual_df.index,y = -anual_df['Aluguel'] + anual_df['Juros Investimento'],name = 'Alugar'))
    fig.update_layout(barmode = 'group',margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig)
    st.header('Fluxos Acumulados')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.index,y = df['Financiamento'].cumsum(),name = 'Financiamento'))
    fig.add_trace(go.Scatter(x = df.index,y = -df['Prestação'].cumsum(),name = 'Prestação'))
    fig.add_trace(go.Scatter(x = df.index,y = df['Valorização'].cumsum(),name = 'Valorização'))
    fig.add_trace(go.Scatter(x = df.index,y = -df['Depreciação'].cumsum(),name = 'Depreciação'))
    fig.update_layout(title = 'Comprar',barmode = 'group',margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.index,y = -df['Aluguel'].cumsum(),name = 'Aluguel'))
    fig.add_trace(go.Scatter(x = df.index,y = df['Juros Investimento'].cumsum(),name = 'Juros Investimento'))
    fig.update_layout(title = 'Alugar',barmode = 'group',margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig)
    st.header('Fluxos Anuais Total')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.index,y = df['Financiamento'].cumsum() - df['Prestação'].cumsum() + df['Valorização'].cumsum() - df['Depreciação'].cumsum(),name = 'Comprar'))
    fig.add_trace(go.Scatter(x = df.index,y = -df['Aluguel'].cumsum() + df['Juros Investimento'].cumsum(),name = 'Alugar'))
    fig.update_layout(barmode = 'group',margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig)

with st.sidebar:
    st.header('Comprar')
    col1,col2 = st.columns(2)
    with col1:
        st.number_input('Valor do Imóvel',min_value = 0.0, value = 1000000.0, step=1000.0, format='%.2f', key='valorimovel')
        st.number_input('Valorização do Imóvel (% a.a.)',min_value = 0.0, value = 5.0, step=.1, format='%.2f', key='valorizacao')
        st.number_input('Anos Financiamento',min_value = 0, value = 5, step=1, key='anosfinanciamento')
    with col2:
        st.number_input('Entrada',min_value = 0.0,max_value = st.session_state['valorimovel'], value = 100000.0, step=1000.0, format='%.2f', key='entrada')
        st.number_input('Depreciação (% a.a.)',min_value = 0.0, value = 4.0, step=.1, format='%.2f', key='depreciacao')
        st.number_input('Taxa Financiamento (% a.a.)',min_value = 0.0, value = 10.0, step=1.0, key='taxafinanciamento')
    st.header('Alugar')
    col1,col2 = st.columns(2)
    with col1:
        st.number_input('Valor do Aluguel',min_value = 0.0, value = 3000.0, step=100.0, format='%.2f', key='aluguel')
    with col2:
        st.radio('Método',options = ['SAC','PRICE'],key = 'metodo')
    st.header('Variáveis Macroeconômicas')
    col1,col2 = st.columns(2)
    with col1:
        st.number_input('Taxa Básica de Juros (% a.a.)',min_value = 0.0, value = 12.5, step=.1, format='%.2f', key='taxabase')
    with col2:
        st.number_input('IPCA Esperado (% a.a.)',min_value = 0.0, value = 5.4, step=.1, format='%.2f', key='ipca')
    st.button('Simular',on_click = calculate)