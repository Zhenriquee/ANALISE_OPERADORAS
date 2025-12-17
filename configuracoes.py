import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FOLDER = os.path.join(BASE_DIR, 'data')
DB_NAME = 'dados_ans_paralela.db'
DATABASE_PATH = '/workspaces/ANALISE_OPERADORAS/data/base_ans_paralela.db'#os.path.join(DB_FOLDER, DB_NAME)

QUERIES_PATH = os.path.join(BASE_DIR, 'queries')

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)