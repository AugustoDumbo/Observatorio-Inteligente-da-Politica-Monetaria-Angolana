# 📘 OBSERVATÓRIO INTELIGENTE DA POLÍTICA MONETÁRIA ANGOLANA
## Manual do Utilizador — Versão 2.0

---

## ✨ Bem-vindo!

O **Observatório Inteligente da Política Monetária Angolana** é uma plataforma que utiliza Inteligência Artificial para monitorizar a economia de Angola. Com ela, pode acompanhar taxas de câmbio, inflação, previsões económicas e muito mais — tudo de forma simples e intuitiva.

**Para quem é este sistema?**
- 🧑‍🎓 **Estudantes** que queiram compreender a economia angolana
- 📊 **Analistas económicos** que necessitam de dados actualizados
- 🏛️ **Instituições** que precisam de monitorizar indicadores
- 👥 **Cidadãos** interessados em política monetária

---

## 📑 Índice

1. [Instalação e Requisitos](#1-instalação-e-requisitos)
2. [Primeiro Acesso](#2-primeiro-acesso)
3. [Dashboard Principal](#3-dashboard-principal)
4. [Previsões com Inteligência Artificial](#4-previsões-com-inteligência-artificial)
5. [Análise de Sentimento (NLP)](#5-análise-de-sentimento-nlp)
6. [Sistema de Alertas](#6-sistema-de-alertas)
7. [Dados Brutos](#7-dados-brutos)
8. [Bot do Telegram](#8-bot-do-telegram)
9. [API REST](#9-api-rest)
10. [Resolução de Problemas](#10-resolução-de-problemas)
11. [Glossário](#11-glossário)

---

## 1. Instalação e Requisitos

### O que precisa:

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| 💻 Sistema Operativo | Ubuntu 20.04+ | Ubuntu 24.04 |
| 🐍 Python | 3.10+ | 3.12 |
| 🐘 PostgreSQL | 14+ | 16+ (TimescaleDB) |
| 💾 RAM | 4 GB | 8 GB |
| 💿 Espaço em Disco | 2 GB | 10 GB |

### Instalação Rápida (5 minutos):

```bash
# 1. Abra o terminal (Ctrl + Alt + T)

# 2. Navegue até à pasta do projecto
cd observatorio_monetario_angola

# 3. Crie o ambiente virtual
python3 -m venv venv

# 4. Active o ambiente
source venv/bin/activate

# 5. Instale as dependências
pip install -r requirements.txt

# 6. Configure as credenciais
nano .env  # Insira as senhas do banco de dados

# 7. Execute o assistente de instalação
./deploy_producao.sh
📁 observatorio_monetario_angola
├── 📊 app_final_v2.py          ← Dashboard (clique aqui para abrir)
├── 🔌 api.py                    ← API (para programadores)
├── 🤖 bot/telegram_bot.py       ← Bot Telegram
├── 📁 scripts/                  ← Códigos internos
├── 📁 models/                   ← Modelos de IA treinados
└── 📁 data/                     ← Dados e relatórios
2. Primeiro Acesso
Iniciar o Sistema:
# Active o ambiente virtual (sempre que abrir o terminal)
cd observatorio_monetario_angola
source venv/bin/activate

# Inicie o dashboard
streamlit run app_final_v2.py

# Abra o navegador e aceda:
# 🔗 http://localhost:8501
┌─────────────────────────────────────────┐
│  🇦🇴 Observatório Monetário Angolano     │
│  ≡ Menu Lateral                          │
│  ┌─────────────┐  ┌─────────────┐       │
│  │ USD/AOA     │  │ Taxa BNA    │       │
│  │ 893.92      │  │ 19.5%       │       │
│  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐       │
│  │ Inflação    │  │ Brent       │       │
│  │ 27.6%       │  │ $85.00      │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
Navegação:

O menu lateral (≡) tem 5 páginas:
Ícone	Página	O que faz
📈	Dashboard Principal	Visão geral da economia
🔮	Previsões ML	Previsões da IA
📰	Análise NLP	Sentimento das notícias

🔔	Sistema de Alertas	Avisos automáticos
📊	Dados Brutos	Tabelas completas
3. Dashboard Principal
Visão Geral

É a página inicial do sistema. Mostra os indicadores mais importantes da economia angolana em tempo real.

https://via.placeholder.com/800x400/1a237e/white?text=Dashboard+Principal
Indicadores Principais:
💵 USD/AOA

    O que é: Quantos Kwanzas valem 1 Dólar americano

    Como ler: Se sobe → Kwanza desvalorizou | Se desce → Kwanza valorizou

    Exemplo: 893.92 Kz = 1 USD

🏦 Taxa BNA

    O que é: Taxa de juro definida pelo Banco Nacional

    Como ler: Taxa alta → Política restritiva | Taxa baixa → Política expansionista

    Valor típico: 15% – 22%

📈 Inflação (IPC)

    O que é: Aumento geral dos preços
    Como ler: Abaixo de 15% é bom | Acima de 25% é preocupante

    Sigla: IPC = Índice de Preços no Consumidor

🛢️ Petróleo Brent

    O que é: Preço internacional do petróleo

    Importância: Angola é grande exportador de petróleo

    Impacto: Preço alto → Mais receitas para o país

Gráficos Interativos:

Todos os gráficos são interativos:

    🖱️ Passe o rato para ver valores exactos

    🔍 Arraste para fazer zoom

    📸 Clique na câmara para salvar imagem
    ⬇️ Botão download para exportar dados

Gráfico 1: Inflação vs Taxa de Juro
Eixo Esquerdo (Vermelho): Inflação
Eixo Direito (Azul): Taxa BNA
Interpretação: Quando a inflação sobe, o BNA geralmente aumenta a taxa de juro.
Gráfico 2: Taxa de Câmbio
Linha Verde: USD/AOA ao longo do tempo
Interpretação: Uma linha a subir significa que o Kwanza está a desvalorizar.
Como Actualizar os Dados:

Os dados actualizam automaticamente a cada 60 segundos. Para forçar actualização:

    🔄 Botão "Rerun" no canto superior direito

    Ou pressione R no teclado

4. Previsões com Inteligência Artificial
O que é?

O sistema usa dois modelos de IA para prever a inflação futura:

    🧠 LSTM (Deep Learning) — Rede neural que aprende padrões temporais

    🌳 XGBoost — Modelo que combina múltiplas árvores de decisão

Como Interpretar as Previsões:
🤖 Modelo LSTM
text

🔮 Previsão de Inflação — Próximos 6 meses
┌──────────┬──────────────┐
│   Mês    │ IPC Previsto │
├──────────┼──────────────┤
│ Jul/2026 │    22.1%     │
│ Ago/2026 │    23.8%     │
│ Set/2026 │    25.6%     │
│ Out/2026 │    25.5%     │
│ Nov/2026 │    25.6%     │
│ Dez/2026 │    26.1%     │
└──────────┴──────────────┘

Como ler:

    📈 Se os valores sobem → Espera-se aceleração da inflação

    📉 Se os valores descem → Espera-se desaceleração

    ⚠️ Valores acima de 25% → Alerta de inflação elevada

📊 Modelo XGBoost

Mostra as variáveis mais importantes para prever a inflação:

    Câmbio EUR/AOA — O Euro tem grande influência

    Câmbio USD/AOA — O Dólar também é relevante

    M2 (lag 3) — Oferta monetária de 3 meses atrás

Limitações das Previsões:

    ⚠️ Importante: As previsões são baseadas em dados simulados. Num cenário real, seriam necessários dados oficiais do INE e BNA para maior precisão.

Factores que afectam a precisão:

    Qualidade dos dados de entrada

    Eventos imprevistos (choques externos)

    Mudanças de política monetária

5. Análise de Sentimento (NLP)
O que é?

O sistema lê notícias económicas angolanas e classifica-as automaticamente como:

    🟢 Positivas — Notícias favoráveis à economia

    🔴 Negativas — Notícias desfavoráveis

    ⚪ Neutras — Notícias informativas

Como Funciona:
text

Notícia → Análise de Texto → Classificação
"Kwanza valorizou 2% face ao dólar" → 🟢 Positivo
"Reservas internacionais caem" → 🔴 Negativo
"BNA reúne-se hoje" → ⚪ Neutro

Tom de Política Monetária:

Além do sentimento, o sistema detecta o tom:

    🦅 Hawkish (Restritivo) — Indica possível aumento de juros

        Palavras-chave: "conter inflação", "apertar", "restrição"

    🕊️ Dovish (Expansionista) — Indica possível redução de juros

        Palavras-chave: "estimular", "crescimento", "flexibilização"

Gráficos:
Pizza de Sentimento

Mostra a proporção de notícias positivas, negativas e neutras.
Barras de Tom Monetário

Mostra quantas notícias têm tom hawkish vs dovish.
Interpretação Prática:

    Se +70% das notícias são positivas → Mercado optimista

    Se +50% são negativas → Possível deterioração económica

    Se tom é maioritariamente hawkish → Expectativa de juros mais altos

6. Sistema de Alertas
O que faz?

Monitoriza automaticamente a economia e avisa quando algo importante acontece.
Tipos de Alertas:
Tipo	O que monitoriza	Exemplo
💵 CÂMBIO	Variação do USD/AOA	"USD subiu 3% esta semana"
📈 INFLAÇÃO	Tendência do IPC	"IPC acelerou nos últimos meses"
📰 SENTIMENTO	ISM das notícias	"Sentimento do mercado deteriorou"
💰 RESERVAS	Nível de divisas	"Reservas abaixo de 14 mil milhões"
Níveis de Alerta:

    🔴 Crítico — Requer acção imediata

    🟡 Médio — Monitorizar com atenção

    🟢 Normal — Situação estável

    ℹ️ Informativo — Dados de rotina

Como Usar:

    Navegue até 🔔 Sistema de Alertas

    Clique em 🔄 Actualizar Alertas

    Leia os alertas e as acções recomendadas

Exemplo de Alerta:
text

🔴 ALTO | CÂMBIO
📝 USD/AOA variou +3.2% nos últimos 7 dias
🎯 Acção Recomendada: Monitorar intervenção do BNA
🕐 Detectado em: 15/06/2026 08:30

Alertas Automáticos:

Se configurado, o sistema envia alertas via Telegram automaticamente a cada 6 horas.
7. Dados Brutos
O que contém?

Tabelas completas com todos os dados recolhidos pelo sistema.
Separadores:
Separador	Conteúdo	Actualização
Câmbio	USD/AOA, EUR/AOA	Mensal
IPC	Inflação geral, alimentação, transportes	Mensal
Juros	Taxa BNA, LUIBOR	Mensal
Internacional	Brent, FED Rate	Semanal
Agregados	M2, M3, Reservas	Mensal
Como Exportar:

    Passe o rato sobre a tabela

    Clique no ícone ⬇️ (download)

    Escolha o formato: CSV (Excel) ou JSON

Exemplo de Uso:
csv

timestamp,moeda,valor_compra,valor_venda
2026-06-01,USD,893.92,911.80
2026-06-01,EUR,969.57,989.00

8. Bot do Telegram
Para que serve?

Permite consultar indicadores económicos directamente no Telegram — sem precisar abrir o navegador.
Como Configurar:
Passo 1: Criar o Bot

    Abra o Telegram

    Procure @BotFather

    Envie /newbot

    Escolha um nome: Observatório Monetário

    Guarde o TOKEN fornecido

Passo 2: Configurar o Sistema
bash

# Edite o ficheiro .env
nano .env

# Adicione a linha:
TELEGRAM_TOKEN=SEU_TOKEN_AQUI

Passo 3: Iniciar o Bot
bash

python bot/telegram_bot.py

Comandos Disponíveis:
Comando	Descrição	Exemplo de Resposta
/start	Menu principal	Botões interactivos
/resumo	Resumo económico	USD, Taxa, IPC, Brent
/cambio	Taxas de câmbio	USD/AOA: 893.92
/inflacao	Dados de inflação	IPC: 27.6%
/previsao	Previsões ML	Jul/2026: 22.1%
/alertas	Alertas activos	3 alertas detectados
/ajuda	Lista de comandos	Todos os comandos
Exemplo de Conversa:
text

👤 Utilizador: /resumo

🤖 Bot:
📊 RESUMO ECONÓMICO
📅 15/06/2026 08:30

💵 USD/AOA: 893.92
🏦 Taxa BNA: 19.5%
📈 Inflação: 27.6%
🛢️ Brent: $85.00
💰 Reservas: $14,500M

🔗 Dados em tempo real

9. API REST
Para Programadores:

A API permite aceder aos dados programaticamente — útil para integrar com outros sistemas.
Documentação Interactiva:

Abra no navegador:
text

http://localhost:8001/docs

Endpoints Principais:
Método	Endpoint	Descrição
GET	/api/resumo	Resumo económico
GET	/api/cambio?moeda=USD&dias=30	Taxas de câmbio
GET	/api/inflacao?meses=12	Dados de inflação
GET	/api/previsoes	Previsões ML
GET	/api/alertas	Alertas do sistema
Exemplo de Uso:
Python:
python

import requests

# Obter resumo económico
response = requests.get('http://localhost:8001/api/resumo')
dados = response.json()

print(f"USD/AOA: {dados['usd_aoa']}")
print(f"Taxa BNA: {dados['taxa_bna']}%")
print(f"IPC: {dados['ipc']}%")

cURL (Terminal):
bash

curl http://localhost:8001/api/resumo

JavaScript:
javascript

fetch('http://localhost:8001/api/resumo')
  .then(response => response.json())
  .then(data => console.log(data));

10. Resolução de Problemas
Problemas Comuns e Soluções:
❌ "Streamlit não encontrado"
bash

# Solução: Instalar novamente
pip install streamlit

❌ "Connection refused" ao abrir dashboard
bash

# Solução: Verificar se está na pasta certa
cd observatorio_monetario_angola
source venv/bin/activate
streamlit run app_final_v2.py --server.port 8501

❌ "Modelo LSTM não disponível"
bash

# Solução: Treinar o modelo primeiro
python scripts/ml/modelo_lstm_pytorch.py

❌ "TimescaleDB connection timeout"
bash

# Solução: Verificar VPN/Firewall
# Ou usar banco de dados local

❌ "Porta 8501 já está em uso"
bash

# Solução: Usar outra porta
streamlit run app_final_v2.py --server.port 8502

❌ Gráficos não aparecem
bash

# Solução: Limpar cache do Streamlit
streamlit cache clear

Onde Encontrar Ajuda:

    📖 Este manual — Consulte o índice

    📁 Documentação — Pasta docs/

    💬 Issues — Repositório GitHub

    📧 Email — [umn2020124584@student.umn.edu.ao]

Logs do Sistema:
bash

# Ver logs do Streamlit
cat ~/.streamlit/logs/*.log

# Ver logs da API
cat data/api.log 2>/dev/null

# Ver relatório de saúde
cat data/health_check.json

11. Glossário
Termos Económicos:
Termo	Significado Simples
BNA	Banco Nacional de Angola — O banco central
IPC	Índice de Preços no Consumidor — Mede a inflação
Taxa BNA	Taxa de juro de referência definida pelo BNA
M2	Quantidade de dinheiro em circulação + depósitos
M3	M2 + outros activos financeiros
Brent	Tipo de petróleo de referência internacional
Kwanza (AOA)	Moeda oficial de Angola
LUIBOR	Taxa de juro entre bancos em Angola
Termos Técnicos:
Termo	Significado Simples
Dashboard	Painel visual com indicadores
API	Interface para outros programas acederem aos dados
LSTM	Tipo de rede neural com "memória" para padrões temporais
XGBoost	Algoritmo que combina múltiplos modelos simples
NLP	Processamento de Linguagem Natural — IA que entende texto
ISM	Índice de Surpresa Monetária — Mede o tom das notícias
ETL	Extract, Transform, Load — Processo de recolha de dados
📞 Suporte e Contacto
Dúvidas Frequentes:

P: Com que frequência os dados são actualizados?
R: Depende da fonte:

    Câmbio BNA: Mensalmente

    Petróleo Brent: Semanalmente

    Análise NLP: Diariamente

P: Posso usar o sistema offline?
R: Parcialmente. Precisa de internet para dados actualizados, mas o dashboard funciona offline com dados em cache.

P: Como adicionar novas fontes de dados?
R: Crie um novo coletor em scripts/ingestao/ e adicione a DAG no Airflow.

P: O sistema funciona em Windows?
R: Sim, usando WSL (Windows Subsystem for Linux) ou Podman.
📝 Licença e Créditos

Desenvolvido por: Augusto Dumbo
Disciplina: Aprendizagem Computacional
Instituição: Universidade Mandume Ya Ndemufayo
Orientador: Eng. Abel Zacarias
Ano: 2026

Tecnologias Utilizadas:

    Python • Streamlit • PyTorch • FastAPI

    TimescaleDB • Apache Airflow • MinIO

    Scikit-learn • XGBoost • Plotly

    📘 Fim do Manual do Utilizador

    "A tecnologia ao serviço da transparência económica" 🇦🇴
    EOF

text
   
