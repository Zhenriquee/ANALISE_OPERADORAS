import streamlit as st
from views.components.tables import formatar_moeda_br

def render_tab_grupo(ex):
    """
    Renderiza a explicação das métricas de Grupo.
    Recebe o dicionário 'extras' do backend.
    """
    grp = ex['grupo']
    st.markdown(f"### 🏢 Análise do Grupo: **{grp['marca']}**")
    st.caption("Entenda como sua participação (Share) dentro do grupo é calculada.")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    
    # --- SHARE FINANCEIRO ---
    with c1:
        st.subheader("🍰 Share de Receita")
        st.latex(r"\text{Share} = \frac{\text{Sua Receita}}{\text{Soma da Receita de TODAS do Grupo}}")
        
        st.write("**Dados Brutos:**")
        st.text(f"Sua Receita:    {formatar_moeda_br(grp['total_op_rec'])}")
        st.text(f"Total do Grupo: {formatar_moeda_br(grp['total_grp_rec'])}")
        
        st.markdown(f"**Cálculo:** {grp['total_op_rec']:.2f} ÷ {grp['total_grp_rec']:.2f}")
        st.metric("Resultado (Share)", f"{grp['share_rec']:.2f}%")

    # --- CRESCIMENTO GRUPO ---
    with c2:
        st.subheader("📈 Referência de Crescimento")
        st.markdown("Calculamos a **Mediana** do crescimento de Vidas de todas as operadoras do grupo para servir de meta interna.")
        
        st.metric("Mediana do Grupo", f"{grp['mediana_cresc_vid']:+.2%}")
        st.caption("Metade das operadoras do seu grupo cresceu acima disso.")