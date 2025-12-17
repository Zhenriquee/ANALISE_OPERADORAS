import pandas as pd 
from backend.repository import AnsRepository

class FilterService:
    def __init__(self, repository:AnsRepository):
        self.repo = repository

    def get_todas_operadoras(self):
        """ esse metodo tem como objetivo retornar todas as operadoras disponiveis na base de dados
        as colunas são: registro operadora, cnpj, razao social e nome fantasia
        """
        df = self.repo.buscar_dados_brutos('/workspaces/ANALISE_OPERADORAS/queries/filtros/listar_todas_operadoras.sql')
        if df.empty:
            return pd.DataFrame()
        if 'nome_fantasia' in df.columns:
            df['nome_fantasia'] = df['nome_fantasia'].fillna(df['razao_social'])
        return df