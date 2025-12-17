import streamlit as st
import pandas as pd
from configuracoes import QUERIES_PATH

from infra.db_connector import ConexaoSQLite
from backend.repository import AnsRepository
from backend.services.filter_service import FilterService

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard ANS - Unimed",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO COM CACHE ---
# O @st.cache_resource é usado para conexões e classes que não mudam.
# Isso evita que o Streamlit recrie a conexão com o banco a cada clique.
@st.cache_resource
def get_filter_service():
    # 1. Conecta (Pega caminho do settings.py automaticamente)
    conector = ConexaoSQLite()
    
    # 2. Prepara Repositório
    repo = AnsRepository(conector, QUERIES_PATH)
    
    # 3. Retorna o Serviço
    return FilterService(repo)

# O @st.cache_data é usado para armazenar DataFrames.
# Se os dados não mudaram, ele não roda a query SQL de novo (muito rápido).
@st.cache_data
def carregar_dados_operadoras(_service):
    return _service.get_todas_operadoras()

def main():
    # 1. Instancia os serviços (uma única vez graças ao cache)
    service = get_filter_service()
    
    # 2. Carrega os dados
    df_operadoras = carregar_dados_operadoras(service)

    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.title("Filtros")
    st.sidebar.header("Seleção de Operadora")

    if not df_operadoras.empty:
        # Cria uma lista formatada: "123456 - UNIMED CARUARU..."
        # Isso ajuda o usuário a ver o código e o nome juntos
        opcoes = df_operadoras.apply(
            lambda x: f"{x['registro_operadora']} - {x['razao_social']}", axis=1
        )
        
        # Selectbox com pesquisa
        escolha = st.sidebar.selectbox(
            "Selecione a Operadora Foco:",
            options=opcoes,
            index=0 # Começa com a primeira da lista
        )
        
        # Extrai o código da string selecionada (pega tudo antes do primeiro " - ")
        cod_selecionado = escolha.split(" - ")[0]
        
        st.sidebar.markdown("---")
        st.sidebar.info(f"**Operadora Selecionada:**\n\n{escolha}")
        st.sidebar.text(f"CNPJ: {df_operadoras[df_operadoras['registro_operadora'] == cod_selecionado]['cnpj'].values[0]}")

    else:
        st.error("Nenhuma operadora carregada do banco de dados.")
        st.stop()

    # --- ÁREA PRINCIPAL ---
    st.title("📊 Painel Estratégico ANS")
    st.markdown("Visualize os dados comparativos das operadoras de saúde.")
    
    st.divider()

    # Apenas para debug/visualização inicial: Mostra o DF bruto carregado
    st.subheader("Base de Operadoras Disponíveis")
    st.dataframe(
        df_operadoras, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "registro_operadora": "Reg. ANS",
            "razao_social": "Razão Social",
            "cnpj": "CNPJ",
            "nome_fantasia": "Nome Fantasia"
        }
    )

# Executa a aplicação
if __name__ == "__main__":
    main()