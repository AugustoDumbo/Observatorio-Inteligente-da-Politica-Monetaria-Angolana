"""
Configurações locais que NÃO vão para o git
Copie este arquivo como .env na raiz do projeto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# ===== TIMESCALE CLOUD =====
TIMESCALE_HOST = os.getenv('TIMESCALE_HOST', 'iga9aocw54.pdvvijvwbr.tsdb.cloud.timescale.com')
TIMESCALE_PORT = int(os.getenv('TIMESCALE_PORT', '31664'))
TIMESCALE_DB = os.getenv('TIMESCALE_DB', 'tsdb')
TIMESCALE_USER = os.getenv('TIMESCALE_USER', 'tsdbadmin')
TIMESCALE_PASSWORD = os.getenv('TIMESCALE_PASSWORD', 'wenvap0mxeoqp19a')

# Monta a string de conexão
TIMESCALE_CONN_STRING = f"postgresql://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:{TIMESCALE_PORT}/{TIMESCALE_DB}?sslmode=require"
