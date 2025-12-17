import sqlite3
import pandas as pd
import os
from configuracoes import DATABASE_PATH

class ConexaoSQLite:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.df_path = db_path
        self.validar_caminho()

    def validar_caminho(self):
        """ essa função tem como objetivo validar o caminho do banco, verificar se o arquivo .db existe
        """
        if not os.path.exists(self.df_path):
            raise FileNotFoundError(f"Banco de dados não encontrado:{self.df_path}")
    
    def executar_query(self, query_string:str, parametros:dict = None) -> pd.DataFrame:
        """ O unico objetivo dessa função é retornar uma consulta com base na query e parametros passados, 
        essa função ja abre e fecha a conexão com o banco
        """
        conn = None
        try:
            conn = sqlite3.connect(self.df_path)
            return pd.read_sql_query(query_string, conn, params= parametros)
        except Exception as e:
            print(f"Erro no SQLite: {e}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()
            