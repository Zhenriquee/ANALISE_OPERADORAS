import pandas as pd
import numpy as np
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
    ids_novos = ids_ref - ids_comp      # Entrantes
    ids_excluidos = ids_comp - ids_ref  # Saintes
    
    # 4. Recuperar dados detalhados
    df_entrantes = df_ref[df_ref['ID_OPERADORA'].isin(ids_novos)].copy()
    df_saintes = df_comp[df_comp['ID_OPERADORA'].isin(ids_excluidos)].copy()
    
    return df_entrantes, df_saintes

def gerar_analise_impacto(df_entrantes, df_saintes):
    """
    Calcula o impacto financeiro, de vidas e segmenta para Mercado e Unimed.
    """
    # --- Função Auxiliar Local para Porcentagem ---
    def _calc_pct(ganho, perda):
        if perda == 0:
            return 1.0 if ganho > 0 else 0.0 # Se não perdeu nada e ganhou, é 100% (ou infinito)
        return (ganho - perda) / perda

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
    ganho_vidas = df_entrantes['NR_BENEF_T'].sum()
    perda_vidas = df_saintes['NR_BENEF_T'].sum()
    
    ganho_rec = df_entrantes['VL_SALDO_FINAL'].sum()
    perda_rec = df_saintes['VL_SALDO_FINAL'].sum()

    impacto_geral = {
        'Vidas_Ganhas': ganho_vidas,
        'Vidas_Perdidas': perda_vidas,
        'Receita_Ganha': ganho_rec,
        'Receita_Perdida': perda_rec,
        'Saldo_Vidas': ganho_vidas - perda_vidas,
        'Saldo_Receita': ganho_rec - perda_rec,
        # Novos campos percentuais
        'Pct_Saldo_Vidas': _calc_pct(ganho_vidas, perda_vidas),
        'Pct_Saldo_Receita': _calc_pct(ganho_rec, perda_rec)
    }

    # --- 3. Cálculos de Impacto REDE UNIMED ---
    uni_entrou = df_entrantes[df_entrantes['Marca_Temp'] == 'UNIMED'].copy()
    uni_saiu = df_saintes[df_saintes['Marca_Temp'] == 'UNIMED'].copy()

    uv_ganho = uni_entrou['NR_BENEF_T'].sum()
    uv_perda = uni_saiu['NR_BENEF_T'].sum()
    ur_ganho = uni_entrou['VL_SALDO_FINAL'].sum()
    ur_perda = uni_saiu['VL_SALDO_FINAL'].sum()

    impacto_unimed = {
        'Vidas_Ganhas': uv_ganho,
        'Vidas_Perdidas': uv_perda,
        'Receita_Ganha': ur_ganho,
        'Receita_Perdida': ur_perda,
        'Qtd_Entrou': len(uni_entrou),
        'Qtd_Saiu': len(uni_saiu),
        'Entrantes_DF': uni_entrou,
        'Saintes_DF': uni_saiu,
        'Saldo_Vidas': uv_ganho - uv_perda,
        'Saldo_Receita': ur_ganho - ur_perda,
        # Novos campos percentuais
        'Pct_Saldo_Vidas': _calc_pct(uv_ganho, uv_perda),
        'Pct_Saldo_Receita': _calc_pct(ur_ganho, ur_perda)
    }

    return {
        'Geral': impacto_geral,
        'Unimed': impacto_unimed
    }