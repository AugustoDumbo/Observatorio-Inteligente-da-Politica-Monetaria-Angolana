#!/bin/bash
# ==========================================
# 🇦🇴 DEPLOY PRODUÇÃO - Observatório Monetário
# ==========================================

set -e  # Parar em caso de erro

echo "🚀 INICIANDO DEPLOY EM PRODUÇÃO"
echo "================================"

# 1. Verificar ambiente
echo ""
echo "📋 Verificando pré-requisitos..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 não encontrado"; exit 1; }
echo "✅ Python3: $(python3 --version)"

command -v podman >/dev/null 2>&1 && echo "✅ Podman disponível" || echo "⚠️ Podman não encontrado (opcional)"

# 2. Ativar ambiente virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "⚠️ Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
fi

# 3. Instalar dependências
echo ""
echo "📦 Instalando dependências..."
pip install -q -r requirements-cloud.txt 2>/dev/null || pip install -q -r requirements.txt

# 4. Verificar conexão com banco
echo ""
echo "🔌 Testando conexão com TimescaleDB..."
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.utils.conexoes import ConexaoPostgres
pg = ConexaoPostgres()
if pg.testar_conexao():
    print('✅ TimescaleDB conectado')
else:
    print('❌ Falha na conexão')
"

# 5. Treinar modelos (se necessário)
echo ""
echo "🤖 Verificando modelos ML..."
if [ ! -f "models/lstm_model.pth" ]; then
    echo "⚠️ Treinando LSTM..."
    python3 scripts/ml/modelo_lstm_pytorch.py
fi
if [ ! -f "models/modelo_inflacao.pkl" ]; then
    echo "⚠️ Treinando XGBoost..."
    python3 scripts/ml/modelo_inflacao.py
fi
echo "✅ Modelos OK"

# 6. Gerar alertas iniciais
echo ""
echo "🔔 Gerando alertas iniciais..."
python3 scripts/alertas/sistema_alertas.py

# 7. Iniciar serviços
echo ""
echo "🌟 INICIANDO SERVIÇOS..."
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔌 API: http://localhost:8001/docs"
echo "🤖 Bot Telegram: python bot/telegram_bot.py"
echo ""
echo "================================"
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"

# 8. Opção de iniciar dashboard
read -p "Iniciar dashboard agora? (s/n): " iniciar
if [ "$iniciar" = "s" ]; then
    streamlit run app_final_v2.py --server.port 8501
fi
