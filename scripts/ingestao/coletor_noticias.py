"""
Coletor de Notícias Econômicas Angolanas
Fontes: Expansão, Mercado, Angop, Jornal de Angola
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import random
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColetorNoticias:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.fontes = {
            'angop': 'https://www.angop.ao',
            'expansao': 'https://www.expansao.co.ao',
            'mercado': 'https://www.mercado.co.ao',
            'jornal_angola': 'https://www.jornaldeangola.ao'
        }
    
    def gerar_noticias_simuladas(self, num=20):
        """
        Gera notícias simuladas realistas para testes
        Posteriormente substituir por scraping real
        """
        logger.info(f"📰 Gerando {num} notícias simuladas...")
        
        templates = [
            {
                'titulo': 'BNA mantém taxa diretora em {taxa}% pelo {n}º mês consecutivo',
                'conteudo': 'O Comité de Política Monetária do Banco Nacional de Angola decidiu hoje manter a taxa BNA em {taxa}%, citando a necessidade de conter as pressões inflacionárias. O governador destacou que a inflação continua elevada, mas mostra sinais de desaceleração gradual. A decisão visa ancorar as expectativas de inflação e estabilizar o kwanza.',
                'categoria': 'politica_monetaria',
                'sentimento': 'neutro'
            },
            {
                'titulo': 'Inflação em Angola sobe para {inflacao}% em termos anuais',
                'conteudo': 'O Instituto Nacional de Estatística divulgou hoje que a inflação homóloga atingiu {inflacao}%, pressionada pelo aumento dos preços dos alimentos e combustíveis. Analistas esperavam uma subida menor, o que pode forçar o BNA a adotar uma postura mais restritiva na próxima reunião do CPM.',
                'categoria': 'inflacao',
                'sentimento': 'negativo'
            },
            {
                'titulo': 'Kwanza aprecia {valor}% face ao dólar após medidas do BNA',
                'conteudo': 'O kwanza registou hoje uma apreciação de {valor}% face ao dólar norte-americano, reagindo positivamente às recentes medidas do BNA de restrição de liquidez. Operadores do mercado cambial reportaram maior oferta de divisas, refletindo uma melhoria na confiança dos investidores.',
                'categoria': 'cambio',
                'sentimento': 'positivo'
            },
            {
                'titulo': 'Preço do petróleo Brent atinge {preco} USD impulsionando receitas fiscais',
                'conteudo': 'O preço do barril de petróleo Brent atingiu hoje {preco} USD nos mercados internacionais, o valor mais alto dos últimos meses. Para Angola, segundo maior produtor africano, esta subida representa um alívio nas contas públicas e pode permitir maior flexibilidade na política cambial.',
                'categoria': 'petroleo',
                'sentimento': 'positivo'
            },
            {
                'titulo': 'Reservas internacionais de Angola caem para {reservas} mil milhões USD',
                'conteudo': 'As reservas internacionais líquidas de Angola caíram para {reservas} mil milhões de dólares, o nível mais baixo desde 2018. Economistas alertam que a redução das reservas pode limitar a capacidade do BNA de intervir no mercado cambial e defender o kwanza.',
                'categoria': 'reservas',
                'sentimento': 'negativo'
            },
            {
                'titulo': 'Governador do BNA: "Política monetária continuará restritiva enquanto necessário"',
                'conteudo': 'Em entrevista exclusiva, o governador do BNA reafirmou o compromisso com a estabilidade de preços e disse que a política monetária permanecerá restritiva enquanto a inflação não convergir para o objetivo. Destacou a importância da coordenação com a política fiscal para garantir a estabilidade macroeconómica.',
                'categoria': 'politica_monetaria',
                'sentimento': 'hawkish'
            },
            {
                'titulo': 'Crédito à economia cresce {credito}% impulsionado por setor privado',
                'conteudo': 'O crédito à economia registou um crescimento de {credito}% no último trimestre, impulsionado principalmente pelo setor privado. O BNA vê com bons olhos a expansão do crédito, mas alerta para a necessidade de manter a qualidade dos ativos e evitar o sobre-endividamento.',
                'categoria': 'credito',
                'sentimento': 'positivo'
            },
            {
                'titulo': 'FMI revê em baixa projeções de crescimento para Angola',
                'conteudo': 'O Fundo Monetário Internacional reviu em baixa as projeções de crescimento económico para Angola, citando riscos relacionados com a volatilidade do preço do petróleo e a inflação persistente. O FMI recomenda a continuação das reformas estruturais e a consolidação fiscal.',
                'categoria': 'pib',
                'sentimento': 'negativo'
            }
        ]
        
        noticias = []
        data_base = datetime.now()
        
        for i in range(num):
            template = random.choice(templates)
            data = data_base - timedelta(days=random.randint(0, 30))
            
            # Preencher template com valores realistas
            titulo = template['titulo'].format(
                taxa=round(random.uniform(18, 21), 1),
                n=random.randint(2, 8),
                inflacao=round(random.uniform(15, 28), 1),
                valor=round(random.uniform(0.5, 3), 1),
                preco=round(random.uniform(80, 95), 2),
                reservas=round(random.uniform(12, 15), 1),
                credito=round(random.uniform(2, 8), 1)
            )
            
            conteudo = template['conteudo'].format(
                taxa=round(random.uniform(18, 21), 1),
                n=random.randint(2, 8),
                inflacao=round(random.uniform(15, 28), 1),
                valor=round(random.uniform(0.5, 3), 1),
                preco=round(random.uniform(80, 95), 2),
                reservas=round(random.uniform(12, 15), 1),
                credito=round(random.uniform(2, 8), 1)
            )
            
            noticias.append({
                'timestamp': data,
                'titulo': titulo,
                'conteudo': conteudo,
                'url_original': f'{random.choice(list(self.fontes.values()))}/economia/{i}',
                'fonte': random.choice(list(self.fontes.keys())),
                'categoria': template['categoria'],
                'sentimento_referencia': template['sentimento']
            })
        
        return pd.DataFrame(noticias)
    
    def salvar_noticias(self, df):
        """Salva notícias no banco de dados"""
        conn = self.pg.conectar()
        cur = conn.cursor()
        
        registros = 0
        for _, row in df.iterrows():
            # Verifica se já existe (evita duplicatas)
            cur.execute("""
                SELECT id FROM raw.noticias 
                WHERE titulo = %s AND DATE(timestamp) = DATE(%s)
            """, (row['titulo'], row['timestamp']))
            
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO raw.noticias 
                    (timestamp, titulo, conteudo, url_original, fonte, categoria)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (row['timestamp'], row['titulo'], row['conteudo'],
                      row['url_original'], row['fonte'], row['categoria']))
                registros += 1
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"✅ {registros} novas notícias salvas")
        return registros
    
    def executar(self):
        """Pipeline principal de coleta de notícias"""
        logger.info("📰 Iniciando coleta de notícias econômicas...")
        
        # Gerar notícias simuladas
        df = self.gerar_noticias_simuladas(20)
        
        # Salvar no banco
        novas = self.salvar_noticias(df)
        
        logger.info(f"✅ Coleta concluída: {novas} notícias processadas")
        return df

if __name__ == "__main__":
    coletor = ColetorNoticias()
    dados = coletor.executar()
    print("\n📊 Amostra das notícias coletadas:")
    print(dados[['timestamp', 'titulo', 'categoria']].head(10))
    print(f"\nCategorias: {dados['categoria'].value_counts().to_dict()}")
