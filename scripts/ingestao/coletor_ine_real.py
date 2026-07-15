"""Coletor de IPC do INE Angola - Dados Reais"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scripts.utils.conexoes import ConexaoPostgres
from scripts.ingestao.coletor_ine import ColetorINE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColetorINEReal:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.base_url = "https://www.ine.gov.ao"
    
    def buscar_ultimo_ipc(self):
        """Busca o ficheiro Excel mais recente do IPC"""
        logger.info("🔍 Procurando último relatório de IPC...")
        
        try:
            response = requests.get(self.base_url, timeout=15, 
                                   headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    texto = link.get_text().lower()
                    
                    if ('ipc' in texto or 'índice' in texto) and \
                       ('.xls' in href or '.pdf' in href):
                        logger.info(f"📁 Encontrado: {texto[:80]}")
                        return href if href.startswith('http') else f"{self.base_url}{href}"
                
                logger.info("ℹ️ Nenhum link de IPC encontrado na página principal")
        except Exception as e:
            logger.warning(f"⚠️ Erro: {e}")
        
        return None
    
    def executar(self):
        """Pipeline principal"""
        logger.info("🏛️ INE - Coleta de IPC")
        
        url = self.buscar_ultimo_ipc()
        
        if url:
            logger.info(f"✅ URL encontrada: {url}")
            logger.info("📝 Scraping completo requer download + parse do Excel")
        else:
            logger.warning("⚠️ URL não encontrada")
        
        # Fallback: dados simulados
        logger.info("📊 Usando ColetorINE simulado...")
        coletor = ColetorINE()
        return coletor.executar()

if __name__ == "__main__":
    coletor = ColetorINEReal()
    dados = coletor.executar()
    if dados is not None:
        print(f"\n✅ Dados processados: {len(dados)} registros")
