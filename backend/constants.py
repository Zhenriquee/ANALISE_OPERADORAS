class Colunas:
    """Mapeamento centralizado de nomes de colunas"""
    # Identificadores
    ID_OPERADORA = "ID_OPERADORA"
    REGISTRO_ANS = "registro_operadora"
    CD_OPERADORA = "CD_OPERADO"
    REG_ANS_FIN = "REG_ANS"
    TRIMESTRE = "ID_TRIMESTRE"
    
    # Dimensões
    RAZAO_SOCIAL = "razao_social"
    CNPJ = "cnpj"
    UF = "uf"
    CIDADE = "cidade"
    MODALIDADE = "modalidade"
    REPRESENTANTE = "representante"
    CARGO_REP = "cargo_representante"
    DATA_REGISTRO = "Data_Registro_ANS"
    
    # Métricas
    VIDAS = "NR_BENEF_T"
    RECEITA = "VL_SALDO_FINAL"
    
    # KPIs Calculados
    VAR_VIDAS = "VAR_PCT_VIDAS"
    VAR_RECEITA = "VAR_PCT_RECEITA"
    CUSTO_VIDA = "CUSTO_POR_VIDA"

class Negocio:
    """Regras de Negócio Globais"""
    DATA_CORTE_INICIO = "2012-T1"