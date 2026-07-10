"""
Script para validar toda a infraestrutura antes de começar
Execute de dentro da pasta observatorio_monetario_angola:
python tests/testar_infra.py
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.conexoes import ConexaoPostgres, ConexaoMinio
from config.settings import MINIO_CONFIG, POSTGRES_CONFIG
import requests

def testar_airflow():
    """Testa se o Airflow está respondendo"""
    try:
        response = requests.get('http://localhost:8082/health')
        if response.status_code == 200:
            print("✅ Airflow 2.10.4 rodando na porta 8082")
            return True
    except Exception as e:
        print(f"❌ Airflow não está respondendo: {e}")
        return False

def testar_minio():
    """Testa conexão com MinIO"""
    try:
        minio = ConexaoMinio()
        if minio.testar_conexao():
            minio.criar_buckets()
            return True
    except Exception as e:
        print(f"❌ Erro MinIO: {e}")
        return False

def testar_postgres():
    """Testa conexão com PostgreSQL"""
    try:
        pg = ConexaoPostgres()
        return pg.testar_conexao()
    except Exception as e:
        print(f"❌ Erro PostgreSQL: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 TESTANDO INFRAESTRUTURA DO OBSERVATÓRIO MONETÁRIO")
    print("=" * 60)
    print(f"📁 Diretório atual: {Path.cwd()}")
    print(f"📁 Script location: {Path(__file__).parent}")
    print()
    
    resultados = {
        "Airflow": testar_airflow(),
        "MinIO": testar_minio(),
        "PostgreSQL/TimescaleDB": testar_postgres()
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    for servico, status in resultados.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {servico}: {'OK' if status else 'FALHA'}")
    
    if all(resultados.values()):
        print("\n🚀 Infraestrutura pronta! Podemos começar a ingestão de dados.")
    else:
        print("\n⚠️ Alguns serviços precisam de atenção antes de prosseguir.")

if __name__ == "__main__":
    main()
