"""
Modelo LSTM para Previsão de Inflação
Deep Learning com redes neurais recorrentes
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import logging
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Importar TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModeloLSTM:
    def __init__(self):
        self.pg = ConexaoPostgres()
        self.modelo = None
        self.scaler = MinMaxScaler()
        self.modelo_path = Path(__file__).parent.parent.parent / 'models' / 'lstm_inflacao.h5'
        self.lookback = 6  # Meses para prever
        
    def carregar_dados(self):
        """Carrega dados do banco para treino"""
        logger.info("📊 Carregando dados para LSTM...")
        
        conn = self.pg.conectar()
        
        # Query para pegar todas as features
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
    
    def preparar_dados_lstm(self, df):
        """Prepara dados no formato para LSTM"""
        logger.info("🔧 Preparando sequências para LSTM...")
        
        # Features para o modelo
        feature_cols = ['usd_aoa', 'taxa_bna', 'm2', 'reservas', 'brent', 'inflacao_global']
        
        # Preencher NaN
        df = df.ffill().bfill()
        
        # Normalizar
        dados_normalizados = self.scaler.fit_transform(df[feature_cols + ['ipc']])
        
        # Criar sequências
        X, y = [], []
        for i in range(self.lookback, len(dados_normalizados)):
            X.append(dados_normalizados[i-self.lookback:i])
            y.append(dados_normalizados[i, -1])  # Última coluna é IPC
        
        X = np.array(X)
        y = np.array(y)
        
        # Split treino/teste
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        logger.info(f"✅ Sequências: {X.shape[0]} amostras, {X.shape[1]} timesteps, {X.shape[2]} features")
        logger.info(f"   Treino: {len(X_train)} | Teste: {len(X_test)}")
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def construir_modelo(self, input_shape):
        """Constrói arquitetura LSTM"""
        logger.info("🧠 Construindo modelo LSTM...")
        
        self.modelo = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.2),
            
            LSTM(32, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        self.modelo.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info(f"✅ Modelo construído: {self.modelo.count_params()} parâmetros")
        return self.modelo
    
    def treinar(self, X_train, y_train, X_test, y_test):
        """Treina o modelo LSTM"""
        logger.info("🎯 Iniciando treino LSTM...")
        
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        history = self.modelo.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=100,
            batch_size=4,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Avaliar
        y_pred = self.modelo.predict(X_test, verbose=0)
        
        # Desnormalizar para calcular métricas
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        logger.info(f"✅ Treino concluído!")
        logger.info(f"📊 MAE: {mae:.4f}")
        logger.info(f"📊 RMSE: {rmse:.4f}")
        logger.info(f"📊 Épocas: {len(history.history['loss'])}")
        
        # Salvar modelo
        self.modelo.save(self.modelo_path)
        logger.info(f"💾 Modelo salvo: {self.modelo_path}")
        
        return history
    
    def prever(self, meses=6):
        """Faz previsões para próximos meses"""
        logger.info(f"🔮 Prevendo {meses} meses à frente...")
        
        if self.modelo is None:
            try:
                self.modelo = tf.keras.models.load_model(self.modelo_path)
                logger.info("📂 Modelo carregado")
            except:
                logger.error("❌ Modelo não encontrado. Treine primeiro.")
                return None
        
        # Carregar dados mais recentes
        df = self.carregar_dados()
        if df is None:
            return None
        
        feature_cols = ['usd_aoa', 'taxa_bna', 'm2', 'reservas', 'brent', 'inflacao_global']
        df = df.ffill().bfill()
        
        # Normalizar
        dados_norm = self.scaler.transform(df[feature_cols + ['ipc']])
        
        # Última sequência
        ultima_seq = dados_norm[-self.lookback:]
        
        previsoes = []
        seq_atual = ultima_seq.copy()
        
        for i in range(meses):
            # Prever próximo valor
            pred = self.modelo.predict(seq_atual.reshape(1, self.lookback, -1), verbose=0)[0, 0]
            
            # Criar nova linha com previsão
            nova_linha = seq_atual[-1].copy()
            nova_linha[-1] = pred  # Atualizar IPC
            
            # Atualizar sequência
            seq_atual = np.vstack([seq_atual[1:], nova_linha])
            
            previsoes.append({
                'mes': (datetime.now() + timedelta(days=30*(i+1))).strftime('%Y-%m'),
                'ipc_previsto': float(pred * 100)  # Desnormalizar aproximado
            })
        
        return pd.DataFrame(previsoes)
    
    def executar_pipeline(self):
        """Pipeline completo LSTM"""
        logger.info("🚀 INICIANDO PIPELINE LSTM DE PREVISÃO DE INFLAÇÃO")
        logger.info("=" * 60)
        
        # Carregar dados
        df = self.carregar_dados()
        if df is None:
            return
        
        # Preparar dados
        X_train, X_test, y_train, y_test, features = self.preparar_dados_lstm(df)
        
        # Construir modelo
        self.construir_modelo((self.lookback, X_train.shape[2]))
        
        # Treinar
        self.treinar(X_train, y_train, X_test, y_test)
        
        # Prever
        previsoes = self.prever(6)
        
        if previsoes is not None:
            logger.info("\n🔮 PREVISÕES LSTM:")
            for _, row in previsoes.iterrows():
                logger.info(f"  {row['mes']}: {row['ipc_previsto']:.1f}%")
        
        logger.info("\n✅ PIPELINE LSTM CONCLUÍDO!")

import os
if __name__ == "__main__":
    modelo = ModeloLSTM()
    modelo.executar_pipeline()
