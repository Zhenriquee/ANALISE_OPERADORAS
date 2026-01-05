import pandera.pandas as pa
from pandera.typing import Series

class SchemaMestre(pa.DataFrameModel):
    """
    Contrato de Dados para o Dataset Mestre (Gold Layer).
    Garante que o dashboard receba exatamente o que espera.
    Refatorado para Pandera >= 0.20.0
    """
    # Chaves e Identificadores
    ID_TRIMESTRE: Series[str] = pa.Field(coerce=True)
    ID_OPERADORA: Series[str] = pa.Field(str_length=6, coerce=True)
    
    # Dimensões
    razao_social: Series[str] = pa.Field(nullable=True)
    cidade: Series[str] = pa.Field(nullable=True)
    # Lista atualizada de UFs válidas
    uf: Series[str] = pa.Field(
        isin=['SP', 'RJ', 'MG', 'ES', 'RS', 'SC', 'PR', 'BA', 'PE', 
              'CE', 'DF', 'GO', 'MT', 'MS', 'AM', 'PA', 'RO', 'RR', 
              'AP', 'TO', 'MA', 'PI', 'RN', 'PB', 'AL', 'SE', 'AC'], 
        nullable=True
    )
    modalidade: Series[str] = pa.Field(nullable=True)
    
    # Métricas Críticas
    NR_BENEF_T: Series[int] = pa.Field(ge=0, coerce=True)
    VL_SALDO_FINAL: Series[float] = pa.Field(coerce=True)
    
    # KPIs Calculados
    CUSTO_POR_VIDA: Series[float] = pa.Field(nullable=True)

    class Config:
        strict = False # Permite colunas extras, mas valida as declaradas acima