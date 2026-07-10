# Configurações globais do projeto
import os
from datetime import datetime
from pathlib import Path

# ===== DIRETÓRIOS BASE =====
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

# ===== CONEXÃO POSTGRESQL (TimescaleDB) =====
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5434)),
    'database': os.getenv('POSTGRES_DB', 'observatorio'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'sslmode': 'require'
}

# ===== CONEXÃO MINIO =====
MINIO_CONFIG = {
    'endpoint': os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
    'access_key': os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    'secret_key': os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
    'secure': False  # True se usar HTTPS
}

# ===== BUCKETS MINIO =====
BUCKETS = {
    'raw': 'raw-data',
    'processed': 'processed-data',
    'curated': 'curated-data',
    'models': 'ml-models'
}

# ===== FONTES DE DADOS =====
FONTES = {
    'bna': {
        'base_url': 'https://www.bna.ao',
        'apis': {
            'taxas_cambio': '/api/taxas-cambio',
            'taxa_diretora': '/api/taxa-bna'
        }
    },
    'ine': {
        'base_url': 'https://www.ine.gov.ao',
        'endpoints': {
            'ipc': '/estatisticas/ipc'
        }
    },
    'internacional': {
        'fred_api_key': os.getenv('FRED_API_KEY', ''),
        'worldbank_api': 'https://api.worldbank.org/v2'
    }
}
