"""
API REST do Observatório Monetário Angolano
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.utils.conexoes import ConexaoPostgres
import pandas as pd
import json

app = FastAPI(
    title="Observatório Monetário API",
    description="API de dados económicos de Angola",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "api": "Observatório Monetário Angolano",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/cambio")
def get_cambio(moeda: str = "USD", dias: int = 30):
    """Taxas de câmbio"""
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    df = pd.read_sql(f"""
        SELECT timestamp, moeda, valor_compra, valor_venda
        FROM raw.taxas_cambio
        WHERE moeda = %s
        AND timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn, params=(moeda,))
    
    conn.close()
    return df.to_dict('records')

@app.get("/api/inflacao")
def get_inflacao(meses: int = 12):
    """Dados de inflação (IPC)"""
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    df = pd.read_sql(f"""
        SELECT timestamp, ipc_geral, ipc_alimentacao, ipc_transportes
        FROM raw.ipc
        ORDER BY timestamp DESC
        LIMIT {meses}
    """, conn)
    
    conn.close()
    return df.to_dict('records')

@app.get("/api/alertas")
def get_alertas():
    """Últimos alertas gerados"""
    alertas_path = Path('data/alertas.json')
    
    if alertas_path.exists():
        with open(alertas_path) as f:
            return json.load(f)
    
    return {"total_alertas": 0, "alertas": []}

@app.get("/api/previsoes")
def get_previsoes():
    """Previsões de inflação - Carrega modelo treinado"""
    try:
        import torch
        import joblib
        from scripts.ml.modelo_lstm_pytorch import LSTMModel, ModeloLSTMPyTorch
        
        modelo_path = Path('models/lstm_model.pth')
        scaler_path = Path('models/scaler_lstm.pkl')
        
        if not modelo_path.exists() or not scaler_path.exists():
            return {"error": "Modelo não treinado. Execute: python scripts/ml/modelo_lstm_pytorch.py"}
        
        # Criar wrapper e carregar modelo SALVO
        modelo = ModeloLSTMPyTorch()
        modelo.scaler = joblib.load(scaler_path)
        modelo.modelo = LSTMModel(7)
        modelo.modelo.load_state_dict(torch.load(modelo_path, map_location='cpu'))
        modelo.modelo.eval()
        
        # Fazer previsão
        previsoes = modelo.prever(6)
        
        if previsoes is not None:
            return previsoes.to_dict('records')
        else:
            return {"error": "Não foi possível gerar previsões"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/resumo")
def get_resumo():
    """Resumo económico"""
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    # Último câmbio USD
    cambio = pd.read_sql("""
        SELECT valor_compra FROM raw.taxas_cambio
        WHERE moeda = 'USD'
        ORDER BY timestamp DESC LIMIT 1
    """, conn).iloc[0, 0] if not pd.read_sql("""
        SELECT valor_compra FROM raw.taxas_cambio
        WHERE moeda = 'USD'
        ORDER BY timestamp DESC LIMIT 1
    """, conn).empty else 0
    
    # Última taxa BNA
    juros = pd.read_sql("""
        SELECT taxa_bna FROM raw.taxas_juro
        ORDER BY timestamp DESC LIMIT 1
    """, conn)
    taxa = juros.iloc[0, 0] if not juros.empty else 0
    
    # Último IPC
    ipc_df = pd.read_sql("""
        SELECT ipc_geral FROM raw.ipc
        ORDER BY timestamp DESC LIMIT 1
    """, conn)
    ipc = ipc_df.iloc[0, 0] if not ipc_df.empty else 0
    
    # Brent
    brent_df = pd.read_sql("""
        SELECT brent_crude FROM raw.precos_internacionais
        ORDER BY timestamp DESC LIMIT 1
    """, conn)
    brent = brent_df.iloc[0, 0] if not brent_df.empty else 0
    
    conn.close()
    
    return {
        "data": datetime.now().isoformat(),
        "usd_aoa": float(cambio),
        "taxa_bna": float(taxa),
        "ipc": float(ipc),
        "brent": float(brent)
    }


from fastapi.responses import FileResponse

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico') if Path('favicon.ico').exists() else None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

# Adicionar no final do arquivo (se não existir)
import os

from fastapi.responses import FileResponse

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico') if Path('favicon.ico').exists() else None


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Adicionar no final do arquivo (se não existir)
import os

from fastapi.responses import FileResponse

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico') if Path('favicon.ico').exists() else None


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
