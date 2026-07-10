#!/usr/bin/env python3
"""
Health Check - Monitoramento do Observatório
Verifica se todos os componentes estão funcionando
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
import json
from scripts.utils.conexoes import ConexaoPostgres, ConexaoMinio

class HealthCheck:
    def __init__(self):
        self.status = {
            'timestamp': datetime.now().isoformat(),
            'componentes': {}
        }
    
    def check_database(self):
        """Verifica TimescaleDB"""
        try:
            pg = ConexaoPostgres()
            conn = pg.conectar()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            self.status['componentes']['database'] = {'status': '✅ OK', 'latencia': 'baixa'}
            return True
        except Exception as e:
            self.status['componentes']['database'] = {'status': f'❌ ERRO: {e}'}
            return False
    
    def check_minio(self):
        """Verifica MinIO"""
        try:
            minio = ConexaoMinio()
            buckets = minio.client.list_buckets()
            self.status['componentes']['minio'] = {
                'status': '✅ OK',
                'buckets': len(buckets)
            }
            return True
        except Exception as e:
            self.status['componentes']['minio'] = {'status': f'❌ ERRO: {e}'}
            return False
    
    def check_modelos(self):
        """Verifica modelos ML"""
        modelos_path = Path('models')
        modelos = {
            'lstm': modelos_path / 'lstm_model.pth',
            'scaler_lstm': modelos_path / 'scaler_lstm.pkl',
            'xgboost': modelos_path / 'modelo_inflacao.pkl'
        }
        
        for nome, path in modelos.items():
            if path.exists():
                self.status['componentes'][f'modelo_{nome}'] = {
                    'status': '✅ OK',
                    'tamanho': f'{path.stat().st_size / 1024:.1f} KB'
                }
            else:
                self.status['componentes'][f'modelo_{nome}'] = {'status': '⚠️ Não encontrado'}
    
    def check_dados(self):
        """Verifica se há dados recentes"""
        try:
            pg = ConexaoPostgres()
            conn = pg.conectar()
            cur = conn.cursor()
            
            tabelas = ['taxas_cambio', 'taxas_juro', 'ipc', 'precos_internacionais']
            for tabela in tabelas:
                cur.execute(f"""
                    SELECT MAX(timestamp) FROM raw.{tabela}
                """)
                ultimo = cur.fetchone()[0]
                dias_atras = (datetime.now() - ultimo.replace(tzinfo=None)).days if ultimo else 999
                
                status = '✅ OK' if dias_atras < 7 else '⚠️ Desatualizado' if dias_atras < 30 else '❌ Muito antigo'
                self.status['componentes'][f'dados_{tabela}'] = {
                    'status': status,
                    'ultima_atualizacao': str(ultimo)[:19] if ultimo else 'Nunca',
                    'dias_atras': dias_atras
                }
            
            cur.close()
            conn.close()
        except Exception as e:
            self.status['componentes']['dados'] = {'status': f'❌ ERRO: {e}'}
    
    def executar(self):
        """Executa todas as verificações"""
        print("🏥 HEALTH CHECK - OBSERVATÓRIO MONETÁRIO")
        print("=" * 50)
        
        self.check_database()
        self.check_minio()
        self.check_modelos()
        self.check_dados()
        
        # Calcular saúde geral
        todos_ok = all('✅' in str(c.get('status', '')) for c in self.status['componentes'].values())
        self.status['saude_geral'] = '✅ SAUDÁVEL' if todos_ok else '⚠️ ATENÇÃO'
        
        print(f"\nStatus Geral: {self.status['saude_geral']}")
        print(f"Timestamp: {self.status['timestamp'][:19]}")
        print("\nComponentes:")
        
        for nome, info in self.status['componentes'].items():
            status = info.get('status', 'Desconhecido')
            print(f"  {status} | {nome}")
        
        # Salvar relatório
        report_path = Path('data/health_check.json')
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Relatório salvo: {report_path}")
        return self.status

if __name__ == "__main__":
    hc = HealthCheck()
    hc.executar()
