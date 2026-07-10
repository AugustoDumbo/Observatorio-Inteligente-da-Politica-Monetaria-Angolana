"""
Analisador de Sentimento para Notícias Econômicas Angolanas
Versão 2.0 - Corrigida
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalisadorSentimento:
    def __init__(self):
        self.pg = ConexaoPostgres()
        
        self.lexico = {
            'positivo': [
                'crescimento', 'apreciação', 'estabilidade', 'confiança',
                'superavit', 'recuperação', 'expansão', 'otimismo',
                'valorização', 'reforço', 'melhoria', 'aumento das reservas',
                'controlo da inflação', 'disciplina fiscal', 'excedente',
                'lucro', 'ganho', 'recorde', 'histórico'
            ],
            'negativo': [
                'recessão', 'depreciação', 'volatilidade', 'incerteza',
                'deficit', 'contração', 'crise', 'pessimismo',
                'desvalorização', 'fuga de capitais', 'escassez de divisas',
                'inflação elevada', 'endividamento', 'queda', 'perda',
                'colapso', 'default', 'insustentável', 'alerta'
            ],
            'hawkish': [
                'restritiva', 'aumento da taxa', 'contenção', 'apertar',
                'rigor', 'disciplina monetária', 'ancorar expectativas',
                'combate à inflação', 'restrição de liquidez', 'controlar',
                'travar', 'conter', 'austeridade'
            ],
            'dovish': [
                'expansionista', 'flexibilização', 'estímulo', 'crescimento',
                'redução da taxa', 'alívio', 'acomodação',
                'suporte à economia', 'injeção de liquidez', 'relaxar',
                'flexibilizar', 'impulsionar', 'facilitar'
            ]
        }
        
        self._criar_tabela_analises()
    
    def _criar_tabela_analises(self):
        """Cria a tabela de análises se não existir"""
        try:
            conn = self.pg.conectar()
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.analise_sentimento (
                    id SERIAL PRIMARY KEY,
                    noticia_id INTEGER,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    score_sentimento DECIMAL(5,3),
                    sentimento VARCHAR(20),
                    confianca DECIMAL(5,3),
                    tom_monetario VARCHAR(20),
                    eventos_detectados TEXT,
                    metricas JSONB
                );
                
                CREATE INDEX IF NOT EXISTS idx_analise_noticia 
                ON raw.analise_sentimento(noticia_id);
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("✅ Tabela raw.analise_sentimento verificada")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabela: {e}")
    
    def analisar_sentimento_lexico(self, texto):
        """Análise de sentimento baseada em dicionário léxico"""
        if not texto:
            return {
                'score': 0, 
                'sentimento': 'neutro', 
                'confianca': 0,
                'tom_monetario': 'neutro',
                'metricas': {'positivo': 0, 'negativo': 0, 'hawkish': 0, 'dovish': 0}
            }
        
        texto_lower = texto.lower()
        scores = {'positivo': 0, 'negativo': 0, 'hawkish': 0, 'dovish': 0}
        
        for categoria, termos in self.lexico.items():
            for termo in termos:
                count = len(re.findall(r'\b' + re.escape(termo) + r'\b', texto_lower))
                if count == 0:
                    count = texto_lower.count(termo)
                scores[categoria] += count
        
        score_positivo = scores['positivo'] + scores['dovish']
        score_negativo = scores['negativo'] + scores['hawkish']
        score_neto = score_positivo - score_negativo
        
        max_possivel = max(abs(score_neto), len(texto.split()) / 20, 1)
        score_normalizado = score_neto / max_possivel
        score_normalizado = max(-1, min(1, score_normalizado))
        
        if score_normalizado > 0.15:
            sentimento = 'positivo'
        elif score_normalizado < -0.15:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'
        
        total_termos = sum(scores.values())
        confianca = min(1.0, total_termos / 5) if total_termos > 0 else 0.3
        
        if scores['hawkish'] > scores['dovish'] and scores['hawkish'] > 0:
            tom_monetario = 'hawkish'
        elif scores['dovish'] > scores['hawkish'] and scores['dovish'] > 0:
            tom_monetario = 'dovish'
        else:
            tom_monetario = 'neutro'
        
        return {
            'score': round(score_normalizado, 3),
            'sentimento': sentimento,
            'confianca': round(confianca, 3),
            'tom_monetario': tom_monetario,
            'metricas': scores
        }
    
    def processar_noticias_nao_analisadas(self, limite=100):
        """Processa notícias pendentes de análise"""
        logger.info("🔍 Buscando notícias não analisadas...")
        
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        # Buscar IDs já analisados
        cur.execute("SELECT COALESCE(MAX(noticia_id), 0) FROM raw.analise_sentimento")
        ultimo_id = cur.fetchone()[0]
        
        # Buscar notícias novas
        cur.execute("""
            SELECT id, timestamp, titulo, conteudo, fonte, categoria
            FROM raw.noticias
            WHERE id > %s
            ORDER BY id
            LIMIT %s
        """, (ultimo_id, limite))
        
        noticias = cur.fetchall()
        
        if len(noticias) == 0:
            logger.info("✅ Nenhuma notícia pendente para análise")
            cur.close()
            conn.close()
            return 0
        
        logger.info(f"📊 {len(noticias)} notícias para analisar")
        
        analises = []
        for noticia in noticias:
            noticia_id = noticia[0]
            timestamp = noticia[1]
            titulo = noticia[2]
            conteudo = noticia[3] or ''
            
            texto_completo = f"{titulo} {conteudo}"
            analise = self.analisar_sentimento_lexico(texto_completo)
            
            # Converter métricas para JSON válido
            metricas_json = json.dumps(analise['metricas'])
            
            # Inserir análise
            cur.execute("""
                INSERT INTO raw.analise_sentimento 
                (noticia_id, timestamp, score_sentimento, sentimento, 
                 confianca, tom_monetario, eventos_detectados, metricas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (
                noticia_id,
                timestamp,
                analise['score'],
                analise['sentimento'],
                analise['confianca'],
                analise['tom_monetario'],
                '',
                metricas_json
            ))
            
            analises.append({
                'id': noticia_id,
                'titulo': titulo[:80],
                'sentimento': analise['sentimento'],
                'tom': analise['tom_monetario']
            })
        
        conn.commit()
        
        df_resumo = pd.DataFrame(analises)
        distribuicao = df_resumo['sentimento'].value_counts().to_dict()
        
        logger.info(f"✅ {len(analises)} notícias analisadas com sucesso")
        logger.info(f"📊 Distribuição: {distribuicao}")
        
        cur.close()
        conn.close()
        return len(analises)
    
    def calcular_indice_surpresa(self, dias=7):
        """Calcula o Índice de Surpresa Monetária"""
        logger.info(f"📊 Calculando ISM para os últimos {dias} dias...")
        
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        # Query simples sem parâmetros problemáticos
        query = f"""
            SELECT 
                tom_monetario,
                COUNT(*) as volume
            FROM raw.analise_sentimento
            WHERE timestamp >= NOW() - INTERVAL '{dias} days'
            GROUP BY tom_monetario
        """
        
        cur.execute(query)
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        
        hawkish = sum(r[1] for r in resultados if r[0] == 'hawkish')
        dovish = sum(r[1] for r in resultados if r[0] == 'dovish')
        total = hawkish + dovish
        
        if total > 0:
            ism = (hawkish - dovish) / total
        else:
            ism = 0
        
        if ism > 0.3:
            interpretacao = 'Expectativa de aperto monetário 📈'
        elif ism < -0.3:
            interpretacao = 'Expectativa de flexibilização 📉'
        else:
            interpretacao = 'Expectativa neutra/estável ⚖️'
        
        return {
            'ism': round(ism, 3),
            'interpretacao': interpretacao,
            'volume': int(total),
            'hawkish': hawkish,
            'dovish': dovish,
            'periodo_dias': dias
        }

