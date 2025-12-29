import pandas as pd
import os

# --- CONFIGURAÇÃO E CARREGAMENTO AUTOMÁTICO ---
# Define o nome do arquivo (deve estar na raiz do projeto, onde fica o app.py)
ARQUIVO_LISTA_UNIMED = 'rede_unimed.txt'

def _inicializar_lista_unimed():
    """
    Função interna que lê o arquivo .txt e retorna um conjunto (set) de registros ANS.
    É executada automaticamente ao importar este arquivo.
    """
    lista_registros = set()
    
    # Verifica se o arquivo existe para evitar erros
    if os.path.exists(ARQUIVO_LISTA_UNIMED):
        try:
            with open(ARQUIVO_LISTA_UNIMED, 'r', encoding='utf-8') as f:
                # Cria um SET com os números limpos (remove espaços e quebras de linha)
                lista_registros = {linha.strip() for linha in f if linha.strip()}
            print(f"Sucesso: {len(lista_registros)} exceções Unimed carregadas.")
        except Exception as e:
            print(f"Erro ao ler '{ARQUIVO_LISTA_UNIMED}': {e}")
    else:
        print(f"Aviso: Arquivo '{ARQUIVO_LISTA_UNIMED}' não encontrado. Regra de lista ignorada.")
        
    return lista_registros

# --- CACHE GLOBAL ---
# Esta variável é carregada apenas UMA vez quando o sistema inicia.
# A função extrair_marca vai consultar ela diretamente.
_CACHE_REDE_UNIMED = _inicializar_lista_unimed()


# --- FUNÇÕES PRINCIPAIS ---

def extrair_marca(razao_social, registro_ans):
    """
    Normaliza a Marca/Grupo Econômico.
    Argumentos:
      - razao_social: Nome da operadora (str)
      - registro_ans: Código ANS (str ou int)
      
    Nota: A lista de exceção é lida da variável global _CACHE_REDE_UNIMED.
    """
    
    # 1. Validação Prioritária: Registro ANS na Lista Carregada
    # Converte para string para garantir a comparação correta
    ans_str = str(registro_ans).strip()
    
    if ans_str in _CACHE_REDE_UNIMED:
        return "UNIMED"

    # Tratamento de Nulos
    if pd.isna(razao_social): return "OUTROS"
    
    nome = razao_social.strip().upper()
    
    # 2. Validação Secundária: Prefixo do Nome
    if nome.startswith("UNIMED"): return "UNIMED"
    
    # 3. Demais Grupos (Regras Padrão)
    if nome.startswith("BRADESCO"): return "BRADESCO"
    if nome.startswith("AMIL"): return "AMIL"
    if nome.startswith("SUL AMERICA") or nome.startswith("SULAMERICA"): return "SULAMERICA"
    if nome.startswith("HAPVIDA"): return "HAPVIDA"
    if nome.startswith("NOTRE DAME") or nome.startswith("NOTREDAME") or nome.startswith("GNDI"): return "NOTREDAME"
    if nome.startswith("GOLDEN CROSS"): return "GOLDEN CROSS"
    if nome.startswith("PORTO SEGURO"): return "PORTO SEGURO"
    
    # Regra Geral: Primeira palavra
    primeira_palavra = nome.split()[0].replace("-", "")
    return primeira_palavra

def analisar_performance_marca(df_trimestre, operadora_row):
    """
    Retorna estatísticas comparativas do grupo.
    """
    # Identifica a marca da operadora selecionada
    marca = extrair_marca(operadora_row['razao_social'], operadora_row['ID_OPERADORA'])
    
    # Cria cópia para cálculo
    df_calc = df_trimestre.copy()
    
    # Aplica a função para todas as linhas do dataframe
    df_calc['Marca_Temp'] = df_calc.apply(
        lambda row: extrair_marca(row['razao_social'], row['ID_OPERADORA']), 
        axis=1
    )
    
    # Filtra o grupo
    df_grupo = df_calc[df_calc['Marca_Temp'] == marca].copy()
    
    total_vidas_grupo = df_grupo['NR_BENEF_T'].sum()
    
    # Share of Brand
    vidas_op = operadora_row['NR_BENEF_T']
    share_of_brand = (vidas_op / total_vidas_grupo) * 100 if total_vidas_grupo > 0 else 0
    
    return {
        'Marca': marca,
        'Qtd_Grupo': len(df_grupo),
        'Share_of_Brand': share_of_brand,
        'Media_Cresc_Vidas_Grupo': df_grupo['VAR_PCT_VIDAS'].median(),
        'Media_Cresc_Receita_Grupo': df_grupo['VAR_PCT_RECEITA'].median(),
        'Df_Grupo': df_grupo 
    }