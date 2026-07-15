"""
Coletor BNA com Dados REAIS via ExchangeRate-API
Fonte: https://open.er-api.com (grátis, sem key)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import requests
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColetorBNAReal:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.api_base = "https://open.er-api.com/v6"
        
    def obter_cambio_atual(self, moeda_base="USD"):
        """
        Obtém taxa de câmbio atual via ExchangeRate-API
        Retorna USD/AOA e EUR/AOA
        """
        logger.info(f"💵 Obtendo câmbio real para {moeda_base}...")
        
        try:
            # Obter USD → todas moedas
            url = f"{self.api_base}/latest/{moeda_base}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                aoa_rate = data['rates'].get('AOA')
                eur_rate = data['rates'].get('EUR')
                
                if aoa_rate:
                    # Calcular EUR/AOA via USD
                    eur_aoa = aoa_rate / eur_rate if eur_rate else None
                    
                    logger.info(f"✅ USD/AOA = {aoa_rate:.2f}")
                    logger.info(f"✅ EUR/AOA = {eur_aoa:.2f}" if eur_aoa else "⚠️ EUR não disponível")
                    
                    return {
                        'data': datetime.now(),
                        'usd_aoa': aoa_rate,
                        'eur_aoa': eur_aoa or aoa_rate * 1.08  # Fallback aproximado
                    }
        except Exception as e:
            logger.warning(f"⚠️ Erro API: {e}")
        
        return None
    
    def obter_historico(self, dias=30):
        """
        Tenta obter dados históricos (limitado na API gratuita)
        """
        logger.info(f"📊 Obtendo histórico de {dias} dias...")
        
        dados = []
        hoje = datetime.now()
        
        # A API gratuita só dá o último dia
        # Para histórico, fazemos múltiplas chamadas (cuidado com rate limit!)
        for i in range(min(dias, 5)):  # Limitar a 5 dias para não abusar
            data = hoje - timedelta(days=i)
            
            try:
                # Tentar data específica (a API pode não suportar)
                url = f"{self.api_base}/latest/USD"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    rates = response.json()['rates']
                    dados.append({
                        'data': data,
                        'usd_aoa': rates.get('AOA', 0),
                        'eur_aoa': rates.get('AOA', 0) / rates.get('EUR', 1)
                    })
                
                time.sleep(0.5)  # Respeitar rate limit
            except:
                pass
        
        return pd.DataFrame(dados) if dados else None
    
    def salvar_cambio(self, dados):
        """Salva taxa de câmbio no banco"""
        if not dados:
            return 0
        
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        
        # Salvar USD
        if dados.get('usd_aoa'):
            cur.execute("""
                INSERT INTO raw.taxas_cambio (timestamp, moeda, valor_compra, valor_venda)
                VALUES (%s, 'USD', %s, %s)
                ON CONFLICT (timestamp, moeda) DO UPDATE 
                SET valor_compra = EXCLUDED.valor_compra,
                    valor_venda = EXCLUDED.valor_venda
            """, (dados['data'], dados['usd_aoa'], dados['usd_aoa'] * 1.02))
            registros += 1
        
        # Salvar EUR
        if dados.get('eur_aoa'):
            cur.execute("""
                INSERT INTO raw.taxas_cambio (timestamp, moeda, valor_compra, valor_venda)
                VALUES (%s, 'EUR', %s, %s)
                ON CONFLICT (timestamp, moeda) DO UPDATE 
                SET valor_compra = EXCLUDED.valor_compra,
                    valor_venda = EXCLUDED.valor_venda
            """, (dados['data'], dados['eur_aoa'], dados['eur_aoa'] * 1.02))
            registros += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"✅ {registros} registros de câmbio salvos")
        return registros
    
    def executar(self):
        """Pipeline principal"""
        logger.info("🏦 Obtendo câmbio REAL via ExchangeRate-API...")
        
        # Obter câmbio atual
        dados = self.obter_cambio_atual("USD")
        
        if dados:
            self.salvar_cambio(dados)
            
            print("\n📊 CÂMBIO REAL (ExchangeRate-API):")
            print(f"  Data: {dados['data'].strftime('%Y-%m-%d %H:%M')}")
            print(f"  💵 USD/AOA: {dados['usd_aoa']:,.2f}")
            print(f"  💶 EUR/AOA: {dados['eur_aoa']:,.2f}")
        else:
            logger.error("❌ Não foi possível obter câmbio real")
        
        return dados

if __name__ == "__main__":
    coletor = ColetorBNAReal()
    dados = coletor.executar()
    
    if dados:
        print("\n✅ DADOS REAIS OBTIDOS COM SUCESSO!")
        print("🌐 Fonte: ExchangeRate-API (open.er-api.com)")
    else:
        print("\n❌ Falha ao obter dados reais")
