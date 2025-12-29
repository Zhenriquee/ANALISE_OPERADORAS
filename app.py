import streamlit as st
from backend.services.data_engine import DataEngine

# Import das Views
from views.vis_panorama import render_panorama_mercado
from views.vis_analise import render_analise
from views.vis_receita import render_analise_receita
from views.vis_vidas import render_analise_vidas
from views.vis_comparativo import render_comparativo
from views.vis_calculadora import render_calculadora_didatica
from views.vis_ciencia_dados import render_ciencia_dados
from views.vis_movimentacao import render_movimentacao_mercado

# Configuração Global da Página
st.set_page_config(
    page_title="Analise Operadoras",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(show_spinner="Carregando Base ANS...")
def carregar_dados_globais():
    engine = DataEngine()
    return engine.gerar_dataset_mestre()

# Carrega uma vez para todo o app
if "df_mestre" not in st.session_state:
    st.session_state["df_mestre"] = carregar_dados_globais()

df = st.session_state["df_mestre"]

def page_panorama():
    render_panorama_mercado(df)

def page_analise():
    # Renderiza a tela normal
    render_analise(df)
    
def page_receita():
    render_analise_receita(df)

def page_vidas():
    render_analise_vidas(df)

def page_comparativo():
    render_comparativo(df)
    
def page_calculadora():
    render_calculadora_didatica(df)

def page_ciencia():
    render_ciencia_dados(df)    

def page_movimentacao():
    render_movimentacao_mercado(df)

pages = {
    "Visão de Mercado": [
        st.Page(page_panorama, title="Panorama Estratégico ANS", icon="🌎"),
    ],
    "Análise Estratégica": [
        st.Page(page_analise, title="Diagnóstico 360º", icon="🏥"),
        st.Page(page_receita, title="Performance Financeira", icon="💰"),
        st.Page(page_vidas, title="Gestão de Carteira", icon="👥"),
        st.Page(page_movimentacao, title="Movimentação de Mercado", icon="🔄"),
    ],
    "Ferramentas": [
        st.Page(page_comparativo, title="Benchmarking Competitivo", icon="⚖️"),
        st.Page(page_calculadora, title="Metodologia e Criterios", icon="📐"),
        st.Page(page_ciencia, title="Ciência de Dados", icon="🧪"),
    ]
}

pg = st.navigation(pages, position="top")

# --- RENDERIZAÇÃO ---
pg.run()