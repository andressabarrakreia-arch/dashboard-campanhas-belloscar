import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Painel de Leads - Belloscar", layout="wide")
st.title("🚗 Painel de Análise de Leads - Belloscar")

# NOME EXATO DO ARQUIVO QUE VOCÊ SUBIU NO GITHUB
# Se a sua planilha for CSV, mude para 'leads.csv'
NOME_ARQUIVO = 'leads.xlsx'

try:
    # Lê o arquivo automaticamente
    if NOME_ARQUIVO.endswith('.csv'):
        df = pd.read_csv(NOME_ARQUIVO)
    else:
        df = pd.read_excel(NOME_ARQUIVO)
        
    # Padroniza o nome das colunas para evitar erros de digitação
    df.columns = df.columns.str.lower().str.strip()

    # Converte a coluna de data
    df['data do lead'] = pd.to_datetime(df['data do lead'], errors='coerce')

    # Filtros na barra lateral
    st.sidebar.header("Filtros")
    data_min = df['data do lead'].min().date()
    data_max = df['data do lead'].max().date()
    
    data_inicio = st.sidebar.date_input("Data Início", data_min)
    data_fim = st.sidebar.date_input("Data Fim", data_max)

    # Aplica o filtro de data
    mask = (df['data do lead'].dt.date >= data_inicio) & (df['data do lead'].dt.date <= data_fim)
    df_filtrado = df.loc[mask]

    # Padroniza textos para contagem
    df_filtrado['visita'] = df_filtrado['visita'].astype(str).str.lower().str.strip()
    df_filtrado['status'] = df_filtrado['status'].astype(str).str.lower().str.strip()

    # Métricas Principais (KPIs)
    total_leads = len(df_filtrado)
    visitas_realizadas = len(df_filtrado[df_filtrado['visita'] == 'sim'])
    vendas_sucesso = len(df_filtrado[df_filtrado['status'] == 'sucesso'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Leads", total_leads)
    col2.metric("Visitas (Sim)", visitas_realizadas)
    col3.metric("Vendas (Sucesso)", vendas_sucesso)
    
    st.divider()

    # Gráfico 1: Leads por Origem
    st.subheader("📊 Volume de Leads por Origem")
    leads_origem = df_filtrado['origem'].value_counts().reset_index()
    leads_origem.columns = ['Origem', 'Quantidade']
    fig_origem = px.bar(leads_origem, x='Origem', y='Quantidade', color='Origem', text='Quantidade')
    st.plotly_chart(fig_origem, use_container_width=True)

    st.divider()

    # Tabela e Gráfico 2: Conversão por Canal
    st.subheader("📈 Conversão por Canal")
    
    # Agrupamento para calcular conversão
    conversao = df_filtrado.groupby('origem').agg(
        Total_Leads=('origem', 'count'),
        Visitas=('visita', lambda x: (x == 'sim').sum()),
        Sucessos=('status', lambda x: (x == 'sucesso').sum())
    ).reset_index()

    # Cálculo das porcentagens
    conversao['Taxa Visita (%)'] = ((conversao['Visitas'] / conversao['Total_Leads']) * 100).round(1)
    conversao['Taxa Sucesso (%)'] = ((conversao['Sucessos'] / conversao['Total_Leads']) * 100).round(1)

    # Mostra a tabela de conversão
    st.dataframe(conversao, use_container_width=True)

    # Gráfico de barras agrupadas
    fig_conv = px.bar(
        conversao, 
        x='origem', 
        y=['Taxa Visita (%)', 'Taxa Sucesso (%)'], 
        barmode='group',
        title="Comparativo de Taxa de Conversão por Origem"
    )
    st.plotly_chart(fig_conv, use_container_width=True)

except FileNotFoundError:
    st.error(f"⚠️ Arquivo '{NOME_ARQUIVO}' não encontrado! Certifique-se de que você subiu a planilha no GitHub com esse exato nome.")
except Exception as e:
    st.error(f"⚠️ Ocorreu um erro ao processar a planilha. Verifique se os nomes das colunas estão corretos: {e}")
