import logging
import sys
from backend.config import settings

def get_logger(name: str) -> logging.Logger:
    """
    Fábrica de Loggers configurada para o padrão do projeto.
    Formato: [DATA HORA] [NIVEL] [MODULO] - MENSAGEM
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Handler para Console (Stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatação profissional
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger