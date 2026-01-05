import sqlite3
import pandas as pd
import logging
from typing import Optional

# Configuração de Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexaoSQLite:
    """
    Gerenciador de Conexão SQLite.
    Princípio: Ignorância de Configuração.
    Esta classe não importa 'settings' ou 'config'. Ela apenas recebe o caminho no __init__.
    """
    
    def __init__(self, db_path: str):
        """
        Args:
            db_path (str): Caminho absoluto ou relativo para o arquivo .db.
                           Obrigatório passar explicitamente.
        """
        self.db_name = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def __enter__(self):
        """Context Manager: Abre conexão ao usar 'with'"""
        self._conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Fecha conexão ao sair"""
        self._desconectar()

    def _conectar(self):
        """Estabelece a conexão se não existir"""
        if not self.connection:
            try:
                self.connection = sqlite3.connect(self.db_name)
            except sqlite3.Error as e:
                logger.error(f"Erro de conexão SQLite no caminho '{self.db_name}': {e}")
                raise

    def _desconectar(self):
        """Fecha a conexão com segurança"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def executar_query(self, query: str, parametros: tuple = None) -> pd.DataFrame:
        """
        Executa uma query SQL e retorna diretamente um Pandas DataFrame.
        """
        self._conectar()
        
        try:
            # Pandas read_sql já trata a conversão e nomes de colunas
            return pd.read_sql(query, self.connection, params=parametros)
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            return pd.DataFrame() # Fail Gracefully
            
    def executar_comando(self, sql: str, parametros: tuple = None) -> None:
        """
        Para comandos que NÃO retornam dados (INSERT, UPDATE, DELETE, CREATE).
        """
        self._conectar()
        try:
            cursor = self.connection.cursor()
            if parametros:
                cursor.execute(sql, parametros)
            else:
                cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Erro ao executar comando: {e}")
            raise