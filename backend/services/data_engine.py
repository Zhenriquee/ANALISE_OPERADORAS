import pandas as pd
from infra.db_connector import ConexaoSQLite
from backend.repository import AnsRepository
from backend.config import settings
from backend.processing.processor import DataProcessor
from backend.logger import get_logger
from backend.contracts import SchemaMestre
from backend.constants import Colunas, Negocio

logger = get_logger(__name__)

class DataEngine:
    def __init__(self):
        # 1. Infraestrutura (Conexão) - Agora usa settings.DB_PATH
        # Idealmente, injetaríamos isso no __init__, mas manteremos assim por enquanto
        self.connector = ConexaoSQLite(str(settings.DB_PATH))
        
        # 2. Repositório (Acesso a Dados)
        self.repository = AnsRepository(self.connector, str(settings.QUERIES_DIR))
        
        # 3. Processador (Lógica de Transformação)
        self.processor = DataProcessor()

    def _extrair_dados(self):
        """Etapa de Extração (Bronze Layer)"""
        logger.info(f"Iniciando extração de dados (Corte: {settings.DATA_CORTE_INICIO})...")
        
        # Parâmetro para injetar nas queries
        params = (settings.DATA_CORTE_INICIO,)
        
        return (
            self.repository.buscar_dados_brutos("etl/load_dim_operadoras.sql"),
            self.repository.buscar_dados_brutos("etl/load_beneficiarios.sql", params),
            self.repository.buscar_dados_brutos("etl/load_financeiro.sql", params)
        )
    def gerar_dataset_mestre(self):
        """
        Pipeline ETL Principal Otimizado
        """
        # 1. Extração Otimizada
        df_dim, df_ben, df_fin = self._extrair_dados()
        
        if df_dim.empty: 
            logger.warning("Dimensão de operadoras vazia. Abortando.")
            return pd.DataFrame()

        logger.info("Normalizando chaves e consolidando dados...")

        # 2. Transformação Silver (Normalização)
        df_dim = self.processor.normalizar_chaves(df_dim, [Colunas.REGISTRO_ANS])
        df_ben = self.processor.normalizar_chaves(df_ben, [Colunas.CD_OPERADORA])
        df_fin = self.processor.normalizar_chaves(df_fin, [Colunas.REG_ANS_FIN])

        # [REMOVIDO] df_ben = self.processor.aplicar_filtro_temporal(...) 
        # Motivo: O SQL já realizou essa filtragem, economizando memória.

        # 3. Transformação Gold (Consolidação)
        # 3. Transformação Gold (Consolidação)
        df_mestre = pd.merge(
            df_ben, df_fin,
            left_on=[Colunas.CD_OPERADORA, Colunas.TRIMESTRE],
            right_on=[Colunas.REG_ANS_FIN, Colunas.TRIMESTRE],
            how='outer'
        )

        # Tratamento de Nulos (Coalesce)
        df_mestre[Colunas.ID_OPERADORA] = df_mestre[Colunas.CD_OPERADORA].fillna(df_mestre[Colunas.REG_ANS_FIN])
        df_mestre[Colunas.VIDAS] = df_mestre[Colunas.VIDAS].fillna(0)
        df_mestre[Colunas.RECEITA] = df_mestre[Colunas.RECEITA].fillna(0)

        # Enriquecimento
        df_final = self.processor.enriquecer_dataset(df_mestre, df_dim)

        # 4. KPIs
        df_final = self.processor.calcular_kpis(df_final)

        # Seleção Final de Colunas
        cols_desejadas = [
            Colunas.TRIMESTRE, Colunas.ID_OPERADORA, Colunas.RAZAO_SOCIAL, 
            Colunas.CNPJ, Colunas.UF, Colunas.MODALIDADE, Colunas.CIDADE,
            Colunas.VIDAS, Colunas.RECEITA, 
            Colunas.VAR_VIDAS, Colunas.VAR_RECEITA, Colunas.CUSTO_VIDA
        ]
        
        # Interseção segura de colunas
        cols_existentes = [c for c in cols_desejadas if c in df_final.columns]
        df_final = df_final[cols_existentes]

        # Validação de Contrato
        try:
            logger.info("Validando contrato de dados...")
            SchemaMestre.validate(df_final, lazy=True)
            logger.info("Dados validados com sucesso.")
        except Exception as e:
            logger.error(f"Violação de Schema: {e}")

        return df_final