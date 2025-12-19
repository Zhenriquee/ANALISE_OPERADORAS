import streamlit as st
import pandas as pd

# Importando as Lógicas
from backend.analytics.filtros_mercado import filtrar_por_modalidade
from backend.analytics.calculadora_score import calcular_power_score
from views.styles import aplicar_estilo_ranking

def render_panorama_mercado(df_mestre):
    # 1. Preparação
    ultimo_trimestre = df_mestre['ID_TRIMESTRE'].max()
    df_base = df_mestre[df_mestre['ID_TRIMESTRE'] == ultimo_trimestre].copy()

    # --- CONTROLES E FILTROS ---
    with st.container():
        col_filtro, col_info = st.columns([1.5, 2])
        
        with col_filtro:
            opcoes_modalidade = sorted(df_base['modalidade'].dropna().unique())
            sel_modalidade = st.multiselect(
                "📌 Filtrar por Modalidade:",
                options=opcoes_modalidade,
                placeholder="Selecione (Vazio = Todas)"
            )
        
        # --- NOVO GLOSSÁRIO DETALHADO ---
        with col_info:
            with st.expander("📚 Glossário: Entenda os Cálculos, Score e Siglas"):
                tab_score, tab_share, tab_evolucao = st.tabs(["🏆 Power Score", "🍰 Market Share", "📈 Evolução (Vol/Fin)"])
                
                with tab_score:
                    st.markdown("""
                    **O que é?** Nota de 0 a 100 que define a força da operadora.
                    **Fórmula:**
                    $$Score = (0.4 \\times Vidas) + (0.4 \\times Receita) + (0.2 \\times Performance)$$
                    * **40% Tamanho:** Baseado no número de vidas (normalizado pelo máximo do filtro).
                    * **40% Financeiro:** Baseado na receita total (normalizado pelo máximo do filtro).
                    * **20% Performance:** Baseado na média de crescimento trimestral (Vidas + Receita).
                    """)
                
                with tab_share:
                    st.markdown("""
                    **O que é?** A fatia de mercado que a operadora domina dentro do filtro selecionado.
                    **Fórmula :**
                    $$Share = \\frac{\\text{Valor da Operadora}}{\\text{Soma Total do Mercado (Filtro)}} \\times 100$$
                    Exemplo: Se a soma de todas as receitas das cooperativas for 1 Milhão e a operadora faturou 
                                R$ 100 mil, seu Share é 10%.
                    """)
                
                with tab_evolucao:
                    st.markdown("""
                    **O que é ?** A variação percentual em relação ao trimestre anterior (Trimestre a Trimestre).
                    
                    * **(Vol):** Abreviatura para **Volume de Vidas**. Indica se a carteira de beneficiários cresceu ou diminuiu.
                    * **(Fin):** Abreviatura para **Financeiro (Receita)**. Indica se o faturamento (Conta 31) cresceu ou diminuiu.
                    
                    **Interpretação:**
                    * <span style='color:green'>Verde (+):</span> Crescimento.
                    * <span style='color:red'>Vermelho (-):</span> Queda/Retração.
                    """, unsafe_allow_html=True)

    # 2. Lógica de Negócio
    df_filtrado = filtrar_por_modalidade(df_base, sel_modalidade)
    
    if df_filtrado.empty:
        st.warning("Sem dados para os filtros selecionados.")
        return

    df_ranqueado = calcular_power_score(df_filtrado)
    df_ranqueado['Rank'] = df_ranqueado.index + 1
    
    # Contexto e Totais para cálculo do Share
    texto_contexto = f"Filtro: {', '.join(sel_modalidade)}" if sel_modalidade else "Mercado Total"
    total_vidas = df_filtrado['NR_BENEF_T'].sum()
    total_receita = df_filtrado['VL_SALDO_FINAL'].sum()

    # --- CARD DO LÍDER ---
    top_1 = df_ranqueado.iloc[0]
    
    st.divider()
    st.caption(f"📅 Referência: **{ultimo_trimestre}** | 🔍 {texto_contexto}")

    with st.container():
        c_rank, c_info = st.columns([1, 6])
        with c_rank:
            st.markdown(f"<h1 style='text-align: center; color: #DAA520; font-size: 60px; margin: 0;'>#1</h1>", unsafe_allow_html=True)
            st.caption("Líder do Filtro")
        with c_info:
            st.markdown(f"## {top_1['razao_social']}")
            st.markdown(f"**CNPJ:** {top_1['cnpj']} | **Modalidade:** {top_1['modalidade']}")
            st.progress(int(top_1['Power_Score']) / 100, text=f"Power Score: {top_1['Power_Score']:.1f}/100")

        st.divider()
        
        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        
        # Vidas + Delta
        k1.metric("👥 Vidas", f"{int(top_1['NR_BENEF_T']):,}".replace(",", "."), 
                  delta=f"{top_1['VAR_PCT_VIDAS']*100:.2f}% (Vol)",
                  delta_color="normal",
                  help="Variação de Volume (Vidas) vs Trimestre Anterior")
        
        # Cálculo Share Vidas
        share_vidas = (top_1['NR_BENEF_T']/total_vidas)*100
        k1.caption(f"Share Vidas: {share_vidas:.2f}%")

        # Receita + Delta
        k2.metric("💰 Receita", f"R$ {top_1['VL_SALDO_FINAL']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                  delta=f"{top_1['VAR_PCT_RECEITA']*100:.2f}% (Fin)",
                  delta_color="normal",
                  help="Variação Financeira (Receita) vs Trimestre Anterior")
        
        # Cálculo Share Receita
        share_receita = (top_1['VL_SALDO_FINAL']/total_receita)*100
        k2.caption(f"Share Receita: {share_receita:.2f}%")

        ticket = top_1['VL_SALDO_FINAL'] / top_1['NR_BENEF_T'] if top_1['NR_BENEF_T'] > 0 else 0
        k3.metric("📊 Ticket Médio", f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                  help="Receita Total dividida pelo Total de Vidas")

        k4.metric("📍 Sede", f"{str(top_1.get('cidade','')).title()}/{str(top_1.get('uf',''))}")

        # Info Executiva
        nome = str(top_1.get('representante') or 'Não Informado').title()
        cargo = str(top_1.get('cargo_representante') or '').title()
        st.info(f"**Gestão:** {nome} — *{cargo}*")

    st.divider()

    # --- TABELA TOP 30 ---
    st.subheader(f"🏆 Ranking de Performance - {texto_contexto}")
    st.markdown("*Use a barra de rolagem para ver mais detalhes. As colunas 'Δ' indicam a variação percentual trimestral.*")
    
    cols_view = ['Rank', 'razao_social', 'modalidade', 'Power_Score', 'NR_BENEF_T', 'VAR_PCT_VIDAS', 'VL_SALDO_FINAL', 'VAR_PCT_RECEITA']
    df_view = df_ranqueado.head(30)[cols_view].copy()
    
    # Renomear para exibição amigável
    df_view.columns = ['Rank', 'Operadora', 'Modalidade', 'Score', 'Vidas', 'Δ Vol (%)', 'Receita (R$)', 'Δ Fin (%)']

    styler = aplicar_estilo_ranking(df_view)
    
    # Formatação (Percentual e Moeda)
    styler.format({
        'Score': "{:.1f}", 
        'Vidas': "{:,.0f}", 
        'Δ Vol (%)': "{:.2%}", 
        'Receita (R$)': "R$ {:,.2f}",
        'Δ Fin (%)': "{:.2%}" 
    })

    st.dataframe(styler, use_container_width=True, height=800, hide_index=True)