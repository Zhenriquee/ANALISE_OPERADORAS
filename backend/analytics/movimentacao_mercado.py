import pandas as pd
from backend.analytics.brand_intelligence import extrair_marca

def calcular_fluxo_entrada_saida(df_mestre, trimestre_ref, trimestre_comp):
    """
    Identifica operadoras que entraram e saíram do mercado entre dois trimestres.
    """
    # 1. Filtrar os dados dos dois períodos
    df_ref = df_mestre[df_mestre['ID_TRIMESTRE'] == trimestre_ref].copy()
    df_comp = df_mestre[df_mestre['ID_TRIMESTRE'] == trimestre_comp].copy()
    
    # 2. Extrair conjuntos de IDs únicos
    ids_ref = set(df_ref['ID_OPERADORA'].unique())
    ids_comp = set(df_comp['ID_OPERADORA'].unique())
    
    # 3. Calcular Diferenças
    ids_novos = ids_ref - ids_comp      # Entrantes (Estão em Ref, não estavam em Comp)
    ids_excluidos = ids_comp - ids_ref  # Saintes (Estavam em Comp, não estão em Ref)
    
    # 4. Recuperar dados detalhados
    # Entrantes: Pegamos os dados do trimestre ATUAL (Ref)
    df_entrantes = df_ref[df_ref['ID_OPERADORA'].isin(ids_novos)].copy()
    
    # Saintes: Pegamos os dados do trimestre ANTERIOR (Comp)
    # Isso garante que 'Vidas Perdidas' seja exatamente o que a operadora tinha antes de sair
    df_saintes = df_comp[df_comp['ID_OPERADORA'].isin(ids_excluidos)].copy()
    
    # 5. Enriquecimento com Dados Cadastrais (Datas e Motivos) se disponíveis no df_mestre
    # Como df_ref e df_comp são recortes, as colunas 'descredenciada_em' e 'descredenciamento_motivo' 
    # já devem estar presentes se existirem no banco de dados.
    
    return df_entrantes, df_saintes

def gerar_analise_impacto(df_entrantes, df_saintes):
    """
    Calcula o impacto financeiro, de vidas e segmenta para Mercado e Unimed.
    """
    # --- 1. Aplicação de Marca ---
    def _aplicar_marca(df):
        if not df.empty:
            df['ID_OPERADORA'] = df['ID_OPERADORA'].astype(str)
            df['Marca_Temp'] = df.apply(
                lambda row: extrair_marca(row['razao_social'], row['ID_OPERADORA']), axis=1
            )
        else:
            df['Marca_Temp'] = []
        return df

    df_entrantes = _aplicar_marca(df_entrantes)
    df_saintes = _aplicar_marca(df_saintes)

    # --- 2. Cálculos de Impacto GERAL ---
    # Nota: Vidas perdidas agora é a soma das vidas que as saintes tinham no trimestre ANTERIOR
    impacto_geral = {
        'Vidas_Ganhas': df_entrantes['NR_BENEF_T'].sum(),
        'Vidas_Perdidas': df_saintes['NR_BENEF_T'].sum(),
        'Receita_Ganha': df_entrantes['VL_SALDO_FINAL'].sum(),
        'Receita_Perdida': df_saintes['VL_SALDO_FINAL'].sum(),
    }
    impacto_geral['Saldo_Vidas'] = impacto_geral['Vidas_Ganhas'] - impacto_geral['Vidas_Perdidas']
    impacto_geral['Saldo_Receita'] = impacto_geral['Receita_Ganha'] - impacto_geral['Receita_Perdida']

    # --- 3. Cálculos de Impacto REDE UNIMED ---
    uni_entrou = df_entrantes[df_entrantes['Marca_Temp'] == 'UNIMED'].copy()
    uni_saiu = df_saintes[df_saintes['Marca_Temp'] == 'UNIMED'].copy()

    impacto_unimed = {
        'Vidas_Ganhas': uni_entrou['NR_BENEF_T'].sum(),
        'Vidas_Perdidas': uni_saiu['NR_BENEF_T'].sum(),
        'Receita_Ganha': uni_entrou['VL_SALDO_FINAL'].sum(),
        'Receita_Perdida': uni_saiu['VL_SALDO_FINAL'].sum(),
        'Qtd_Entrou': len(uni_entrou),
        'Qtd_Saiu': len(uni_saiu),
        'Entrantes_DF': uni_entrou,
        'Saintes_DF': uni_saiu
    }
    impacto_unimed['Saldo_Vidas'] = impacto_unimed['Vidas_Ganhas'] - impacto_unimed['Vidas_Perdidas']
    impacto_unimed['Saldo_Receita'] = impacto_unimed['Receita_Ganha'] - impacto_unimed['Receita_Perdida']

    return {
        'Geral': impacto_geral,
        'Unimed': impacto_unimed
    }