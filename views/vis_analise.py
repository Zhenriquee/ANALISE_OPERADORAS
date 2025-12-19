import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Imports de Backend
from backend.analytics.comparativos import calcular_variacoes_operadora
from backend.analytics.brand_intelligence import analisar_performance_marca, extrair_marca
from backend.analytics.calculadora_score import calcular_power_score

# --- FUNÇÃO AUXILIAR PARA GERAR GRÁFICOS ---
def _gerar_grafico_spread(df_mestre, id_operadora, nome_operadora, tipo_kpi, tipo_comparacao, filtro_grupo=None):
    col_valor = 'VL_SALDO_FINAL' if tipo_kpi == 'Receita' else 'NR_BENEF_T'
    col_var_pct = 'VAR_PCT_RECEITA' if tipo_kpi == 'Receita' else 'VAR_PCT_VIDAS'
    label_titulo = f"Spread {tipo_kpi}: {nome_operadora} vs {tipo_comparacao}"
    
    timeline_completa = sorted(df_mestre['ID_TRIMESTRE'].unique())

    df_op = df_mestre[df_mestre['ID_OPERADORA'] == str(id_operadora)].copy()
    df_op = df_op.set_index('ID_TRIMESTRE').reindex(timeline_completa)
    s_op_pct = df_op[col_valor].pct_change() * 100

    if tipo_comparacao == 'Grupo':
        df_ref = df_mestre[df_mestre['Marca_Temp'] == filtro_grupo].copy()
    else:
        df_ref = df_mestre.copy()
        
    s_ref_pct = df_ref.groupby('ID_TRIMESTRE')[col_var_pct].median() * 100
    s_ref_pct = s_ref_pct.reindex(timeline_completa)

    s_spread = s_op_pct - s_ref_pct
    
    df_graf = pd.DataFrame({
        'ID_TRIMESTRE': timeline_completa,
        'SPREAD': s_spread.values,
        'OP_PCT': s_op_pct.values,
        'REF_PCT': s_ref_pct.values
    }).dropna(subset=['SPREAD']).sort_values('ID_TRIMESTRE')

    if df_graf.empty: return None

    df_graf['Cor'] = np.where(df_graf['SPREAD'] >= 0, 'Superou', 'Abaixo')
    
    fig = px.bar(
        df_graf, x='ID_TRIMESTRE', y='SPREAD', color='Cor',
        color_discrete_map={'Superou': '#2E8B57', 'Abaixo': '#CD5C5C'},
        custom_data=['OP_PCT', 'REF_PCT']
    )
    
    fig.update_layout(
        title=dict(text=label_titulo, font=dict(size=14)),
        xaxis={'categoryorder':'category ascending'},
        xaxis_title=None, yaxis_title="Spread (p.p.)",
        legend_title=None, hovermode="x unified", height=350,
        showlegend=False, yaxis=dict(ticksuffix=" p.p.")
    )
    
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>Spread: %{y:.2f} p.p.</b>",
            f"{nome_operadora}: %{{customdata[0]:.2f}}%",
            f"{tipo_comparacao}: %{{customdata[1]:.2f}}%"
        ])
    )
    fig.add_hline(y=0, line_width=1, line_color="black")
    return fig

