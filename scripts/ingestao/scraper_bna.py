"""
Scraper do BNA - Taxas de Câmbio Reais
Tenta extrair dados do site do BNA
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_acesso_bna():
    """Testa se o site do BNA está acessível"""
    urls = [
        "https://www.bna.ao/",
        "https://www.bna.ao/Estatisticas/Taxas-de-Cambio",
        "https://www.bna.ao/PT/Estatisticas/Taxas-de-Cambio"
    ]
    
    for url in urls:
        try:
            logger.info(f"🔍 Testando: {url}")
            response = requests.get(url, timeout=15, 
                                   headers={'User-Agent': 'Mozilla/5.0'})
            logger.info(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar tabelas
                tabelas = soup.find_all('table')
                logger.info(f"   Tabelas encontradas: {len(tabelas)}")
                
                # Procurar texto "USD" ou "câmbio"
                if 'USD' in response.text or 'cambio' in response.text.lower():
                    logger.info("   ✅ Página contém dados de câmbio!")
                    return url, response.text
        except Exception as e:
            logger.warning(f"   ❌ Erro: {e}")
    
    return None, None

if __name__ == "__main__":
    print("🔍 TESTANDO ACESSO AO BNA...")
    print("=" * 50)
    
    url, html = testar_acesso_bna()
    
    if url:
        print(f"\n✅ BNA acessível: {url}")
        print("📊 Próximo passo: Extrair tabelas de câmbio")
    else:
        print("\n❌ BNA inacessível (timeout ou bloqueio)")
        print("📝 Documentar: Necessário VPN ou proxy para aceder ao BNA")
        print("💡 Alternativa: Usar API de terceiros (ex: exchangerate-api.com)")
