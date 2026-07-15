# 🇦🇴 Observatório Inteligente da Política Monetária Angolana

**Plataforma nacional de monitoramento económico baseada em Inteligência Artificial**

---

## 📊 Funcionalidades

- ✅ **Coleta automática** de dados do BNA, INE e fontes internacionais
- ✅ **Análise NLP** de notícias e comunicados oficiais
- ✅ **Previsões ML** de inflação com LSTM e XGBoost
- ✅ **Alertas inteligentes** em tempo real
- ✅ **Dashboard interativo** com Streamlit
- ✅ **API REST** para integração
- ✅ **Bot Telegram** para consultas rápidas

## 🏗️ Arquitetura

📦 observatorio_monetario_angola
├── 📊 Dashboard (Streamlit)
├── 🔌 API (FastAPI)
├── 🤖 Bot (Telegram)
├── 🗄️ TimescaleDB (Cloud)
├── 💾 MinIO (Storage)
├── ⚙️ Airflow (Orquestração)
└── 🧠 Modelos ML
├── LSTM (PyTorch)
├── XGBoost
└── NLP (Sentimento)

## 🚀 Deploy Rápido

```bash
# 1. Clonar e instalar
git clone https://github.com/AugustoDumbo/Observatorio-Inteligente-da-Politica-Monetaria-Angolana.git
cd observatorio_monetario_angola
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configurar
cp .env.example .env
nano .env  # Adicionar credenciais

# 3. Treinar modelos
python scripts/ml/modelo_lstm_pytorch.py
python scripts/ml/modelo_inflacao.py

# 4. Iniciar
./deploy_producao.sh
📈 Comandos Rápidos
Comando	Descrição
streamlit run app_final_v2.py	Dashboard
python api.py	API REST
python bot/telegram_bot.py	Bot Telegram
python scripts/alertas/sistema_alertas.py	Alertas
./deploy_producao.sh	Deploy completo
🔗 Acessos

    📊 Dashboard: http://localhost:8501

    🔌 API Docs: http://localhost:8001/docs

    ⚙️ Airflow: http://localhost:8082

    💾 MinIO: http://localhost:9001

Desenvolvido com ❤️ para Angola | Tecnologia IA/ML a serviço da política monetária

## 📊 Status dos Dados (Julho 2026)

| Fonte | Status | Valor Atual |
|-------|--------|-------------|
| 💵 USD/AOA | ✅ Real | 924.98 |
| 💶 EUR/AOA | ✅ Real | 1,056.20 |
| 🛢️ Brent | ✅ Real | $85.3 |
| 🏦 FED Funds | ✅ Real | 5.3% |
| 🌍 Inflação Global | ✅ Real | 3.1% |
| 📈 IPC Angola | 🟡 Simulado | ~28% |
| 🏛️ Taxa BNA | 🟡 Simulado | ~19.5% |

*Dados reais via ExchangeRate-API, World Bank, FRED*
