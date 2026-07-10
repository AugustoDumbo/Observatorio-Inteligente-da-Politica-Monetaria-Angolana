"""
Modelo LSTM com PyTorch para Previsão de Inflação
Mais leve e compatível com CPUs antigas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import warnings
import os
import json
warnings.filterwarnings('ignore')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMModel(nn.Module):
    """Arquitetura LSTM para previsão de inflação"""
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout
        )
        self.batch_norm = nn.BatchNorm1d(hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size, 16)
        self.fc2 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_out = lstm_out[:, -1, :]
        out = self.batch_norm(last_out)
        out = self.dropout(out)
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

class ModeloLSTMPyTorch:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.modelo = None
        self.scaler = MinMaxScaler()
        self.modelo_path = Path(__file__).parent.parent.parent / 'models' / 'lstm_model.pth'
        self.scaler_path = Path(__file__).parent.parent.parent / 'models' / 'scaler_lstm.pkl'
        self.lookback = 6
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def carregar_dados(self):
        """Carrega dados do banco para treino"""
        logger.info("📊 Carregando dados para LSTM...")
        
        conn = self.pg.conectar()
        
        query = """
            WITH features AS (
                SELECT 
                    DATE_TRUNC('month', t.timestamp) as mes,
                    AVG(CASE WHEN t.moeda = 'USD' THEN t.valor_compra END) as usd_aoa,
                    AVG(j.taxa_bna) as taxa_bna,
                    AVG(a.m2) as m2,
                    AVG(a.reservas_internacionais) as reservas,
                    AVG(p.brent_crude) as brent,
                    AVG(p.inflacao_global) as inflacao_global,
                    AVG(i.ipc_geral) as ipc
                FROM raw.taxas_cambio t
                LEFT JOIN raw.taxas_juro j ON DATE_TRUNC('month', j.timestamp) = DATE_TRUNC('month', t.timestamp)
                LEFT JOIN raw.agregados_monetarios a ON DATE_TRUNC('month', a.timestamp) = DATE_TRUNC('month', t.timestamp)
                LEFT JOIN raw.precos_internacionais p ON DATE_TRUNC('month', p.timestamp) = DATE_TRUNC('month', t.timestamp)
                LEFT JOIN raw.ipc i ON DATE_TRUNC('month', i.timestamp) = DATE_TRUNC('month', t.timestamp)
                WHERE t.timestamp >= NOW() - INTERVAL '36 months'
                GROUP BY 1
                ORDER BY 1
            )
            SELECT * FROM features WHERE ipc IS NOT NULL
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            logger.warning("⚠️ Sem dados de IPC. Execute o coletor INE primeiro.")
            return None
        
        logger.info(f"✅ {len(df)} meses carregados")
        return df
    
    def preparar_dados(self, df):
        """Prepara dados para PyTorch"""
        logger.info("🔧 Preparando dados...")
        
        feature_cols = ['usd_aoa', 'taxa_bna', 'm2', 'reservas', 'brent', 'inflacao_global']
        
        # Preencher NaN
        df = df.ffill().bfill().fillna(0)
        
        if len(df) < self.lookback + 5:
            logger.error("❌ Dados insuficientes")
            return None
        
        # Normalizar
        dados = self.scaler.fit_transform(df[feature_cols + ['ipc']])
        
        # Criar sequências
        X, y = [], []
        for i in range(self.lookback, len(dados)):
            X.append(dados[i-self.lookback:i])
            y.append(dados[i, -1])
        
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32).reshape(-1, 1)
        
        # Split
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        logger.info(f"✅ {len(X)} sequências | Treino: {len(X_train)} | Teste: {len(X_test)}")
        
        # Converter para tensores PyTorch
        X_train_t = torch.FloatTensor(X_train)
        y_train_t = torch.FloatTensor(y_train)
        X_test_t = torch.FloatTensor(X_test)
        y_test_t = torch.FloatTensor(y_test)
        
        return X_train_t, X_test_t, y_train_t, y_test_t, feature_cols
    
    def treinar(self, X_train, y_train, X_test, y_test, epochs=200):
        """Treina o modelo"""
        logger.info(f"🧠 Treinando LSTM no device: {self.device}...")
        
        input_size = X_train.shape[2]
        self.modelo = LSTMModel(input_size).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.modelo.parameters(), lr=0.001)
        
        # DataLoader
        train_dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        
        best_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        for epoch in range(epochs):
            self.modelo.train()
            train_loss = 0
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.modelo(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validação
            self.modelo.eval()
            with torch.no_grad():
                X_test_d = X_test.to(self.device)
                y_test_d = y_test.to(self.device)
                y_pred = self.modelo(X_test_d)
                val_loss = criterion(y_pred, y_test_d).item()
            
            # Early stopping
            if val_loss < best_loss:
                best_loss = val_loss
                patience_counter = 0
                # Salvar melhor modelo
                torch.save(self.modelo.state_dict(), self.modelo_path)
            else:
                patience_counter += 1
            
            if patience_counter >= patience:
                logger.info(f"⏹️ Early stopping na época {epoch+1}")
                break
            
            if (epoch + 1) % 20 == 0:
                logger.info(f"  Época {epoch+1}/{epochs} | Loss: {train_loss/len(train_loader):.4f} | Val Loss: {val_loss:.4f}")
        
        # Carregar melhor modelo
        self.modelo.load_state_dict(torch.load(self.modelo_path))
        
        # Avaliar
        self.modelo.eval()
        with torch.no_grad():
            y_pred = self.modelo(X_test.to(self.device)).cpu().numpy()
            y_true = y_test.cpu().numpy()
            
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            r2 = r2_score(y_true, y_pred)
        
        logger.info(f"✅ Treino concluído!")
        logger.info(f"📊 MAE: {mae:.4f}")
        logger.info(f"📊 RMSE: {rmse:.4f}")
        logger.info(f"📊 R²: {r2:.4f}")
        
        # Salvar scaler
        import joblib
        joblib.dump(self.scaler, self.scaler_path)
        
        return {'mae': mae, 'rmse': rmse, 'r2': r2}
    
    def prever(self, meses=6):
        """Previsão para próximos meses"""
        logger.info(f"🔮 Prevendo {meses} meses...")
        
        if self.modelo is None:
            try:
                self.modelo = LSTMModel(7)  # 6 features + IPC
                self.modelo.load_state_dict(torch.load(self.modelo_path))
                self.modelo.eval()
                logger.info("📂 Modelo carregado")
            except:
                logger.error("❌ Modelo não encontrado")
                return None
        
        df = self.carregar_dados()
        if df is None:
            return None
        
        feature_cols = ['usd_aoa', 'taxa_bna', 'm2', 'reservas', 'brent', 'inflacao_global']
        df = df.ffill().bfill().fillna(0)
        
        # Preparar última sequência
        dados = self.scaler.transform(df[feature_cols + ['ipc']])
        ultima_seq = dados[-self.lookback:]
        
        previsoes = []
        seq_atual = torch.FloatTensor(ultima_seq).unsqueeze(0)
        
        self.modelo.eval()
        with torch.no_grad():
            for i in range(meses):
                pred = self.modelo(seq_atual).item()
                
                # Criar nova linha
                nova = seq_atual[0, -1].clone()
                nova[-1] = pred
                
                # Atualizar sequência
                seq_atual = torch.cat([seq_atual[:, 1:, :], nova.unsqueeze(0).unsqueeze(0)], dim=1)
                
                # Desnormalizar (aproximado)
                previsoes.append({
                    'mes': (datetime.now() + timedelta(days=30*(i+1))).strftime('%Y-%m'),
                    'ipc_previsto': round(pred * 30, 1)  # Aproximação
                })
        
        return pd.DataFrame(previsoes)
    
    def executar_pipeline(self):
        """Pipeline completo"""
        logger.info("🚀 PIPELINE LSTM (PyTorch)")
        logger.info("=" * 60)
        
        df = self.carregar_dados()
        if df is None:
            return
        
        dados = self.preparar_dados(df)
        if dados is None:
            return
        
        X_train, X_test, y_train, y_test, features = dados
        metricas = self.treinar(X_train, y_train, X_test, y_test)
        
        previsoes = self.prever(6)
        if previsoes is not None:
            logger.info("\n🔮 PREVISÕES:")
            for _, row in previsoes.iterrows():
                logger.info(f"  {row['mes']}: {row['ipc_previsto']}%")
        
        logger.info("\n✅ PIPELINE CONCLUÍDO!")
        return metricas, previsoes

if __name__ == "__main__":
    modelo = ModeloLSTMPyTorch()
    metricas, previsoes = modelo.executar_pipeline()
    
    if metricas:
        print("\n📊 RESULTADOS FINAIS:")
        print(f"  MAE: {metricas['mae']:.4f}")
        print(f"  RMSE: {metricas['rmse']:.4f}")
        print(f"  R²: {metricas['r2']:.4f}")
