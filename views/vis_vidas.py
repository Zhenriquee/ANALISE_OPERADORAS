import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import traceback

# Imports Clean Arch
from backend.use_cases.lives_analysis import LivesAnalysisUseCase
from backend.exceptions import AppError
from backend.analytics.brand_intelligence import extrair_marca

# Imports Componentes Visuais
from views.components.header import render_header
from views.components.metrics import render_lives_kpi_row
from views.components.charts import render_spread_chart
from views.components.tables import render_ranking_table, formatar_moeda_br
from views.components.glossary import render_glossary
from views.components.footer import render_sidebar_footer
from views.components.sidebar_header import render_sidebar_header

def render_evolution_lives_chart(df_mestre, id_operadora):
    """(Helper local de visualização)"""
    df_hist = df_mestre[df_mestre['ID_OPERADORA'] == str(id_operadora)].sort_values('ID_TRIMESTRE')
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_hist['ID_TRIMESTRE'], y=df_hist['NR_BENEF_T'], 
        name='Vidas', line=dict(color='#1f77b4', width=4), 
        hovertemplate='%{y:,.0f} Vidas'
    ))
    fig.update_layout(
        title="", xaxis_title="Trimestre", 
        yaxis=dict(title="Vidas", tickformat=",.0f"),
        hovermode="x unified", height=400
    )
    return fig

def render_analise_vidas(df_mestre):
    # --- 1. CONTROLLER (Sidebar) ---
    with st.sidebar:
        render_sidebar_header()
        st.divider()
        st.header("⚙️ Filtros de Carteira")
        
        try:
            opcoes_trimestre = sorted(df_mestre['ID_TRIMESTRE'].unique(), reverse=True)
            sel_trimestre = st.selectbox("📅 Trimestre:", options=opcoes_trimestre)
        except Exception:
            st.error("Erro ao carregar lista de trimestres.")
            return
        
        # Filtros Cascata
        df_base = df_mestre[df_mestre['ID_TRIMESTRE'] == sel_trimestre].copy()
        
        opts_mod = ["Todas"] + sorted(df_base['modalidade'].dropna().unique())
        sel_mod = st.selectbox("1️⃣ Modalidade:", opts_mod)
        if sel_mod != "Todas": df_base = df_base[df_base['modalidade'] == sel_mod]
        
        # Grupo
        df_base['Marca_Temp'] = df_base.apply(
            lambda row: extrair_marca(row['razao_social'], row['ID_OPERADORA']), 
            axis=1
        )
        opts_grupo = ["Todos"] + sorted(df_base['Marca_Temp'].unique())
        sel_grupo = st.selectbox("2️⃣ Grupo:", opts_grupo)
        if sel_grupo != "Todos": df_base = df_base[df_base['Marca_Temp'] == sel_grupo]
        
        # Operadora
        df_ops = df_base[['ID_OPERADORA', 'razao_social', 'cnpj']].drop_duplicates()
        map_ops = {f"{r['razao_social']} ({r['cnpj']})": str(r['ID_OPERADORA']) for _, r in df_ops.iterrows()}
        
        idx_def = 0
        lista_ops = sorted(list(map_ops.keys()))
        for i, op in enumerate(lista_ops):
            if "340952" in map_ops[op] or "UNIMED CARUARU" in op: idx_def = i; break
            
        if not lista_ops: st.warning("Sem operadoras."); return
        sel_op_nome = st.selectbox("3️⃣ Operadora:", lista_ops, index=idx_def)
        id_op = map_ops[sel_op_nome]
        
        st.markdown("---")
        render_glossary()
        render_sidebar_footer()

    # --- 2. EXECUÇÃO DO CASO DE USO ---
    try:
        use_case = LivesAnalysisUseCase(df_mestre)
        resultado = use_case.execute(id_operadora=id_op, trimestre=sel_trimestre)
        
        info = resultado['info']
        metrics = resultado['metrics']
        content = resultado['content']

    except AppError as e:
        st.warning(f"Atenção: {str(e)}")
        return
    except Exception as e:
        st.error(f"Erro crítico: {str(e)}")
        with st.expander("Detalhes Técnicos"):
            st.code(traceback.format_exc())
        return

    # --- 3. RENDERIZAÇÃO ---
    
    st.caption(f"📅 Referência: **{info['trimestre']}** | Grupo: **{info['marca']}** | Visão: **Carteira de Vidas**")
    
    # Header
    render_header(info['dados_op'], metrics['rank_geral'], metrics['score'])
    st.divider()

    # Storytelling
    st.info(content['storytelling'], icon="👥")
    st.divider()
    
    # KPIs Grid (Avançado - Similar ao Financeiro)
    render_lives_kpi_row(
        metrics['kpis'], 
        metrics['kpis_avancados'],
        rank_grupo_info=(metrics['rank_grupo'], metrics['total_grupo'], info['marca'])
    )
    st.divider()
    
    # Matriz Volume
    st.subheader("1. Matriz de Performance (Volume)")
    def fmt_mat(val, delta, money=False):
        v_str = formatar_moeda_br(val) if money else f"{int(val):,}".replace(",", ".")
        return f"{v_str} ({delta:+.2%})"
        
    kpis = metrics['kpis']
    matriz = {
        "Indicador": ["Carteira de Vidas", "Ticket Médio"],
        "Atual": [f"{int(kpis['Vidas']):,}".replace(",", "."), formatar_moeda_br(kpis['Ticket'])],
        "vs QoQ": [fmt_mat(kpis['Val_Vidas_QoQ'], kpis['Var_Vidas_QoQ']), "-"],
        "vs YoY": [fmt_mat(kpis['Val_Vidas_YoY'], kpis['Var_Vidas_YoY']), "-"]
    }
    st.dataframe(pd.DataFrame(matriz), width="stretch", hide_index=True)
    st.divider()
    
    # Gráficos Spread
    st.subheader("2. Performance Relativa (Spread de Vidas)")
    
    # Prepara DF Gráficos
    df_graficos = content['df_full'].copy()
    if 'Marca_Temp' not in df_graficos.columns:
        df_graficos['Marca_Temp'] = df_graficos.apply(
            lambda row: extrair_marca(row['razao_social'], row['ID_OPERADORA']), 
            axis=1
        )
    
    c1, c2 = st.columns(2)
    c1.plotly_chart(render_spread_chart(df_graficos, info['id_op'], info['dados_op']['razao_social'], "Vidas", "Mercado"), width="stretch")
    c2.plotly_chart(render_spread_chart(df_graficos, info['id_op'], info['dados_op']['razao_social'], "Vidas", "Grupo", info['marca']), width="stretch")
    st.divider()
    
    # Evolução
    st.subheader("3. Evolução Histórica da Carteira")
    st.plotly_chart(render_evolution_lives_chart(df_graficos, info['id_op']), width="stretch")
    st.divider()
    
    # Tabelas
    render_ranking_table(
        content['tabela_grupo'], 
        titulo=f"4. Ranking Carteira Grupo: {info['marca']}",
        subtitulo="Ordenado por Score de Vidas (Volume + Crescimento)."
    )
    st.divider()
    
    render_ranking_table(
        content['tabela_geral'], 
        titulo="5. Ranking Carteira Geral",
        subtitulo="Comparativo de mercado baseado em performance de vidas."
    )