import streamlit as st
from views.components.tables import formatar_moeda_br

def render_tab_power_score(ps):
    """
    Renderiza a explicação detalhada do Power Score.
    Recebe o dicionário 'passos_score' do backend.
    """
    st.markdown("### ⚡ Decomposição do Power Score")
    st.info(f"O Power Score final é **{ps['final']:.1f} / 100**. Veja abaixo a contribuição de cada pilar.")

    # Calculamos a contribuição em pontos (Score * Peso)
    pts_vidas = ps['vidas']['score'] * 0.40
    pts_rec = ps['receita']['score'] * 0.40
    pts_perf = ps['perf']['final_score'] * 0.20
    
    # --- 1. PILAR VIDAS ---
    with st.expander(f"1. Pilar Tamanho de Carteira (Vidas) - Contribui com **{pts_vidas:.1f} pontos**", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("1. Seu Volume", f"{int(ps['vidas']['real']):,}".replace(",", "."))
        c2.metric("2. Máximo Mercado", f"{int(ps['vidas']['max_mkt']):,}".replace(",", "."))
        c3.metric("3. Score (0-100)", f"{ps['vidas']['score']:.1f}")
        c4.metric("4. Pontos (Peso 40%)", f"+ {pts_vidas:.1f}", help="Score * 0.4")
        
        st.markdown("**Racional:**")
        st.latex(r"\text{Score} = \frac{\text{Vidas Operadora}}{\text{Maior Operadora do Mercado}} \times 100")
        st.latex(fr"\text{{Pontos}} = {ps['vidas']['score']:.1f} \times 0.40 = \textbf{{{pts_vidas:.2f}}}")

    # --- 2. PILAR RECEITA ---
    with st.expander(f"2. Pilar Faturamento (Receita) - Contribui com **{pts_rec:.1f} pontos**", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("1. Sua Receita", formatar_moeda_br(ps['receita']['real']))
        c2.metric("2. Máximo Mercado", formatar_moeda_br(ps['receita']['max_mkt']))
        c3.metric("3. Score (0-100)", f"{ps['receita']['score']:.1f}")
        c4.metric("4. Pontos (Peso 40%)", f"+ {pts_rec:.1f}", help="Score * 0.4")
        
        st.markdown("**Racional:**")
        st.latex(r"\text{Score} = \frac{\text{Receita Operadora}}{\text{Maior Receita do Mercado}} \times 100")
        st.latex(fr"\text{{Pontos}} = {ps['receita']['score']:.1f} \times 0.40 = \textbf{{{pts_rec:.2f}}}")

    # --- 3. PILAR PERFORMANCE ---
    with st.expander(f"3. Pilar Performance (Crescimento) - Contribui com **{pts_perf:.1f} pontos**", expanded=False):
        st.markdown("A performance é a média de duas notas: **Crescimento de Vidas** e **Crescimento de Receita**.")
        
        col_A, col_B = st.columns(2)
        
        # Performance Vidas
        with col_A:
            st.caption("A. Nota Vidas")
            st.metric("Cresc. Real", f"{ps['perf']['vid_real']:+.2%}")
            st.metric("Clipado (-10% a +10%)", f"{ps['perf']['vid_clip']:+.2%}")
            st.metric("Nota Parcial", f"{ps['perf']['vid_score']:.1f}")
            
        # Performance Receita
        with col_B:
            st.caption("B. Nota Receita")
            st.metric("Cresc. Real", f"{ps['perf']['rec_real']:+.2%}")
            st.metric("Clipado (-10% a +10%)", f"{ps['perf']['rec_clip']:+.2%}")
            st.metric("Nota Parcial", f"{ps['perf']['rec_score']:.1f}")
            
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Média (A + B) / 2", f"{ps['perf']['final_score']:.1f}")
        c2.metric("Peso", "20%")
        c3.metric("Pontos Finais", f"+ {pts_perf:.1f}")

    # --- SOMATÓRIO FINAL ---
    st.divider()
    st.subheader("🏁 Conta Final")
    st.latex(r"\text{Power Score} = \text{Pts Vidas} + \text{Pts Receita} + \text{Pts Performance}")
    
    cols = st.columns(5)
    cols[0].metric("Pts Vidas", f"{pts_vidas:.1f}")
    cols[1].markdown("### +")
    cols[2].metric("Pts Receita", f"{pts_rec:.1f}")
    cols[3].markdown("### +")
    cols[4].metric("Pts Perf.", f"{pts_perf:.1f}")
    
    st.success(f"**Resultado = {ps['final']:.1f}**")