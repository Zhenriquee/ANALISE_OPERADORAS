import streamlit as st
from backend.services.data_engine import DataEngine

# Import das Views
from views.vis_panorama import render_panorama_mercado
from views.vis_analise import render_analise
from views.vis_receita import render_analise_receita
from views.vis_vidas import render_analise_vidas
from views.vis_comparativo import render_comparativo
from views.vis_calculadora import render_calculadora_didatica

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

# --- FUNÇÕES WRAPPERS (Para capturar estado) ---
# Precisamos interceptar a renderização para saber qual operadora foi escolhida
# Nota: Nas views atuais, a seleção ocorre DENTRO delas.
# Para a Calculadora funcionar, as views precisariam escrever no st.session_state['filtro_id_op'].
# Como não queremos refatorar TODAS as views agora, vamos assumir que o usuário
# precisa selecionar manualmente na calculadora se não estiver gravado, 
# mas vamos injetar um callback simples nas próximas refatorações.

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
    # Esta página vai tentar ler do session_state
    # (Para funcionar perfeitamente, precisaríamos adicionar st.session_state['filtro_id_op'] = id_op 
    # dentro de vis_analise.py. Por enquanto, ela vai mostrar o aviso para selecionar.)
    render_calculadora_didatica(df)

# --- DEFINIÇÃO DA NAVEGAÇÃO (st.navigation) ---
# Aqui criamos os títulos bonitos e ícones
pages = {
    "Visão de Mercado": [
        st.Page(page_panorama, title="Panorama Estratégico ANS", icon="🌎"),
    ],
    "Análise Estratégica": [
        st.Page(page_analise, title="Diagnóstico 360º", icon="🏥"),
        st.Page(page_receita, title="Performance Financeira", icon="💰"),
        st.Page(page_vidas, title="Gestão de Carteira", icon="👥"),
    ],
    "Ferramentas": [
        st.Page(page_comparativo, title="Benchmarking Competitivo", icon="⚖️"),
        st.Page(page_calculadora, title="Metodologia e Criterios", icon="📐"),
    ]
}

pg = st.navigation(pages, position="top")

# --- RENDERIZAÇÃO ---
pg.run()