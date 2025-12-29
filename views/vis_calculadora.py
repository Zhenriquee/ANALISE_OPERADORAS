import streamlit as st
from backend.use_cases.calculation_explainer import CalculationExplainerUseCase

# Import dos Novos Componentes
from views.components.calculator.tab_power_score import render_tab_power_score
from views.components.calculator.tab_spread import render_tab_spread
from views.components.calculator.tab_grupo import render_tab_grupo


def render_calculadora_didatica(df_mestre):
    st.header("🧮 Memória de Cálculo")
    st.caption("Auditoria detalhada baseada na regra de negócio oficial.")
    
    # Validação de Seleção
    if "filtro_id_op" not in st.session_state or "filtro_trimestre" not in st.session_state:
        st.warning("⚠️ Nenhuma operadora selecionada. Por favor, vá até a tela 'Raio-X da Operadora' e selecione uma empresa para auditar.")
        return
        
    id_op = st.session_state["filtro_id_op"]
    trimestre = st.session_state["filtro_trimestre"]
    
    # Execução do Caso de Uso
    use_case = CalculationExplainerUseCase(df_mestre)
    try:
        resultado = use_case.execute(id_op, trimestre)
    except Exception as e:
        st.error(f"Erro ao gerar memória de cálculo: {e}")
        return
        
    dados = resultado['dados_op']
    
    # Cabeçalho
    st.subheader(f"Auditoria: {dados['razao_social']}")
    st.markdown("---")
    
    # Abas Modularizadas
    tab1, tab2, tab3 = st.tabs(["⚡ Power Score", "📊 Performance Relativa", "🏢 Métricas de Grupo"])
    
    with tab1:
        render_tab_power_score(resultado['passos_score'])
        
    with tab2:
        render_tab_spread(resultado['extras'])
        
    with tab3:
        render_tab_grupo(resultado['extras'])