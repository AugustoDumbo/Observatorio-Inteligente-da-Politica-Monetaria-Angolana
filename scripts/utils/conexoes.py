import psycopg2
from minio import Minio
import logging
import socket
from config.settings import MINIO_CONFIG, BUCKETS
from config.local_settings import (
    TIMESCALE_HOST, TIMESCALE_PORT, TIMESCALE_DB, 
    TIMESCALE_USER, TIMESCALE_PASSWORD, TIMESCALE_CONN_STRING
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexaoPostgres:
    """Gerenciador de conexão com TimescaleDB Cloud"""
    
    def __init__(self):
        self.conn_params = {
            'host': TIMESCALE_HOST,
            'port': TIMESCALE_PORT,
            'database': TIMESCALE_DB,
            'user': TIMESCALE_USER,
            'password': TIMESCALE_PASSWORD,
            'sslmode': 'require',
            'connect_timeout': 10  # Timeout de 10 segundos
        }
    
    def verificar_dns(self):
        """Verifica se o host é alcançável"""
        try:
            socket.gethostbyname(self.conn_params['host'])
            logger.info(f"✅ DNS resolvido: {self.conn_params['host']}")
            return True
        except socket.gaierror as e:
            logger.error(f"❌ Erro DNS: {e}")
            return False
    
    def conectar(self):
        """Estabelece conexão com timeout"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            logger.info("✅ Conectado ao TimescaleDB Cloud")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro de conexão (timeout/autenticação): {e}")
            logger.info("💡 Verifique se o serviço está ativo no Timescale Cloud Console")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            raise
    
    def testar_conexao(self):
        """Teste completo de conectividade"""
        logger.info(f"🔍 Testando conexão com: {self.conn_params['host']}")
        
        # 1. Testa DNS
        if not self.verificar_dns():
            return False
        
        # 2. Testa conexão
        try:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"✅ Versão PostgreSQL: {version[0]}")
            
            # Testa se TimescaleDB está instalado
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname='timescaledb';")
            tsdb = cur.fetchone()
            if tsdb:
                logger.info(f"✅ TimescaleDB {tsdb[1]} instalado")
            
            cur.close()
            conn.close()
            return True
        except Exception:
            return False

class ConexaoMinio:
    """Gerenciador de conexão com MinIO"""
    
    def __init__(self):
        self.client = Minio(
            endpoint=MINIO_CONFIG['endpoint'],
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['secure']
        )
        
    def criar_buckets(self):
        """Cria os buckets necessários se não existirem"""
        for bucket_name in BUCKETS.values():
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logger.info(f"✅ Bucket '{bucket_name}' criado")
                else:
                    logger.info(f"ℹ️ Bucket '{bucket_name}' já existe")
            except Exception as e:
                logger.error(f"❌ Erro ao criar bucket {bucket_name}: {e}")
    
    def testar_conexao(self):
        """Testa conexão com MinIO"""
        try:
            buckets = self.client.list_buckets()
            logger.info(f"✅ Conectado ao MinIO. {len(buckets)} buckets encontrados")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao MinIO: {e}")
            return False
