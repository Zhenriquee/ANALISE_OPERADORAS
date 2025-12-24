import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from backend.analytics.data_science import (
    calcular_correlacoes, 
    preparar_dados_segmentacao, 
    calcular_outliers_ticket,
    calcular_elbow_method, # NOVO
    aplicar_kmeans_pca     # NOVO
)
from backend.analytics.brand_intelligence import extrair_marca
from views.components.tables import formatar_moeda_br


def render_ciencia_dados(df_mestre):
    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Configuração DS")
        trimestres = sorted(df_mestre['ID_TRIMESTRE'].unique(), reverse=True)
        sel_trimestre = st.selectbox("📅 Trimestre de Referência:", trimestres)
        
        st.info("ℹ️ **Nota:** Esta tela utiliza todo o dataset do trimestre selecionado para gerar padrões de mercado.")

    st.title("🧪 Ciência de Dados & Insights")
    st.markdown("Análises estatísticas avançadas para identificar padrões ocultos no mercado.")
    st.divider()

    # --- 1. Matriz de Correlação ---
    st.subheader("1. Correlação de Variáveis (O que influencia o quê?)")
    st.markdown("Identifique quais indicadores caminham juntos. *Ex: Se 'Cresc. Vidas' e 'Cresc. Receita' forem vermelhos (fortes), um impulsiona o outro.*")
    
    df_corr = calcular_correlacoes(df_mestre)
    
    fig_corr = px.imshow(
        df_corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r", # Vermelho para positivo, Azul para negativo
        origin='lower'
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.divider()

    # --- 2. Segmentação de Mercado (Quadrantes) ---
    st.subheader("2. Segmentação: Crescimento vs Tamanho")
    st.markdown("Onde os players estão posicionados? **Eixo X:** Tamanho (Share) | **Eixo Y:** Velocidade (Crescimento).")
    
    df_seg = preparar_dados_segmentacao(df_mestre, sel_trimestre)
    df_seg['Marca'] = df_seg['razao_social'].apply(extrair_marca)
    
    # Gráfico de Bolhas
    fig_seg = px.scatter(
        df_seg,
        x="Market_Share",
        y="VAR_PCT_RECEITA",
        size="NR_BENEF_T", # Tamanho da bolha = Vidas
        color="modalidade", # Cor = Modalidade
        hover_name="razao_social",
        log_x=True, # Escala logarítmica no X ajuda a ver pequenos e grandes juntos
        labels={"Market_Share": "Market Share (Log)", "VAR_PCT_RECEITA": "Crescimento Receita (%)", "NR_BENEF_T": "Vidas"},
        title=f"Mapa de Oportunidades - {sel_trimestre}"
    )
    
    # Linhas de média para criar quadrantes
    media_cresc = df_seg['VAR_PCT_RECEITA'].median()
    media_share = df_seg['Market_Share'].median()
    
    fig_seg.add_hline(y=media_cresc, line_dash="dot", annotation_text="Média Crescimento", line_color="grey")
    fig_seg.add_vline(x=media_share, line_dash="dot", annotation_text="Média Share", line_color="grey")
    
    st.plotly_chart(fig_seg, use_container_width=True)
    
    st.divider()

    # --- 3. Distribuição de Preços (Boxplot) ---
    st.subheader("3. Distribuição de Ticket Médio por Modalidade")
    st.markdown("Como os preços variam dentro de cada modalidade? Identifique outliers (pontos fora da caixa).")
    
    df_dist = calcular_outliers_ticket(df_mestre, sel_trimestre)
    
    # Filtra tickets absurdos (erro de dado) apenas para visualização (ex: > 50k)
    df_dist = df_dist[df_dist['Ticket_Medio'] < 5000] 
    
    fig_box = px.box(
        df_dist,
        x="modalidade",
        y="Ticket_Medio",
        color="modalidade",
        points="outliers", # Mostra apenas os pontos fora da curva
        title=f"Dispersão de Preços - {sel_trimestre}",
        labels={"Ticket_Medio": "Ticket Médio (R$)", "modalidade": "Modalidade"}
    )
    fig_box.update_layout(yaxis_tickprefix="R$ ")
    
    st.plotly_chart(fig_box, use_container_width=True)

    

    # --- 4. CLUSTERIZAÇÃO AVANÇADA ---
    st.subheader("4. Clusterização Avançada (2D & 3D)")
    st.markdown("Agrupamento de operadoras via Machine Learning (K-Means) projetado em múltiplas dimensões (PCA).")
    
    # Adicionamos a aba "Cubo 3D"
    tab_elbow, tab_2d, tab_3d, tab_info = st.tabs([
        "📐 Cotovelo (K Ideal)", 
        "🗺️ Mapa 2D", 
        "🧊 Cubo 3D (Interativo)", 
        "📋 Interpretação"
    ])
    
    # --- ABA 1: Cotovelo ---
    with tab_elbow:
        df_elbow = calcular_elbow_method(df_mestre, sel_trimestre)
        fig_elb = px.line(df_elbow, x='K', y='Inertia', markers=True, title="Método do Cotovelo")
        st.plotly_chart(fig_elb, use_container_width=True)
        
        k_sel = st.slider("Selecione o número de clusters (K):", 2, 8, 4)

    # --- PROCESSAMENTO ---
    # Processamento
    df_all, df_centroids, var_exp = aplicar_kmeans_pca(
        df_mestre, 
        sel_trimestre, 
        n_clusters=k_sel, 
        n_components=3
    )

    # --- ABA 2: Mapa 2D (Apenas Centroides) ---
    with tab_2d:
        st.info(f"Visualizando os {k_sel} grupos estratégicos.")
        
        fig_2d = px.scatter(
            df_centroids, 
            x="PC1", y="PC2", 
            color="Cluster_ID",
            size="Qtd_Operadoras", # Tamanho da bolha = Quantidade de empresas no grupo
            hover_name="Cluster_ID",
            # Dados que aparecem ao passar o mouse no grupo
            hover_data={
                "PC1": False, "PC2": False,
                "Qtd_Operadoras": True,
                "NR_BENEF_T": ":,.0f",
                "VL_SALDO_FINAL": ":,.2f",
                "Ticket_Medio": ":,.2f"
            },
            title=f"Posição Relativa dos {k_sel} Grupos (2D)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        # Aumenta o tamanho base das bolhas para ficarem visíveis
        fig_2d.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
        st.plotly_chart(fig_2d, use_container_width=True)

    # --- ABA 3: Cubo 3D (Apenas Centroides) ---
    with tab_3d:
        st.markdown(f"Visualizando a distância espacial entre os **{k_sel} grupos**.")
        
        fig_3d = px.scatter_3d(
            df_centroids, 
            x="PC1", y="PC2", z="PC3",
            color="Cluster_ID",
            size="Qtd_Operadoras", # Tamanho = Densidade do cluster
            hover_name="Cluster_ID",
            hover_data={
                "PC1": False, "PC2": False, "PC3": False,
                "Qtd_Operadoras": True,
                "NR_BENEF_T": ":,.0f",
                "VL_SALDO_FINAL": ":,.2f"
            },
            title=f"Distância entre Grupos (3D)",
            color_discrete_sequence=px.colors.qualitative.Bold,
            opacity=0.9
        )
        
        fig_3d.update_layout(
            height=600,
            scene=dict(
                xaxis_title='Dimensão 1 (Tamanho/Volume)',
                yaxis_title='Dimensão 2 (Crescimento)',
                zaxis_title='Dimensão 3 (Rentabilidade/Mix)'
            )
        )
        st.plotly_chart(fig_3d, use_container_width=True)

    # --- ABA 4: Interpretação (Tabela) ---
    with tab_info:
        st.markdown("### 📋 Perfil Médio de cada Cluster")
        
        # Adiciona a contagem na tabela para o usuário saber o tamanho do grupo
        view_summ = df_centroids.copy()
        view_summ['Qtd Ops'] = view_summ['Qtd_Operadoras']
        view_summ['Vidas (Méd)'] = view_summ['NR_BENEF_T'].map('{:,.0f}'.format)
        view_summ['Receita (Méd)'] = view_summ['VL_SALDO_FINAL'].apply(formatar_moeda_br)
        view_summ['Ticket (Méd)'] = view_summ['Ticket_Medio'].apply(formatar_moeda_br)
        view_summ['Cresc. Vidas'] = view_summ['VAR_PCT_VIDAS'].map('{:+.2%}'.format)
        
        cols = ['Cluster_ID', 'Qtd Ops', 'Vidas (Méd)', 'Receita (Méd)', 'Ticket (Méd)', 'Cresc. Vidas']
        st.dataframe(view_summ[cols].set_index('Cluster_ID'), use_container_width=True)