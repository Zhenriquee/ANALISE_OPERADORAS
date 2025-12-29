import streamlit as st
import plotly.express as px
from backend.analytics.movimentacao_mercado import calcular_fluxo_entrada_saida
from views.components.header import render_header
from views.components.tables import formatar_moeda_br

def render_movimentacao_mercado(df_mestre):
    st.header("🔄 Movimentação de Mercado (Entradas & Saídas)")
    st.markdown("Identifique operadoras que iniciaram ou encerraram suas atividades (ou relatórios) entre dois períodos.")
    
    # --- Filtros de Seleção ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        lista_trimestres = sorted(df_mestre['ID_TRIMESTRE'].unique(), reverse=True)
        
        with col1:
            tri_atual = st.selectbox(
                "📅 Trimestre Referência (B):", 
                lista_trimestres, 
                index=0,
                help="O período mais recente que você quer analisar."
            )
            
        with col2:
            # Tenta pegar o trimestre anterior automaticamente
            idx_anterior = 1 if len(lista_trimestres) > 1 else 0
            tri_anterior = st.selectbox(
                "📅 Trimestre Comparativo (A):", 
                lista_trimestres, 
                index=idx_anterior,
                help="O período passado para comparar. Quem estava aqui e não está mais no B?"
            )

    if tri_atual == tri_anterior:
        st.warning("⚠️ Selecione trimestres diferentes para realizar a comparação.")
        return

    # --- Processamento ---
    df_entrantes, df_saintes = calcular_fluxo_entrada_saida(df_mestre, tri_atual, tri_anterior)
    
    # --- Métricas Resumo ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.metric("Entrantes (Novas no B)", len(df_entrantes), delta=len(df_entrantes), delta_color="normal")
    with col_kpi2:
        st.metric("Saídas (Ausentes no B)", len(df_saintes), delta=-len(df_saintes), delta_color="inverse")
    with col_kpi3:
        saldo = len(df_entrantes) - len(df_saintes)
        st.metric("Saldo Líquido de Operadoras", saldo, delta=saldo)

    st.divider()

    # --- Visualização Detalhada ---
    tab_entrantes, tab_saintes = st.tabs([
        f"🟢 Entraram em {tri_atual} ({len(df_entrantes)})", 
        f"🔴 Saíram após {tri_anterior} ({len(df_saintes)})"
    ])
    
    # Colunas para exibir na tabela
    cols_view = ['ID_OPERADORA', 'razao_social', 'modalidade', 'uf', 'NR_BENEF_T', 'VL_SALDO_FINAL']
    cols_rename = {
        'ID_OPERADORA': 'Registro ANS',
        'razao_social': 'Razão Social', 
        'modalidade': 'Modalidade',
        'NR_BENEF_T': 'Vidas',
        'VL_SALDO_FINAL': 'Receita (R$)'
    }

    def preparar_tabela(df):
        if df.empty: return df
        
        # 1. Seleciona apenas colunas que existem no dataframe
        cols_presentes = [c for c in cols_view if c in df.columns]
        df_show = df[cols_presentes].copy()
        
        # 2. Formatação e Remoção das Colunas Originais
        if 'VL_SALDO_FINAL' in df_show.columns:
            # Cria a coluna formatada
            df_show['Receita (R$)'] = df_show['VL_SALDO_FINAL'].apply(formatar_moeda_br)
            # Remove a original imediatamente
            df_show = df_show.drop(columns=['VL_SALDO_FINAL'])
            
        if 'NR_BENEF_T' in df_show.columns:
            # Cria a coluna formatada
            df_show['Vidas'] = df_show['NR_BENEF_T'].map('{:,.0f}'.format)
            # Remove a original imediatamente
            df_show = df_show.drop(columns=['NR_BENEF_T'])
            
        # 3. Retorno Limpo
        # Apenas renomeamos as colunas estruturais (ex: uf -> UF, ID -> Registro)
        # Não usamos .drop() aqui pois já fizemos isso acima.
        return df_show.rename(columns=cols_rename)

    with tab_entrantes:
        if not df_entrantes.empty:
            st.dataframe(preparar_tabela(df_entrantes), width='stretch', hide_index=True)
            
            # Gráfico de perfil dos entrantes
            st.markdown("#### Perfil dos Entrantes por Modalidade")
            fig = px.pie(df_entrantes, names='modalidade', title='Distribuição por Tipo', hole=0.4)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info(f"Nenhuma operadora nova identificada em {tri_atual} comparado a {tri_anterior}.")

    with tab_saintes:
        if not df_saintes.empty:
            st.markdown(f"ℹ️ *Estes dados referem-se ao último registro visto em {tri_anterior}.*")
            st.dataframe(preparar_tabela(df_saintes), width='stretch', hide_index=True)
            
            # Análise de impacto da saída
            total_vidas_perdidas = df_saintes['NR_BENEF_T'].sum()
            st.caption(f"📉 A saída dessas operadoras retirou **{total_vidas_perdidas:,.0f} vidas** da base ativa (referência {tri_anterior}).")
        else:
            st.success(f"Nenhuma operadora deixou de reportar dados entre {tri_anterior} e {tri_atual}.")