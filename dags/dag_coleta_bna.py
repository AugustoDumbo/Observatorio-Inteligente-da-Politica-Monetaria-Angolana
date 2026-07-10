"""
DAG: Coleta de Dados do BNA
Frequência: Mensal (dia 1 de cada mês)
Responsável: Observatório Monetário Angolano
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.task_group import TaskGroup
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ingestao.coletor_bna import ColetorBNA
from scripts.utils.conexoes import ConexaoPostgres
import logging

logger = logging.getLogger(__name__)

# Argumentos padrão
default_args = {
    'owner': 'observatorio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['admin@observatorio.ao'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30)
}

def verificar_conexoes():
    """Verifica se todas as conexões estão OK antes de começar"""
    logger.info("🔍 Verificando conexões...")
    pg = ConexaoPostgres()
    if pg.testar_conexao():
        logger.info("✅ Conexão com TimescaleDB OK")
        return True
    raise Exception("❌ Falha na conexão com TimescaleDB")

def coletar_dados_bna(**context):
    """Coleta dados do BNA e salva no banco"""
    logger.info("🏦 Iniciando coleta programada do BNA...")
    
    coletor = ColetorBNA()
    dados = coletor.executar()
    
    # Armazena informações para próxima task
    context['task_instance'].xcom_push(
        key='registros_bna',
        value={
            'timestamp': datetime.now().isoformat(),
            'registros': len(dados),
            'periodo': f"{dados['data'].min()} a {dados['data'].max()}"
        }
    )
    
    logger.info(f"✅ Coleta concluída: {len(dados)} registros processados")
    return len(dados)

def validar_dados(**context):
    """Valida os dados recém-inseridos"""
    logger.info("🔍 Validando dados inseridos...")
    
    pg = ConexaoPostgres()
    conn = pg.conectar()
    cur = conn.cursor()
    
    # Verifica se há dados do mês atual
    cur.execute("""
        SELECT COUNT(*) 
        FROM raw.taxas_cambio 
        WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', NOW());
    """)
    count = cur.fetchone()[0]
    
    if count > 0:
        logger.info(f"✅ Validação OK: {count} registros do mês atual")
        cur.close()
        conn.close()
        return True
    else:
        logger.warning("⚠️ Nenhum registro encontrado para o mês atual")
        cur.close()
        conn.close()
        return False

def criar_backup_minio(**context):
    """Faz backup dos dados no MinIO"""
    logger.info("💾 Criando backup no MinIO...")
    
    import pandas as pd
    from minio import Minio
    from io import BytesIO
    from scripts.utils.conexoes import ConexaoPostgres, ConexaoMinio
    
    # Conectar ao banco
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    # Exportar dados para CSV
    query = "SELECT * FROM raw.taxas_cambio ORDER BY timestamp DESC;"
    df = pd.read_sql(query, conn)
    
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Salvar no MinIO
    minio_client = ConexaoMinio()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    object_name = f'bna/taxas_cambio_{timestamp}.csv'
    
    minio_client.client.put_object(
        bucket_name='raw-data',
        object_name=object_name,
        data=csv_buffer,
        length=csv_buffer.getbuffer().nbytes,
        content_type='text/csv'
    )
    
    logger.info(f"✅ Backup criado: {object_name}")
    conn.close()
    return object_name

# Definição da DAG
with DAG(
    dag_id='coleta_bna_mensal',
    default_args=default_args,
    description='Coleta mensal de dados do BNA para o Observatório Monetário',
    schedule_interval='0 8 1 * *',  # 8h do dia 1 de cada mês
    catchup=False,
    max_active_runs=1,
    tags=['bna', 'coleta', 'mensal'],
    doc_md='''
    # DAG de Coleta BNA
    
    Pipeline de coleta de dados do Banco Nacional de Angola.
    
    ## Tarefas:
    1. Verificar conexões
    2. Coletar dados (taxas câmbio, juros, agregados)
    3. Validar dados
    4. Criar backup no MinIO
    '''
) as dag:
    
    # Tarefa 1: Verificar infraestrutura
    verificar = PythonOperator(
        task_id='verificar_conexoes',
        python_callable=verificar_conexoes,
        doc_md='Verifica TimescaleDB e MinIO antes da coleta'
    )
    
    # Tarefa 2: Coletar dados
    coletar = PythonOperator(
        task_id='coletar_dados',
        python_callable=coletar_dados_bna,
        execution_timeout=timedelta(minutes=15),
        doc_md='Executa o coletor do BNA e salva no TimescaleDB'
    )
    
    # Tarefa 3: Validar qualidade
    validar = PythonOperator(
        task_id='validar_dados',
        python_callable=validar_dados,
        doc_md='Valida se os dados foram inseridos corretamente'
    )
    
    # Tarefa 4: Backup
    backup = PythonOperator(
        task_id='backup_minio',
        python_callable=criar_backup_minio,
        doc_md='Exporta dados para CSV e salva no MinIO'
    )
    
    # Tarefa 5: Notificação
    notificar = BashOperator(
        task_id='notificar_sucesso',
        bash_command='echo "✅ Coleta BNA concluída com sucesso em $(date)" && logger -t observatorio "DAG coleta_bna_mensal concluída"',
    )
    
    # Definir dependências
    verificar >> coletar >> validar >> backup >> notificar
