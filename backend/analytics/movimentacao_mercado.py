import pandas as pd

def calcular_fluxo_entrada_saida(df_mestre, trimestre_ref, trimestre_comp):
    """
    Identifica operadoras que entraram e saíram do mercado entre dois trimestres.
    
    Args:
        df_mestre (pd.DataFrame): Dataset completo.
        trimestre_ref (str): Trimestre de Referência (ex: "202401").
        trimestre_comp (str): Trimestre de Comparação (ex: "202304").
        
    Returns:
        tuple: (df_entrantes, df_saintes)
    """
    # 1. Filtrar os dados dos dois períodos
    df_ref = df_mestre[df_mestre['ID_TRIMESTRE'] == trimestre_ref]
    df_comp = df_mestre[df_mestre['ID_TRIMESTRE'] == trimestre_comp]
    
    # 2. Extrair conjuntos de IDs únicos
    ids_ref = set(df_ref['ID_OPERADORA'].unique())
    ids_comp = set(df_comp['ID_OPERADORA'].unique())
    
    # 3. Calcular Diferenças (Matemática de Conjuntos)
    
    # Entrantes: Estão na Referência (B), mas não estavam na Comparação (A)
    ids_novos = ids_ref - ids_comp
    
    # Saintes: Estavam na Comparação (A), mas não estão na Referência (B)
    ids_excluidos = ids_comp - ids_ref
    
    # 4. Recuperar dados detalhados para exibição
    
    # Para quem entrou, pegamos os dados atuais (Ref)
    df_entrantes = df_ref[df_ref['ID_OPERADORA'].isin(ids_novos)].copy()
    
    # Para quem saiu, pegamos os últimos dados vistos (Comp) para saber o tamanho de quem perdemos
    df_saintes = df_comp[df_comp['ID_OPERADORA'].isin(ids_excluidos)].copy()
    
    return df_entrantes, df_saintes