import streamlit as st

def formatar_moeda_kpi(valor):
    """Helper simples para cards"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def render_kpi_row(kpis, rank_grupo_info=None):
    """Renderiza a linha de 4 métricas principais (Padrão)."""
    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "👥 Vidas", 
        f"{int(kpis['Vidas']):,}".replace(",", "."), 
        delta=f"{kpis.get('Var_Vidas_QoQ', 0):.1%} (QoQ)".replace(".", ","),
        delta_color="normal"
    )
    
    val_receita = formatar_moeda_kpi(kpis['Receita'])
    k2.metric(
        "💰 Receita", 
        val_receita,
        delta=f"{kpis.get('Var_Receita_QoQ', 0):.1%} (QoQ)".replace(".", ","),
        delta_color="normal"
    )

    val_ticket = formatar_moeda_kpi(kpis['Ticket'])
    k3.metric(
        "📊 Ticket Médio", 
        val_ticket
    )
    
    if rank_grupo_info:
        if isinstance(rank_grupo_info, tuple):
            rank, total, nome_grupo = rank_grupo_info
            k4.metric(f"🏢 Rank {nome_grupo}", f"#{rank}", f"de {total} ops", delta_color="off")
        else:
            k4.metric("📍 Sede", str(rank_grupo_info))

def render_revenue_kpi_row(kpis, kpis_avancados, rank_grupo_info=None):
    """
    Renderiza linha de KPIs focada em Receita.
    """
    k1, k2, k3 = st.columns(3)

    val_receita = formatar_moeda_kpi(kpis['Receita'])
    k1.metric(
        "💰 Receita Total", 
        val_receita,
        delta=f"{kpis.get('Var_Receita_QoQ', 0):.1%} (QoQ)".replace(".", ","),
        delta_color="normal"
    )

    val_ticket = formatar_moeda_kpi(kpis['Ticket'])
    var_ticket = kpis_avancados.get('Var_Ticket', 0)
    k2.metric(
        "📊 Ticket Médio", 
        val_ticket,
        delta=f"{var_ticket:.1%} (QoQ)".replace(".", ","),
        delta_color="normal",
        help="Variação positiva indica ganho de poder de preço (Pricing Power)."
    )
    
    share_br = kpis_avancados.get('Share_Nacional', 0)
    ctx_br = kpis_avancados.get('Ctx_Share_Nacional', 'N/A')
    k3.metric(
        "🌎 Market Share (Brasil)", 
        f"{share_br:.4f}%".replace('.', ','),
        help=f"**Fórmula:** Receita Operadora / Receita Total Brasil\n\n**Cálculo:** {ctx_br}"
    )
    
    st.markdown("") 
    
    k4, k5, k6 = st.columns(3)

    share_grp = kpis_avancados.get('Share_Grupo', 0)
    marca = kpis_avancados.get('Marca_Grupo', 'Grupo')
    ctx_grp = kpis_avancados.get('Ctx_Share_Grupo', 'N/A')
    
    k4.metric(
        f"🏢 Share no Grupo ({marca})", 
        f"{share_grp:.2f}%".replace('.', ','),
        help=f"**Conceito:** Representatividade financeira da operadora dentro do seu grupo econômico.\n\n**Fórmula:** Receita Operadora / Receita Total do Grupo\n**Cálculo:** {ctx_grp}"
    )
    
    cagr = kpis_avancados.get('CAGR_1Ano', 0)
    k5.metric(
        "📈 Crescimento Anual (CAGR)", 
        f"{cagr:.1%}".replace('.', ','),
        delta="12 Meses",
        help="Taxa de Crescimento Composto no último ano."
    )

    vol = kpis_avancados.get('Volatilidade', 0)
    k6.metric(
        "⚡ Volatilidade (Risco)", 
        f"{vol:.2f}%".replace('.', ','),
        help="Desvio padrão das variações de receita.",
        delta_color="off"
    )

def render_lives_kpi_row(kpis, kpis_avancados, rank_grupo_info=None):
    """
    Renderiza linha de KPIs focada em Vidas (Gestão de Carteira).
    """
    # --- LINHA 1 ---
    k1, k2, k3 = st.columns(3)

    # 1. Vidas
    k1.metric(
        "👥 Carteira de Vidas", 
        f"{int(kpis['Vidas']):,}".replace(",", "."), 
        delta=f"{kpis.get('Var_Vidas_QoQ', 0):.1%} (QoQ)".replace(".", ","),
        delta_color="normal"
    )

    # 2. Ticket
    val_ticket = formatar_moeda_kpi(kpis['Ticket'])
    k2.metric("📊 Ticket Médio", val_ticket, help="Valor médio pago por vida.")
    
    # 3. Share Brasil
    share_br = kpis_avancados.get('Share_Nacional', 0)
    ctx_br = kpis_avancados.get('Ctx_Share_Nacional', 'N/A')
    k3.metric(
        "🌎 Share Vidas (Brasil)", 
        f"{share_br:.4f}%".replace('.', ','),
        help=f"**Fórmula:** Vidas Operadora / Total Vidas Brasil\n\n**Cálculo:** {ctx_br}"
    )
    
    st.markdown("")
    
    # --- LINHA 2 ---
    k4, k5, k6 = st.columns(3)

    # 4. Share Grupo (Atualizado)
    share_grp = kpis_avancados.get('Share_Grupo', 0)
    marca = kpis_avancados.get('Marca_Grupo', 'Grupo')
    ctx_grp = kpis_avancados.get('Ctx_Share_Grupo', 'N/A')
    
    k4.metric(
        f"🏢 Share no Grupo ({marca})", 
        f"{share_grp:.2f}%".replace('.', ','),
        help=f"**Conceito:** Representatividade da carteira dentro do grupo econômico.\n\n**Fórmula:** Vidas Operadora / Total Vidas Grupo\n**Cálculo:** {ctx_grp}"
    )
    
    # 5. CAGR
    cagr = kpis_avancados.get('CAGR_1Ano', 0)
    k5.metric(
        "📈 Crescimento Carteira (CAGR)", 
        f"{cagr:.1%}".replace('.', ','),
        delta="12 Meses",
        help="Taxa de crescimento anual composta da carteira de vidas."
    )

    # 6. Volatilidade
    vol = kpis_avancados.get('Volatilidade', 0)
    k6.metric(
        "⚡ Volatilidade Carteira", 
        f"{vol:.2f}%".replace('.', ','),
        help="Instabilidade da base de clientes (Entradas/Saídas bruscas).",
        delta_color="off"
    )