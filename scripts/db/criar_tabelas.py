"""
Criação das tabelas principais no TimescaleDB
Execute: python scripts/db/criar_tabelas.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from scripts.utils.conexoes import ConexaoPostgres
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def criar_schema_raw():
    """Schema para dados brutos (camada raw)"""
    return """
    -- Schema para dados monetários e econômicos
    CREATE SCHEMA IF NOT EXISTS raw;
    
    -- Tabela de taxas de câmbio (série temporal)
    CREATE TABLE IF NOT EXISTS raw.taxas_cambio (
        timestamp TIMESTAMPTZ NOT NULL,
        moeda VARCHAR(10) NOT NULL,
        valor_compra DECIMAL(10,4),
        valor_venda DECIMAL(10,4),
        fonte VARCHAR(50) DEFAULT 'BNA',
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (timestamp, moeda)
    );
    
    -- Tabela de taxas de juro
    CREATE TABLE IF NOT EXISTS raw.taxas_juro (
        timestamp TIMESTAMPTZ NOT NULL,
        taxa_bna DECIMAL(5,2),
        taxa_luibor_overnight DECIMAL(5,2),
        taxa_facilidade_permanente DECIMAL(5,2),
        fonte VARCHAR(50) DEFAULT 'BNA',
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (timestamp)
    );
    
    -- Tabela de agregados monetários
    CREATE TABLE IF NOT EXISTS raw.agregados_monetarios (
        timestamp TIMESTAMPTZ NOT NULL,
        m2 DECIMAL(15,2),
        m3 DECIMAL(15,2),
        base_monetaria DECIMAL(15,2),
        reservas_internacionais DECIMAL(15,2),
        unidade VARCHAR(10) DEFAULT 'milhoes_aoa',
        fonte VARCHAR(50) DEFAULT 'BNA',
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (timestamp)
    );
    
    -- Tabela de IPC (Índice de Preços no Consumidor)
    CREATE TABLE IF NOT EXISTS raw.ipc (
        timestamp TIMESTAMPTZ NOT NULL,
        ipc_geral DECIMAL(5,2),
        ipc_alimentacao DECIMAL(5,2),
        ipc_transportes DECIMAL(5,2),
        ipc_saude DECIMAL(5,2),
        ipc_habitacao DECIMAL(5,2),
        provincia VARCHAR(50) DEFAULT 'Nacional',
        fonte VARCHAR(50) DEFAULT 'INE',
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (timestamp, provincia)
    );
    
    -- Tabela de preços internacionais
    CREATE TABLE IF NOT EXISTS raw.precos_internacionais (
        timestamp TIMESTAMPTZ NOT NULL,
        brent_crude DECIMAL(10,2),
        federal_funds_rate DECIMAL(5,2),
        inflacao_global DECIMAL(5,2),
        fonte VARCHAR(50) DEFAULT 'FRED/WorldBank',
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (timestamp)
    );
    
    -- Tabela de notícias e comunicados (texto)
    CREATE TABLE IF NOT EXISTS raw.noticias (
        id SERIAL,
        timestamp TIMESTAMPTZ NOT NULL,
        titulo TEXT NOT NULL,
        conteudo TEXT,
        url_original TEXT,
        fonte VARCHAR(50),
        categoria VARCHAR(50),
        data_carga TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (id, timestamp)
    );
    """
    
def criar_hypertables():
    """Converte tabelas em hypertables do TimescaleDB"""
    return """
    -- Converte tabelas de série temporal em hypertables
    SELECT create_hypertable('raw.taxas_cambio', 'timestamp', if_not_exists => TRUE);
    SELECT create_hypertable('raw.taxas_juro', 'timestamp', if_not_exists => TRUE);
    SELECT create_hypertable('raw.agregados_monetarios', 'timestamp', if_not_exists => TRUE);
    SELECT create_hypertable('raw.ipc', 'timestamp', if_not_exists => TRUE);
    SELECT create_hypertable('raw.precos_internacionais', 'timestamp', if_not_exists => TRUE);
    SELECT create_hypertable('raw.noticias', 'timestamp', if_not_exists => TRUE);
    """
    
def criar_indices():
    """Cria índices para otimizar consultas"""
    return """
    -- Índices para consultas frequentes
    CREATE INDEX IF NOT EXISTS idx_taxas_cambio_moeda ON raw.taxas_cambio (moeda, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_ipc_provincia ON raw.ipc (provincia, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_noticias_fonte ON raw.noticias (fonte, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON raw.noticias (categoria, timestamp DESC);
    """
    
def main():
    logger.info("🏗️ Iniciando criação do schema do banco de dados...")
    
    try:
        pg = ConexaoPostgres()
        conn = pg.conectar()
        cur = conn.cursor()
        
        # 1. Criar tabelas
        logger.info("📊 Criando tabelas...")
        cur.execute(criar_schema_raw())
        
        # 2. Criar extensão TimescaleDB se necessário
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        logger.info("✅ Extensão TimescaleDB verificada")
        
        # 3. Converter para hypertables
        logger.info("⚡ Configurando hypertables...")
        cur.execute(criar_hypertables())
        
        # 4. Criar índices
        logger.info("🔍 Criando índices...")
        cur.execute(criar_indices())
        
        conn.commit()
        
        # 5. Verificar tabelas criadas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'raw'
            ORDER BY table_name;
        """)
        tabelas = cur.fetchall()
        
        logger.info(f"✅ {len(tabelas)} tabelas criadas com sucesso:")
        for tabela in tabelas:
            logger.info(f"   - raw.{tabela[0]}")
        
        cur.close()
        conn.close()
        logger.info("🚀 Schema do banco de dados criado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar schema: {e}")
        raise

if __name__ == "__main__":
    main()
