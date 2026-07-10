"""
Sistema de Alertas Inteligentes - Calibrado
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SistemaAlertas:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.alertas = []
        
    def verificar_cambio(self):
        """Alerta para variações cambiais"""
        conn = self.pg.conectar()
        
        df = pd.read_sql("""
            SELECT timestamp, valor_compra
            FROM raw.taxas_cambio
            WHERE moeda = 'USD' 
            AND timestamp >= NOW() - INTERVAL '7 days'
            ORDER BY timestamp
        """, conn)
        
        conn.close()
        
        if len(df) >= 2:
            ultimo = df['valor_compra'].iloc[-1]
            primeiro = df['valor_compra'].iloc[0]
            variacao = ((ultimo - primeiro) / primeiro * 100)
            
            # Limites mais sensíveis para teste
            if abs(variacao) > 0.5:  # Reduzido de 2% para 0.5%
                self.alertas.append({
                    'tipo': 'CÂMBIO',
                    'nivel': '🔴 ALTO' if abs(variacao) > 1 else '🟡 MÉDIO',
                    'mensagem': f'USD/AOA variou {variacao:+.2f}% nos últimos 7 dias (${primeiro:,.0f} → ${ultimo:,.0f})',
                    'timestamp': datetime.now().isoformat(),
                    'acao': 'Monitorar necessidade de intervenção cambial'
                })
    
    def verificar_inflacao(self):
        """Alerta para tendências de inflação"""
        conn = self.pg.conectar()
        
        df = pd.read_sql("""
            SELECT timestamp, ipc_geral
            FROM raw.ipc
            ORDER BY timestamp DESC
            LIMIT 3
        """, conn)
        
        conn.close()
        
        if len(df) >= 2:
            atual = df['ipc_geral'].iloc[0]
            anterior = df['ipc_geral'].iloc[-1]
            tendencia = atual - anterior
            
            if abs(tendencia) > 0.3:  # Mais sensível
                self.alertas.append({
                    'tipo': 'INFLAÇÃO',
                    'nivel': '🔴 ALTO' if tendencia > 0 else '🟢 BAIXO',
                    'mensagem': f'IPC variou {tendencia:+.1f}pp ({anterior:.1f}% → {atual:.1f}%)',
                    'timestamp': datetime.now().isoformat(),
                    'acao': 'Possível ajuste na Taxa BNA' if tendencia > 0 else 'Espaço para política expansionista'
                })
    
    def verificar_nlp(self):
        """Alerta baseado no sentimento do mercado"""
        try:
            from scripts.nlp.analisador_sentimento import AnalisadorSentimento
            
            analisador = AnalisadorSentimento()
            ism = analisador.calcular_indice_surpresa(7)
            
            if ism['volume'] > 0:  # Só alerta se há dados
                self.alertas.append({
                    'tipo': 'SENTIMENTO NLP',
                    'nivel': '🔴 ALTO' if abs(ism['ism']) > 0.3 else '🟢 NORMAL',
                    'mensagem': f'ISM: {ism["ism"]:.2f} - {ism["interpretacao"]} ({ism["volume"]} notícias)',
                    'timestamp': datetime.now().isoformat(),
                    'acao': 'Ajustar comunicação oficial' if abs(ism['ism']) > 0.5 else 'Manter monitoramento'
                })
        except Exception as e:
            logger.warning(f"NLP não disponível: {e}")
    
    def verificar_reservas(self):
        """Alerta para nível de reservas"""
        conn = self.pg.conectar()
        
        df = pd.read_sql("""
            SELECT timestamp, reservas_internacionais
            FROM raw.agregados_monetarios
            ORDER BY timestamp DESC
            LIMIT 3
        """, conn)
        
        conn.close()
        
        if len(df) >= 1:
            reservas = df['reservas_internacionais'].iloc[0]
            
            self.alertas.append({
                'tipo': 'RESERVAS',
                'nivel': 'ℹ️ INFO',
                'mensagem': f'Reservas internacionais: ${reservas:,.0f} milhões',
                'timestamp': datetime.now().isoformat(),
                'acao': 'Nível de monitoramento regular'
            })
    
    def gerar_relatorio(self):
        """Gera relatório consolidado"""
        logger.info("📋 Gerando relatório de alertas...")
        
        self.alertas = []
        self.verificar_cambio()
        self.verificar_inflacao()
        self.verificar_nlp()
        self.verificar_reservas()
        
        # Ordenar por criticidade
        ordem = {'🔴 ALTO': 0, '🟡 MÉDIO': 1, '🟢 NORMAL': 2, '🟢 BAIXO': 3, 'ℹ️ INFO': 4}
        self.alertas.sort(key=lambda x: ordem.get(x['nivel'], 99))
        
        relatorio = {
            'data': datetime.now().isoformat(),
            'total_alertas': len(self.alertas),
            'alertas': self.alertas,
            'resumo': self._gerar_resumo()
        }
        
        # Salvar
        alertas_path = Path(__file__).parent.parent.parent / 'data' / 'alertas.json'
        alertas_path.parent.mkdir(exist_ok=True)
        
        with open(alertas_path, 'w') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        return relatorio
    
    def _gerar_resumo(self):
        criticos = sum(1 for a in self.alertas if 'ALTO' in a['nivel'])
        medios = sum(1 for a in self.alertas if 'MÉDIO' in a['nivel'])
        
        if criticos > 0:
            return f"⚠️ {criticos} alertas críticos requerem atenção imediata"
        elif medios > 0:
            return f"📊 {medios} alertas médios - Monitoramento intensificado"
        else:
            return f"✅ Sistema estável - {len(self.alertas)} indicadores monitorados"
    
    def exibir_dashboard_alertas(self):
        """Exibe alertas no terminal"""
        relatorio = self.gerar_relatorio()
        
        print("\n" + "=" * 70)
        print("🔔 SISTEMA DE ALERTAS - OBSERVATÓRIO MONETÁRIO ANGOLANO")
        print("=" * 70)
        print(f"📅 {relatorio['data'][:19]}")
        print(f"📊 Alertas: {relatorio['total_alertas']}")
        print(f"📋 {relatorio['resumo']}")
        print("-" * 70)
        
        for i, alerta in enumerate(relatorio['alertas'], 1):
            print(f"\n{i}. {alerta['nivel']} | {alerta['tipo']}")
            print(f"   📝 {alerta['mensagem']}")
            print(f"   🎯 {alerta['acao']}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    sistema = SistemaAlertas()
    sistema.exibir_dashboard_alertas()
