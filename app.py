import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(
    page_title="Dengue Araras - Dashboard",
    page_icon="🦟",
    layout="wide"
)

# 2. Estilização CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #d32f2f;
    }
    h1 { color: #1e3d59; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 3. Carregamento de Dados
@st.cache_data
def carregar_dados():
    df_bairros = pd.read_csv('base_bairros_historico_araras.csv')
    df_mes = pd.read_csv('base_final_araras_completa.csv')
    return df_bairros, df_mes

try:
    df_bairros, df_mes = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar arquivos: {e}")
    st.stop()

# --- CABEÇALHO ---
st.title("🦟 Monitoramento Epidemiológico: Dengue em Araras-SP")
st.markdown(f"**Atividade Extensionista II - Aluno: Bruno Danilo Ribeiro (RU: 5267413)**")

# --- BARRA LATERAL ---
st.sidebar.image("Brasão Araras.png", use_container_width=True)
st.sidebar.title("Painel de Controle")
anos_unicos = sorted(df_bairros['ANO'].unique().tolist(), reverse=True)
opcoes_filtro = ["Todos"] + [int(ano) for ano in anos_unicos]
ano_selecionado = st.sidebar.selectbox("Escolha o Ano para Análise", opcoes_filtro)

if ano_selecionado == "Todos":
    df_filtrado_bairros = df_bairros.copy()
    df_filtrado_mes = df_mes.copy()
    label_tempo = "Série Histórica Completa"
else:
    df_filtrado_bairros = df_bairros[df_bairros['ANO'] == int(ano_selecionado)]
    df_filtrado_mes = df_mes[df_mes['ANO'] == int(ano_selecionado)]
    label_tempo = f"Ano de {ano_selecionado}"

# --- MÉTRICAS ---
total_casos = df_filtrado_bairros['CASOS'].sum()
bairro_agrupado = df_filtrado_bairros.groupby('BAIRRO')['CASOS'].sum().reset_index()
bairro_top = bairro_agrupado.sort_values(by='CASOS', ascending=False).iloc[0]
regiao_foco = df_filtrado_bairros.groupby('REGIAO')['CASOS'].sum().idxmax()

c1, c2, c3 = st.columns(3)
c1.metric("Total de Casos", f"{total_casos}", help=label_tempo)
c2.metric("Bairro mais Afetado", bairro_top['BAIRRO'])
c3.metric("Região de Maior Risco", regiao_foco)

# --- ABAS ---
tab_geo, tab_tempo, tab_calor = st.tabs(["📍 Geografia", "📅 Tempo", "🔥 Mapa de Calor"])

with tab_geo:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("10 Bairros com maior número de casos de dengue")
        ranking = df_filtrado_bairros.groupby('BAIRRO')['CASOS'].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_bar = px.bar(ranking, x='CASOS', y='BAIRRO', orientation='h', color='CASOS', color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_b:
        st.subheader("Casos por Região")
        reg_pie = df_filtrado_bairros.groupby('REGIAO')['CASOS'].sum().reset_index()
        fig_pie = px.pie(reg_pie, values='CASOS', names='REGIAO', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab_tempo:
    st.subheader(f"Sazonalidade Mensal: {label_tempo}")
    meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    sazonalidade = df_filtrado_mes.groupby('MÊS')['TOTAL_POSITIVOS'].sum().reindex(meses).reset_index()
    fig_area = px.area(sazonalidade, x='MÊS', y='TOTAL_POSITIVOS', markers=True, color_discrete_sequence=['#d32f2f'])
    st.plotly_chart(fig_area, use_container_width=True)

with tab_calor:
    st.subheader("Intensidade por Bairro ao longo dos Anos")
    # Pegamos os 15 bairros com mais casos no histórico total para o mapa não ficar gigante
    top_bairros_hist = df_bairros.groupby('BAIRRO')['CASOS'].sum().nlargest(15).index
    df_calor = df_bairros[df_bairros['BAIRRO'].isin(top_bairros_hist)]
    
    # Criar a matriz (Bairro vs Ano)
    pivot_calor = df_calor.pivot_table(index='BAIRRO', columns='ANO', values='CASOS', aggfunc='sum').fillna(0)
    
    fig_heat = px.imshow(pivot_calor, 
                        labels=dict(x="Ano", y="Bairro", color="Casos"),
                        color_continuous_scale='YlOrRd',
                        aspect="auto")
    st.plotly_chart(fig_heat, use_container_width=True)

st.caption("Dashboard desenvolvido para o Projeto de Extensão II - UNINTER.")