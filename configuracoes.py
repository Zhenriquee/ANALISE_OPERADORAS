import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define o caminho da pasta de dados
DB_FOLDER = os.path.join(BASE_DIR, 'data')

DB_NAME = 'base_ans_paralela.db' 

# 4. Constrói o caminho absoluto correto para o banco
DATABASE_PATH = os.path.join(DB_FOLDER, DB_NAME)

# 5. Define o caminho das queries
QUERIES_PATH = os.path.join(BASE_DIR, 'queries')

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)