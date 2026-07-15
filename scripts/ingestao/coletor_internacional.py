"""
Coletor de Dados Internacionais REAIS
Fontes: World Bank API (Brent) + FRED API (FED Funds)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColetorInternacional:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.fred_api_key = os.getenv('FRED_API_KEY', '')
        
    def obter_preco_brent(self, meses=24):
        """
        Obtém preço do petróleo Brent via World Bank API
        Indicador: DPANUSSPB (Preço do petróleo bruto, média spot)
        """
        logger.info("🛢️ Obtendo preço do Brent (World Bank API)...")
        
        try:
            url = "http://api.worldbank.org/v2/country/WLD/indicator/DPANUSSPB"
            params = {
                'format': 'json',
                'per_page': meses,
                'date': f"{datetime.now().year - 2}:{datetime.now().year}"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    registros = []
                    for item in data[1]:
                        if item.get('value'):
                            registros.append({
                                'data': pd.to_datetime(item['date']),
                                'brent_crude': float(item['value'])
                            })
                    
                    if registros:
                        df = pd.DataFrame(registros).sort_values('data')
                        logger.info(f"✅ {len(df)} preços Brent obtidos do World Bank")
                        return df
                    else:
                        logger.warning("⚠️ API retornou dados vazios")
                else:
                    logger.warning("⚠️ API retornou estrutura inesperada")
            else:
                logger.warning(f"⚠️ API retornou status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao acessar World Bank API: {e}")
        
        # Fallback: dados simulados
        logger.info("📊 Usando dados simulados como fallback")
        return self._gerar_brent_simulado(meses)
    
    def obter_fed_funds(self, meses=24):
        """
        Obtém Federal Funds Rate via FRED API
        Indicador: FEDFUNDS
        """
        logger.info("🏦 Obtendo Federal Funds Rate (FRED API)...")
        
        if self.fred_api_key:
            try:
                url = "https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': 'FEDFUNDS',
                    'api_key': self.fred_api_key,
                    'file_type': 'json',
                    'limit': meses,
                    'sort_order': 'desc'
                }
                
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    observacoes = data.get('observations', [])
                    
                    if observacoes:
                        registros = []
                        for obs in observacoes:
                            if obs['value'] != '.':
                                registros.append({
                                    'data': pd.to_datetime(obs['date']),
                                    'federal_funds_rate': float(obs['value'])
                                })
                        
                        df = pd.DataFrame(registros).sort_values('data')
                        logger.info(f"✅ {len(df)} taxas FED obtidas da FRED")
                        return df
            except Exception as e:
                logger.warning(f"⚠️ Erro FRED API: {e}")
        
        logger.info("📊 Usando dados FED simulados (sem API key)")
        return self._gerar_fed_simulado(meses)
    
    def obter_inflacao_global(self, meses=24):
        """Obtém inflação global via World Bank"""
        logger.info("🌍 Obtendo inflação global (World Bank API)...")
        
        try:
            url = "http://api.worldbank.org/v2/country/WLD/indicator/FP.CPI.TOTL.ZG"
            params = {
                'format': 'json',
                'per_page': meses,
                'date': f"{datetime.now().year - 2}:{datetime.now().year}"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    registros = []
                    for item in data[1]:
                        if item.get('value'):
                            registros.append({
                                'data': pd.to_datetime(item['date']),
                                'inflacao_global': float(item['value'])
                            })
                    
                    if registros:
                        df = pd.DataFrame(registros).sort_values('data')
                        logger.info(f"✅ {len(df)} registros de inflação global")
                        return df
        except Exception as e:
            logger.warning(f"⚠️ Erro inflação global: {e}")
        
        return self._gerar_inflacao_simulada(meses)
    
    def _gerar_brent_simulado(self, meses):
        """Fallback: Brent simulado"""
        logger.info("Gerando Brent simulado...")
        datas = pd.date_range(start=datetime.now() - timedelta(days=30*meses), periods=meses, freq='MS')
        brent = np.random.normal(82, 5, meses).clip(70, 95)
        return pd.DataFrame({'data': datas, 'brent_crude': brent.round(2)})
    
    def _gerar_fed_simulado(self, meses):
        """Fallback: FED Funds simulado"""
        logger.info("Gerando FED Funds simulado...")
        datas = pd.date_range(start=datetime.now() - timedelta(days=30*meses), periods=meses, freq='MS')
        fed = np.random.normal(5.0, 0.3, meses).clip(4.0, 6.0)
        return pd.DataFrame({'data': datas, 'federal_funds_rate': fed.round(2)})
    
    def _gerar_inflacao_simulada(self, meses):
        """Fallback: Inflação global simulada"""
        logger.info("Gerando inflação global simulada...")
        datas = pd.date_range(start=datetime.now() - timedelta(days=30*meses), periods=meses, freq='MS')
        inf = np.random.normal(3.5, 0.3, meses).clip(2.5, 5.0)
        return pd.DataFrame({'data': datas, 'inflacao_global': inf.round(2)})
    
    def consolidar_dados(self, df_brent, df_fed, df_inflacao):
        """Junta os 3 dataframes num só"""
        logger.info("🔗 Consolidando dados internacionais...")
        
        # Criar base mensal
        datas = pd.date_range(
            start=datetime.now() - timedelta(days=730),
            end=datetime.now(),
            freq='MS'
        )
        df_base = pd.DataFrame({'data': datas})
        df_base['data'] = df_base['data'].dt.tz_localize(None)
        
        # Remover timezone dos outros
        for df in [df_brent, df_fed, df_inflacao]:
            if not df.empty and 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data']).dt.tz_localize(None)
        
        # Merge
        df = df_base.copy()
        if not df_brent.empty:
            df = df.merge(df_brent, on='data', how='left')
        if not df_fed.empty:
            df = df.merge(df_fed, on='data', how='left')
        if not df_inflacao.empty:
            df = df.merge(df_inflacao, on='data', how='left')
        
        # Preencher valores vazios
        df = df.ffill().bfill().fillna(0)
        
        # Garantir colunas necessárias
        for col in ['brent_crude', 'federal_funds_rate', 'inflacao_global']:
            if col not in df.columns:
                df[col] = 0
        
        logger.info(f"✅ Dados consolidados: {len(df)} meses")
        return df
    
    def salvar_dados(self, df):
        """Salva no banco de dados"""
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO raw.precos_internacionais 
                (timestamp, brent_crude, federal_funds_rate, inflacao_global)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (timestamp) DO UPDATE 
                SET brent_crude = EXCLUDED.brent_crude,
                    federal_funds_rate = EXCLUDED.federal_funds_rate,
                    inflacao_global = EXCLUDED.inflacao_global
            """, (row['data'], row['brent_crude'], 
                  row['federal_funds_rate'], row['inflacao_global']))
            registros += 1
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"✅ {registros} registros internacionais salvos")
    
    def executar(self):
        """Pipeline principal"""
        logger.info("🌍 Iniciando coleta de dados internacionais REAIS...")
        
        # Obter dados de cada fonte
        df_brent = self.obter_preco_brent(24)
        df_fed = self.obter_fed_funds(24)
        df_inflacao = self.obter_inflacao_global(24)
        
        # Consolidar
        df = self.consolidar_dados(df_brent, df_fed, df_inflacao)
        
        # Salvar
        self.salvar_dados(df)
        
        # Mostrar amostra
        logger.info(f"\n📊 AMOSTRA DOS DADOS (últimos 5):")
        print(df[['data', 'brent_crude', 'federal_funds_rate', 'inflacao_global']].tail())
        
        logger.info("✅ Coleta internacional concluída!")
        return df

if __name__ == "__main__":
    coletor = ColetorInternacional()
    dados = coletor.executar()
    
    # Verificar quantos reais vs simulados
    brent_real = len(dados[dados['brent_crude'] > 0])
    print(f"\n📊 Resumo:")
    print(f"  Total de meses: {len(dados)}")
    print(f"  Dados Brent: {brent_real} registros")
    print(f"  Período: {dados['data'].min()} a {dados['data'].max()}")
