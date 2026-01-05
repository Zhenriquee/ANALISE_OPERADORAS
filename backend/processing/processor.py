import pandas as pd
import numpy as np
from backend.constants import Colunas

class DataProcessor:
    """
    Responsável pela transformação pura dos dados (Pandas).
    Camada Silver (Limpeza) e Gold (Regras de Negócio/KPIs).
    """

    @staticmethod
    def normalizar_chaves(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
        """Padroniza chaves (ex: Registro ANS) para 6 dígitos string."""
        if df.empty:
            return df
            
        def _normalizar(valor):
            return str(valor).split('.')[0].strip().zfill(6)

        for col in colunas:
            if col in df.columns:
                df[col] = df[col].apply(_normalizar)
        return df

    @staticmethod
    def aplicar_filtro_temporal(df: pd.DataFrame, coluna_tempo: str, data_corte: str) -> pd.DataFrame:
        if df.empty or coluna_tempo not in df.columns:
            return df
        return df[df[coluna_tempo] >= data_corte]

    @staticmethod
    def enriquecer_dataset(df_mestre: pd.DataFrame, df_dimensao: pd.DataFrame) -> pd.DataFrame:
        """Realiza os Joins para criar a Tabela OBT (One Big Table)."""
        # Join de Enriquecimento
        df_final = pd.merge(
            df_mestre,
            df_dimensao,
            left_on='ID_OPERADORA',
            right_on='registro_operadora',
            how='left'
        )
        return df_final

    @staticmethod
    def calcular_kpis(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
            
        df = df.sort_values([Colunas.ID_OPERADORA, Colunas.TRIMESTRE])
        
        # Variações
        df[Colunas.VAR_VIDAS] = df.groupby(Colunas.ID_OPERADORA)[Colunas.VIDAS].pct_change().fillna(0)
        df[Colunas.VAR_RECEITA] = df.groupby(Colunas.ID_OPERADORA)[Colunas.RECEITA].pct_change().fillna(0)

        # KPI Composto
        df[Colunas.CUSTO_VIDA] = np.where(
            df[Colunas.VIDAS] > 0, 
            df[Colunas.RECEITA] / df[Colunas.VIDAS], 
            0
        )
        return df