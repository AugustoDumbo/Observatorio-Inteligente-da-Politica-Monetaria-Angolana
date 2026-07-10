FROM python:3.12-slim

LABEL maintainer="Observatório Monetário Angolano"
LABEL description="Plataforma de monitoramento económico baseada em IA"

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY . .

# Criar diretórios necessários
RUN mkdir -p data models logs

# Portas
EXPOSE 8501 8000

# Comando padrão
CMD ["streamlit", "run", "app_final_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
