import streamlit as st
import plotly.express as px
import pandas as pd
from backend.analytics.movimentacao_mercado import calcular_fluxo_entrada_saida, gerar_analise_impacto
from views.components.tables import formatar_moeda_br

def render_movimentacao_mercado(df_mestre):
    st.header("🔄 Movimentação de Mercado (Entradas & Saídas)")
    st.markdown("Análise de fluxo de operadoras entre trimestres, com foco em impacto de vidas, receita e monitoramento da Rede Unimed.")
    
    # --- Filtros de Seleção ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        lista_trimestres = sorted(df_mestre['ID_TRIMESTRE'].unique(), reverse=True)
        
        with col1:
            tri_atual = st.selectbox("📅 Trimestre Referência (B):", lista_trimestres, index=0)   
        with col2:
            idx_anterior = 1 if len(lista_trimestres) > 1 else 0
            tri_anterior = st.selectbox("📅 Trimestre Comparativo (A):", lista_trimestres, index=idx_anterior)

    if tri_atual == tri_anterior:
        st.warning("⚠️ Selecione trimestres diferentes para realizar a comparação.")
        return

    # --- Processamento ---
    df_entrantes, df_saintes = calcular_fluxo_entrada_saida(df_mestre, tri_atual, tri_anterior)
    analise = gerar_analise_impacto(df_entrantes, df_saintes)
    imp_geral = analise['Geral']
    imp_unimed = analise['Unimed']

    # --- Seção 1: Resumo de Impacto Comparativo ---
    st.subheader("1. Impacto de Mercado vs. Rede Unimed")
    
    t1, t2 = st.tabs(["🌎 Impacto Mercado Geral", "🌲 Impacto Rede Unimed"])
    
    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Vidas Ganhas", f"{imp_geral['Vidas_Ganhas']:,.0f}".replace(",", "."), help="Soma de vidas das operadoras que entraram")
        c2.metric("Vidas Perdidas", f"{imp_geral['Vidas_Perdidas']:,.0f}".replace(",", "."), delta_color="inverse", help="Soma de vidas (no trimestre anterior) das que saíram")
        saldo_v = imp_geral['Saldo_Vidas']
        c3.metric("Saldo Líquido Vidas", f"{saldo_v:+,.0f}".replace(",", "."), delta=saldo_v)
        c4.metric("Saldo Líquido Receita", formatar_moeda_br(imp_geral['Saldo_Receita']), delta=imp_geral['Saldo_Receita'])

    with t2:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Unimeds Entrantes", imp_unimed['Qtd_Entrou'])
        c2.metric("Unimeds Saintes", imp_unimed['Qtd_Saiu'], delta_color="inverse")
        saldo_v_uni = imp_unimed['Saldo_Vidas']
        c3.metric("Saldo Vidas Unimed", f"{saldo_v_uni:+,.0f}".replace(",", "."), delta=saldo_v_uni)
        c4.metric("Saldo Receita Unimed", formatar_moeda_br(imp_unimed['Saldo_Receita']), delta=imp_unimed['Saldo_Receita'])

    st.divider()

    # --- Função Auxiliar de Formatação (CORRIGIDA) ---
    def preparar_tabela_exibicao(df):
        if df.empty: return df
        
        # Mapeamento: Nome na Base -> Nome na Tela
        cols_map = {
            'ID_OPERADORA': 'Registro ANS', 
            'razao_social': 'Razão Social', 
            'uf': 'UF', 
            'NR_BENEF_T': 'Vidas',
            'VL_SALDO_FINAL': 'Receita (R$)',
            'descredenciada_em': 'Data Descred.',
            'descredenciamento_motivo': 'Motivo'
        }
        
        # Seleciona apenas colunas que existem no dataframe
        cols_presentes = [c for c in cols_map.keys() if c in df.columns]
        df_show = df[cols_presentes].copy()
        
        # 1. Formatação de Vidas
        if 'NR_BENEF_T' in df_show.columns:
            df_show['NR_BENEF_T'] = pd.to_numeric(df_show['NR_BENEF_T'], errors='coerce').fillna(0)
            df_show['NR_BENEF_T'] = df_show['NR_BENEF_T'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
            
        # 2. Formatação de Receita (R$)
        if 'VL_SALDO_FINAL' in df_show.columns:
            # Garante que é número antes de formatar
            df_show['VL_SALDO_FINAL'] = pd.to_numeric(df_show['VL_SALDO_FINAL'], errors='coerce').fillna(0)
            df_show['VL_SALDO_FINAL'] = df_show['VL_SALDO_FINAL'].apply(formatar_moeda_br)

        # 3. Formatação de Data (Data Descredenciamento)
        if 'descredenciada_em' in df_show.columns:
            # Converte de string/iso para datetime e depois para string dd/mm/aaaa
            df_show['descredenciada_em'] = pd.to_datetime(df_show['descredenciada_em'], errors='coerce')
            df_show['descredenciada_em'] = df_show['descredenciada_em'].dt.strftime('%d/%m/%Y').fillna("-")
            
        return df_show.rename(columns=cols_map)

    # --- Seção 2: Monitoramento Detalhado UNIMED ---
    st.subheader("2. Detalhe Rede Unimed")
    
    col_u_entrou, col_u_saiu = st.columns(2)

    with col_u_entrou:
        st.info(f"🟢 **Unimeds que Entraram** ({imp_unimed['Qtd_Entrou']})")
        if not imp_unimed['Entrantes_DF'].empty:
            st.dataframe(preparar_tabela_exibicao(imp_unimed['Entrantes_DF']), hide_index=True, use_container_width=True)
        else:
            st.caption("Nenhuma entrada registrada.")

    with col_u_saiu:
        st.error(f"🔴 **Unimeds que Saíram** ({imp_unimed['Qtd_Saiu']})")
        if not imp_unimed['Saintes_DF'].empty:
            st.dataframe(preparar_tabela_exibicao(imp_unimed['Saintes_DF']), hide_index=True, use_container_width=True)
        else:
            st.caption("Nenhuma saída registrada.")

    st.divider()

    # --- Seção 3: Listagem Geral do Mercado ---
    st.subheader("3. Listagem Geral do Mercado")
    
    tab_e, tab_s = st.tabs([f"Entrantes Gerais ({len(df_entrantes)})", f"Saídas Gerais ({len(df_saintes)})"])
    
    with tab_e:
        if not df_entrantes.empty:
            st.dataframe(preparar_tabela_exibicao(df_entrantes), use_container_width=True, hide_index=True)
        else:
            st.info("Sem entrantes no período.")

    with tab_s:
        if not df_saintes.empty:
            st.markdown(f"ℹ️ *Dados financeiros e de vidas referentes ao último reporte em {tri_anterior}.*")
            st.dataframe(preparar_tabela_exibicao(df_saintes), use_container_width=True, hide_index=True)
        else:
            st.info("Sem saídas no período.")