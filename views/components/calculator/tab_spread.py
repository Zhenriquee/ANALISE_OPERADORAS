import streamlit as st

def render_tab_spread(ex):
    """
    Renderiza a explicação detalhada do Spread (Performance Relativa).
    Recebe o dicionário 'extras' do backend.
    """
    st.markdown("### 📊 Performance Relativa (Spread)")
    st.markdown("""
    O Spread responde à pergunta: **"Minha operadora cresceu mais ou menos que o mercado?"**
    
    Ele é calculado subtraindo o crescimento mediano do mercado do seu crescimento.
    """)
    st.divider()
    
    c1, c2 = st.columns(2)
    
    # --- SPREAD RECEITA ---
    with c1:
        st.subheader("💰 Spread de Receita")
        sr = ex['spread_receita']
        
        st.write("Cálculo Passo a Passo:")
        st.text(f"1. Seu Crescimento:      {sr['op']:+.2%}")
        st.text(f"2. Mediana do Mercado: - {sr['mkt']:+.2%}")
        st.text("--------------------------------")
        st.text(f"Resultado:               {sr['res']:+.2%} ({sr['res']*100:+.2f} p.p.)")
        
        if sr['res'] > 0:
            st.success("✅ Você ganhou Market Share financeiro.")
        else:
            st.error("🔻 Você cresceu menos que a média do mercado.")

    # --- SPREAD VIDAS ---
    with c2:
        st.subheader("👥 Spread de Vidas")
        sv = ex['spread_vidas']
        
        st.write("Cálculo Passo a Passo:")
        st.text(f"1. Seu Crescimento:      {sv['op']:+.2%}")
        st.text(f"2. Mediana do Mercado: - {sv['mkt']:+.2%}")
        st.text("--------------------------------")
        st.text(f"Resultado:               {sv['res']:+.2%} ({sv['res']*100:+.2f} p.p.)")
        
        if sv['res'] > 0:
            st.success("✅ Sua base cresceu acima da média.")
        else:
            st.error("🔻 Crescimento de carteira abaixo da média.")