def render_analise(df_mestre):
    # --- 1. CONFIGURAÇÃO (SIDEBAR) ---
    with st.sidebar:
        st.header("⚙️ Configuração da Análise")
        
        opcoes_trimestre = sorted(df_mestre['ID_TRIMESTRE'].unique(), reverse=True)
        sel_trimestre = st.selectbox("📅 Trimestre de Análise:", options=opcoes_trimestre)
        st.markdown("---")
        
        st.subheader("🔍 Filtros de Busca")
        
        # Filtro Prévio de Trimestre
        df_base_filtro = df_mestre[df_mestre['ID_TRIMESTRE'] == sel_trimestre].copy()
        
        opcoes_modalidade = sorted(df_base_filtro['modalidade'].dropna().unique())
        sel_modalidade = st.selectbox("1️⃣ Modalidade:", options=["Todas"] + opcoes_modalidade, index=0)
        
        if sel_modalidade != "Todas":
            df_base_filtro = df_base_filtro[df_base_filtro['modalidade'] == sel_modalidade]

        # Tratamento de Marca
        df_base_filtro['Marca_Temp'] = df_base_filtro['razao_social'].apply(extrair_marca)
        df_mestre['Marca_Temp'] = df_mestre['razao_social'].apply(extrair_marca)

        lista_marcas = sorted(df_base_filtro['Marca_Temp'].unique())
        sel_grupo = st.selectbox("2️⃣ Filtrar por Grupo/Marca:", options=["Todos"] + lista_marcas, index=0)

        if sel_grupo != "Todos":
            df_base_filtro = df_base_filtro[df_base_filtro['Marca_Temp'] == sel_grupo]
            
        df_op_unicas = df_base_filtro[['ID_OPERADORA', 'razao_social', 'cnpj']].drop_duplicates()
        opcoes_map = {f"{row['razao_social']} ({row['cnpj']})": row['ID_OPERADORA'] for _, row in df_op_unicas.iterrows()}
        
        # Default Logic
        default_cnpj_root = "340952"
        index_default = 0
        lista_opcoes = sorted(list(opcoes_map.keys()))
        for i, op in enumerate(lista_opcoes):
            if default_cnpj_root in opcoes_map[op] or "UNIMED CARUARU" in op:
                index_default = i; break
        if index_default >= len(lista_opcoes): index_default = 0

        if not lista_opcoes:
            st.warning("Nenhuma operadora encontrada."); return

        sel_operadora_nome = st.selectbox("3️⃣ Selecione a Operadora:", options=lista_opcoes, index=index_default)
        id_operadora_sel = str(opcoes_map[sel_operadora_nome])
        st.markdown("---")

        with st.expander("📚 Glossário de Análise"):
            t_kpi, t_comp, t_estr = st.tabs(["KPIs", "Comparativos", "Estratégia"])
            with t_kpi:
                st.markdown("""
                **Entenda os Indicadores Básicos:**
                * **Power Score (0-100):** Nota geral de qualidade.
                * **Vidas (Carteira):** Total de beneficiários ativos.
                * **Receita (Financeiro):** Faturamento trimestral total.
                * **Ticket Médio:** Receita / Vidas.
                """)
            with t_comp:
                st.markdown("""
                **Entenda as Variações:**
                * **QoQ:** Trimestre atual vs Anterior.
                * **YoY:** Trimestre atual vs Ano Anterior.
                """)
            with t_estr:
                st.markdown("""
                **Inteligência de Mercado:**
                * **Spread (Alpha):** Diferença entre crescimento da operadora e média do mercado.
                * **Share of Brand:** Tamanho da operadora dentro do seu grupo.
                """)

    # --- 2. PROCESSAMENTO ROBUSTO ---
    df_tri = df_mestre[df_mestre['ID_TRIMESTRE'] == sel_trimestre].copy()
    df_tri['ID_OPERADORA'] = df_tri['ID_OPERADORA'].astype(str)
    
    operadora_row = df_tri[df_tri['ID_OPERADORA'] == id_operadora_sel]
    
    if operadora_row.empty:
        st.error(f"Sem dados para {sel_trimestre}."); return

    op_dados = operadora_row.iloc[0]
    marca_atual = extrair_marca(op_dados['razao_social'])
    
    # Ranks e Scores
    df_tri_scored = calcular_power_score(df_tri)
    df_tri_scored['Rank_Geral'] = df_tri_scored['Power_Score'].rank(ascending=False, method='min')
    df_tri_scored['ID_OPERADORA'] = df_tri_scored['ID_OPERADORA'].astype(str)
    
    df_tri_scored['Marca_Temp'] = df_tri_scored['razao_social'].apply(extrair_marca)
    df_grupo_scored = df_tri_scored[df_tri_scored['Marca_Temp'] == marca_atual].copy()
    df_grupo_scored['Rank_Grupo'] = df_grupo_scored['Power_Score'].rank(ascending=False, method='min')
    
    # Cálculo do Total do Grupo (IMPORTANTE PARA O KPI 4)
    total_grupo = len(df_grupo_scored)

    try:
        dados_geral = df_tri_scored[df_tri_scored['ID_OPERADORA'] == id_operadora_sel]
        if not dados_geral.empty:
            rank_geral = int(dados_geral.iloc[0]['Rank_Geral'])
            score_real = dados_geral.iloc[0]['Power_Score']
        else:
            rank_geral = "-"
            score_real = 0

        dados_grupo = df_grupo_scored[df_grupo_scored['ID_OPERADORA'] == id_operadora_sel]
        if not dados_grupo.empty:
            rank_grupo = int(dados_grupo.iloc[0]['Rank_Grupo'])
        else:
            rank_grupo = "-"
            
    except Exception as e:
        score_real, rank_geral, rank_grupo = 0, "-", "-"

    kpis = calcular_variacoes_operadora(df_mestre, id_operadora_sel, sel_trimestre)
    insights_marca = analisar_performance_marca(df_tri, op_dados)

    # --- 3. RENDERIZAÇÃO ---

    # CABEÇALHO
    st.caption(f"📅 Referência: **{sel_trimestre}** | Grupo: **{marca_atual}**")
    with st.container():
        c_rank, c_info = st.columns([1, 6])
        with c_rank:
            if isinstance(rank_geral, int) and rank_geral <= 3: cor_rank = "#DAA520" 
            else: cor_rank = "#1f77b4"
            st.markdown(f"<h1 style='text-align: center; color: {cor_rank}; font-size: 60px; margin: 0;'>#{rank_geral}</h1>", unsafe_allow_html=True)
            st.caption("Rank Geral")
        with c_info:
            st.markdown(f"## {op_dados['razao_social']}")
            st.markdown(f"**CNPJ:** {op_dados['cnpj']} | **Modalidade:** {op_dados['modalidade']} | 👤 **Gestão:** {str(op_dados.get('representante','')).title()} | **📍 Sede:** {str(op_dados.get('cidade','')).title()}/{str(op_dados.get('uf','')).title()}")
            st.progress(int(score_real) / 100, text=f"Power Score: {score_real:.1f}/100")

    st.divider()

    # --- LINHA DE KPIs (REINSERIDA) ---
    k1, k2, k3, k4 = st.columns(4)

    # 1. Vidas
    k1.metric(
        "👥 Vidas", 
        f"{int(kpis['Vidas']):,}".replace(",", "."), 
        delta=f"{kpis['Var_Vidas_QoQ']:.1%} (QoQ)",
        delta_color="normal"
    )
    
    # 2. Receita
    k2.metric(
        "💰 Receita", 
        f"R$ {kpis['Receita']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"{kpis['Var_Receita_QoQ']:.1%} (QoQ)",
        delta_color="normal"
    )

    # 3. Ticket
    k3.metric(
        "📊 Ticket Médio", 
        f"R$ {kpis['Ticket']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    
    # 4. Rank Grupo
    k4.metric(
        f"🏢 Rank {marca_atual}", 
        f"#{rank_grupo}",
        f"de {total_grupo} ops",
        delta_color="off"
    )

    st.divider()

    # MATRIZ KPI
    st.subheader("1. Matriz de Performance (Valores e Variações)")
    def fmt_val_delta(valor, delta, is_money=False):
        if is_money: val_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else: val_str = f"{int(valor):,}".replace(",", ".")
        return f"{val_str} ({delta:+.2%})"

    data_matrix = {
        "Indicador": ["👥 Carteira de Vidas", "💰 Receita Trimestral (R$)", "🎟️ Ticket Médio (R$)"],
        f"Resultado ({sel_trimestre})": [
            f"{int(kpis['Vidas']):,}".replace(",", "."),
            f"R$ {kpis['Receita']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"R$ {kpis['Ticket']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ],
        f"vs Anterior ({kpis['Ref_QoQ']})": [
            fmt_val_delta(kpis['Val_Vidas_QoQ'], kpis['Var_Vidas_QoQ']),
            fmt_val_delta(kpis['Val_Receita_QoQ'], kpis['Var_Receita_QoQ'], True), "-" 
        ],
        f"vs Ano Passado ({kpis['Ref_YoY']})": [
            fmt_val_delta(kpis['Val_Vidas_YoY'], kpis['Var_Vidas_YoY']),
            fmt_val_delta(kpis['Val_Receita_YoY'], kpis['Var_Receita_YoY'], True), "-"
        ]
    }
    st.dataframe(pd.DataFrame(data_matrix), use_container_width=True, hide_index=True)
    st.divider()

    # SPREAD
    st.subheader("2. Performance Relativa (Spread)")
    st.markdown("Comparativo do crescimento da operadora vs **Mediana do Mercado** e **Mediana do Grupo**.")
    tab_fin, tab_vol = st.tabs(["💰 Financeiro (Receita)", "👥 Volume (Vidas)"])

    with tab_fin:
        c_fin1, c_fin2 = st.columns(2)
        with c_fin1:
            fig_rec_mkt = _gerar_grafico_spread(df_mestre, id_operadora_sel, op_dados['razao_social'], "Receita", "Mercado Geral")
            if fig_rec_mkt: st.plotly_chart(fig_rec_mkt, use_container_width=True)
        with c_fin2:
            fig_rec_grp = _gerar_grafico_spread(df_mestre, id_operadora_sel, op_dados['razao_social'], "Receita", "Grupo", filtro_grupo=marca_atual)
            if fig_rec_grp: st.plotly_chart(fig_rec_grp, use_container_width=True)

    with tab_vol:
        c_vol1, c_vol2 = st.columns(2)
        with c_vol1:
            fig_vid_mkt = _gerar_grafico_spread(df_mestre, id_operadora_sel, op_dados['razao_social'], "Vidas", "Mercado Geral")
            if fig_vid_mkt: st.plotly_chart(fig_vid_mkt, use_container_width=True)
        with c_vol2:
            fig_vid_grp = _gerar_grafico_spread(df_mestre, id_operadora_sel, op_dados['razao_social'], "Vidas", "Grupo", filtro_grupo=marca_atual)
            if fig_vid_grp: st.plotly_chart(fig_vid_grp, use_container_width=True)
    st.divider()

    # HISTÓRICO
    st.subheader("3. Evolução Histórica (Tendência)")
    df_hist = df_mestre[df_mestre['ID_OPERADORA'] == str(id_operadora_sel)].sort_values('ID_TRIMESTRE')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['ID_TRIMESTRE'], y=df_hist['NR_BENEF_T'], name='Vidas', line=dict(color='#1f77b4', width=3), hovertemplate='%{y:,.0f} Vidas'))
    fig.add_trace(go.Scatter(x=df_hist['ID_TRIMESTRE'], y=df_hist['VL_SALDO_FINAL'], name='Receita (R$)', line=dict(color='#2ca02c', width=3, dash='dot'), yaxis='y2', hovertemplate='R$ %{y:,.2f}'))
    fig.update_layout(title="", xaxis=dict(title="Trimestre"), yaxis=dict(title=dict(text="Vidas", font=dict(color="#1f77b4")), tickfont=dict(color="#1f77b4")), yaxis2=dict(title=dict(text="Receita (R$)", font=dict(color="#2ca02c")), tickfont=dict(color="#2ca02c"), overlaying='y', side='right', tickprefix="R$ ", tickformat=",.2s"), legend=dict(x=0, y=1.1, orientation='h'), hovermode="x unified", height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # 4. RANKING DO GRUPO
    st.subheader(f"4. Ranking do Grupo: {marca_atual}")
    st.markdown(f"Listagem das operadoras do grupo **{marca_atual}** ordenadas por Score.")
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Participação no Grupo (Share)", f"{insights_marca['Share_of_Brand']:.2f}%")
    col_m2.metric("Média Cresc. Vidas (Grupo)", f"{insights_marca['Media_Cresc_Vidas_Grupo']:.2%}")
    
    df_view_grupo = df_grupo_scored.copy().sort_values('Power_Score', ascending=False)
    df_view_grupo['#'] = range(1, len(df_view_grupo) + 1)
    
    cols_finais = ['#', 'razao_social', 'uf', 'Power_Score', 'NR_BENEF_T', 'VL_SALDO_FINAL']
    nomes_colunas = {
        '#': 'Rank', 
        'razao_social': 'Operadora', 
        'uf': 'UF', 
        'Power_Score': 'Score', 
        'NR_BENEF_T': 'Vidas', 
        'VL_SALDO_FINAL': 'Receita (R$)'
    }
    
    st.dataframe(
        df_view_grupo[cols_finais].rename(columns=nomes_colunas),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Rank': st.column_config.NumberColumn("Rank", width="small"),
            'Score': st.column_config.NumberColumn("Score", format="%.1f"),
            'Vidas': st.column_config.NumberColumn("Vidas", format="%d"),
            'Receita (R$)': st.column_config.NumberColumn("Receita (R$)", format="R$ %.2f")
        }
    )
    
    st.divider()

    # 5. RANKING GERAL
    st.subheader(f"5. Ranking de Mercado (Geral)")
    st.markdown("Comparativo com **todas as operadoras do Brasil** (ou do filtro de modalidade), ordenadas por Score.")
    
    df_view_geral = df_tri_scored.copy().sort_values('Power_Score', ascending=False)
    df_view_geral['#'] = range(1, len(df_view_geral) + 1)
    
    st.dataframe(
        df_view_geral[cols_finais].rename(columns=nomes_colunas),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Rank': st.column_config.NumberColumn("Rank", width="small"),
            'Score': st.column_config.NumberColumn("Score", format="%.1f"),
            'Vidas': st.column_config.NumberColumn("Vidas", format="%d"),
            'Receita (R$)': st.column_config.NumberColumn("Receita (R$)", format="R$ %.2f")
        }
    )