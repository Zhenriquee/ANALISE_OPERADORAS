import pandas as pd
from backend.processing.processor import DataProcessor

def test_normalizar_chaves():
    # Arrange (Preparação)
    df_input = pd.DataFrame({'registro': [123, '456.0', ' 789 ']})
    expected = ['000123', '000456', '000789']
    
    # Act (Ação)
    df_output = DataProcessor.normalizar_chaves(df_input, ['registro'])
    
    # Assert (Verificação)
    assert df_output['registro'].tolist() == expected

def test_calcular_kpis():
    # Arrange
    df_input = pd.DataFrame({
        'ID_OPERADORA': ['A', 'A'],
        'ID_TRIMESTRE': ['2023-T1', '2023-T2'],
        'NR_BENEF_T': [100, 200],      # Dobrou vidas
        'VL_SALDO_FINAL': [1000, 2000] # Dobrou receita
    })
    
    # Act
    df_output = DataProcessor.calcular_kpis(df_input)
    
    # Assert
    # Variação percentual deve ser 1.0 (100%) para o segundo registro
    assert df_output.iloc[1]['VAR_PCT_VIDAS'] == 1.0
    assert df_output.iloc[1]['CUSTO_POR_VIDA'] == 10.0 # 2000 / 200