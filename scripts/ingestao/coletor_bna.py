"""
Coletor de dados do BNA - Primeira versão com dados históricos simulados
Baseado em padrões reais da economia angolana
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime, timedelta
import random
from scripts.utils.conexoes import ConexaoPostgres
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColetorBNA:
    def __init__(self):
        self.pg = ConexaoPostgres()
        
    def gerar_dados_historicos(self, meses=24):
        """
        Gera dados simulados baseados em padrões reais
        Posteriormente substituiremos por dados reais via API/Scraping
        """
        logger.info(f"📊 Gerando {meses} meses de dados históricos...")
        
        # Datas base
        data_fim = datetime.now().replace(day=1)
        datas = [data_fim - timedelta(days=30*i) for i in range(meses)]
        datas.reverse()
        
        dados = []
        
        # Valores iniciais realistas (aproximados)
        taxa_bna = 19.5  # Taxa diretora
        usd_compra = 830.0  # USD/AOA
        eur_compra = 905.0  # EUR/AOA
        m2 = 12000000  # Milhões AOA (12 trilhões)
        reservas = 14500  # Milhões USD
        
        for i, data in enumerate(datas):
            # Simula variações mensais com alguma tendência
            choque = random.gauss(0, 0.1)
            
            taxa_bna += choque * 0.5
            taxa_bna = max(15, min(22, taxa_bna))  # Limites realistas
            
            usd_compra *= (1 + choque * 0.02 + 0.003)  # Tendência de depreciação
            eur_compra = usd_compra * 1.08 + random.gauss(0, 5)
            
            m2 *= (1 + choque * 0.01 + 0.008)  # Crescimento monetário
            reservas += choque * 50
            
            dados.append({
                'data': data,
                'taxa_bna': round(taxa_bna, 2),
                'usd_compra': round(usd_compra, 2),
                'usd_venda': round(usd_compra * 1.02, 2),
                'eur_compra': round(eur_compra, 2),
                'eur_venda': round(eur_compra * 1.02, 2),
                'm2': round(m2, 2),
                'm3': round(m2 * 1.15, 2),
                'base_monetaria': round(m2 * 0.45, 2),
                'reservas_internacionais': round(reservas, 2)
            })
        
        return pd.DataFrame(dados)
    
    def salvar_taxas_cambio(self, df):
        """Salva taxas de câmbio no banco"""
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        for _, row in df.iterrows():
            # USD
            cur.execute("""
                INSERT INTO raw.taxas_cambio (timestamp, moeda, valor_compra, valor_venda)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (timestamp, moeda) DO UPDATE 
                SET valor_compra = EXCLUDED.valor_compra,
                    valor_venda = EXCLUDED.valor_venda
            """, (row['data'], 'USD', row['usd_compra'], row['usd_venda']))
            
            # EUR
            cur.execute("""
                INSERT INTO raw.taxas_cambio (timestamp, moeda, valor_compra, valor_venda)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (timestamp, moeda) DO UPDATE 
                SET valor_compra = EXCLUDED.valor_compra,
                    valor_venda = EXCLUDED.valor_venda
            """, (row['data'], 'EUR', row['eur_compra'], row['eur_venda']))
            
            registros += 2
            
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"✅ {registros} registros de taxas de câmbio salvos")
    
    def salvar_taxas_juro(self, df):
        """Salva taxas de juro no banco"""
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO raw.taxas_juro (timestamp, taxa_bna, taxa_luibor_overnight)
                VALUES (%s, %s, %s)
                ON CONFLICT (timestamp) DO UPDATE 
                SET taxa_bna = EXCLUDED.taxa_bna
            """, (row['data'], row['taxa_bna'], row['taxa_bna'] - 1.5))
            registros += 1
            
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"✅ {registros} registros de taxas de juro salvos")
    
    def salvar_agregados(self, df):
        """Salva agregados monetários no banco"""
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO raw.agregados_monetarios 
                (timestamp, m2, m3, base_monetaria, reservas_internacionais)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO UPDATE 
                SET m2 = EXCLUDED.m2,
                    m3 = EXCLUDED.m3,
                    reservas_internacionais = EXCLUDED.reservas_internacionais
            """, (row['data'], row['m2'], row['m3'], 
                  row['base_monetaria'], row['reservas_internacionais']))
            registros += 1
            
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"✅ {registros} registros de agregados monetários salvos")
    
    def executar(self):
        """Pipeline principal de coleta"""
        logger.info("🏦 Iniciando coleta de dados do BNA...")
        
        # Gerar dados históricos
        df = self.gerar_dados_historicos(meses=24)
        
        # Salvar nas respectivas tabelas
        self.salvar_taxas_cambio(df)
        self.salvar_taxas_juro(df)
        self.salvar_agregados(df)
        
        logger.info("✅ Coleta BNA concluída!")
        return df

if __name__ == "__main__":
    coletor = ColetorBNA()
    dados = coletor.executar()
    print("\n📊 Amostra dos dados coletados:")
    print(dados.head())
    print(f"\nTotal de meses: {len(dados)}")
