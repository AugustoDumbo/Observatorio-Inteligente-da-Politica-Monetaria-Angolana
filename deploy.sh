#!/bin/bash
# Script de deploy do Observatório Monetário

echo "🇦🇴 Deploy do Observatório Monetário Angolano"
echo "============================================"

# 1. Verificar ambiente
echo "📋 Verificando ambiente..."
command -v podman >/dev/null 2>&1 || { echo "❌ Podman não encontrado"; exit 1; }
echo "✅ Podman encontrado"

# 2. Build da imagem
echo "🔨 Construindo imagem..."
podman build -t observatorio-monetario:latest .

# 3. Parar containers antigos
echo "🛑 Parando containers antigos..."
podman stop observatorio_dashboard observatorio_api 2>/dev/null
podman rm observatorio_dashboard observatorio_api 2>/dev/null

# 4. Iniciar containers
echo "🚀 Iniciando containers..."
podman-compose up -d

# 5. Verificar status
echo "📊 Status dos containers:"
podman ps --filter "name=observatorio"

echo ""
echo "✅ Deploy concluído!"
echo "📊 Dashboard: http://localhost:8501"
echo "🔌 API: http://localhost:8001/docs"
