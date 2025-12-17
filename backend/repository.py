import os
import pandas as pd
from infra.db_connector import ConexaoSQLite

class AnsRepository:
    def __init__(self, connector: ConexaoSQLite, queries_path:str):
        self.connector = connector
        self.queries_path = queries_path

    def _ler_arquivo_sql(self, nome_arquivo:str) -> str:
        caminho = os.path.join(self.queries_path, nome_arquivo)
        with open (caminho,'r', encoding='utf-8') as f:
            return f.read()

    def buscar_dados_brutos(self, nome_query: str, parametros: dict = None) -> pd.DataFrame:
        """Busca o SQL pelo nome e manda a execução para o connector
        """
        sql = self._ler_arquivo_sql(nome_arquivo=nome_query)
        return self.connector.executar_query(sql, parametros=parametros)
        