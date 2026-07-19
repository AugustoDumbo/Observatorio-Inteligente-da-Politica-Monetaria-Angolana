"""
🇦🇴 OBSERVATÓRIO MONETÁRIO - Versão 2.0
Dashboard completo com ML, NLP e Alertas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres
import joblib
import torch
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Observatório Monetário Angolano ",
    page_icon="🇦🇴",
    layout="wide"
)

# ===== CARREGAR MODELOS (Cache) =====
@st.cache_resource
def carregar_modelo_lstm():
    """Carrega modelo LSTM treinado"""
    try:
        from scripts.ml.modelo_lstm_pytorch import LSTMModel, ModeloLSTMPyTorch
        
        modelo_path = Path('models/lstm_model.pth')
        scaler_path = Path('models/scaler_lstm.pkl')
        
        if not modelo_path.exists() or not scaler_path.exists():
            return None, "Modelo não encontrado. Execute: python scripts/ml/modelo_lstm_pytorch.py"
        
        # Criar instância e carregar
        modelo_wrapper = ModeloLSTMPyTorch()
        modelo_wrapper.scaler = joblib.load(scaler_path)
        modelo_wrapper.modelo = LSTMModel(7)  # 6 features + IPC
        modelo_wrapper.modelo.load_state_dict(torch.load(modelo_path, map_location='cpu'))
        modelo_wrapper.modelo.eval()
        
        return modelo_wrapper, "Modelo LSTM carregado com sucesso!"
    except Exception as e:
        return None, f"Erro ao carregar: {str(e)}"

@st.cache_resource
def carregar_modelo_xgboost():
    """Carrega modelo XGBoost treinado"""
    try:
        modelo_path = Path('models/modelo_inflacao.pkl')
        features_path = Path('models/features.pkl')
        
        if modelo_path.exists():
            modelo = joblib.load(modelo_path)
            features = joblib.load(features_path) if features_path.exists() else []
            return modelo, features
        return None, []
    except Exception as e:
        return None, []

# ===== SIDEBAR =====
with st.sidebar:
    st.title("🇦🇴 Observatório")
    st.markdown("---")
    
    pagina = st.radio("📊 Navegação", [
        "📈 Dashboard Principal",
        "🔮 Previsões ML",
        "📰 Análise NLP",
        "🔔 Sistema de Alertas",
        "📊 Dados Brutos"
    ])
    
    st.markdown("---")
    st.metric("🕐 Atualização", datetime.now().strftime('%H:%M'))
    
    st.markdown("### 🟢 Sistemas Ativos")
    st.success("Coleta BNA")
    st.success("Dados Internacionais")
    st.success("NLP + Sentimento")
    st.success("LSTM + XGBoost")
    st.success("Alertas Inteligentes")

# ===== CARREGAR DADOS =====
@st.cache_data(ttl=60)
def carregar_tudo():
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    cambio = pd.read_sql("SELECT * FROM raw.taxas_cambio ORDER BY timestamp DESC LIMIT 100", conn)
    juros = pd.read_sql("SELECT * FROM raw.taxas_juro ORDER BY timestamp DESC LIMIT 50", conn)
    ipc = pd.read_sql("SELECT * FROM raw.ipc ORDER BY timestamp DESC LIMIT 50", conn)
    internacional = pd.read_sql("SELECT * FROM raw.precos_internacionais ORDER BY timestamp DESC LIMIT 50", conn)
    agregados = pd.read_sql("SELECT * FROM raw.agregados_monetarios ORDER BY timestamp DESC LIMIT 50", conn)
    
    try:
        sentimento = pd.read_sql("""
            SELECT * FROM raw.analise_sentimento 
            ORDER BY timestamp DESC LIMIT 100
        """, conn)
    except:
        sentimento = pd.DataFrame()
    
    conn.close()
    return cambio, juros, ipc, internacional, agregados, sentimento

cambio, juros, ipc, internacional, agregados, sentimento = carregar_tudo()

# ===== PÁGINAS =====

if pagina == "📈 Dashboard Principal":
    st.title("🇦🇴 Dashboard Principal")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        usd = cambio[cambio['moeda']=='USD']['valor_compra'].iloc[0]
        st.metric("USD/AOA", f"{usd:,.2f}")
    
    with col2:
        taxa = juros['taxa_bna'].iloc[0] if not juros.empty else 0
        st.metric("Taxa BNA", f"{taxa:.1f}%")
    
    with col3:
        inflacao = ipc['ipc_geral'].iloc[0] if not ipc.empty else 0
        st.metric("Inflação (IPC)", f"{inflacao:.1f}%")
    
    with col4:
        brent = internacional['brent_crude'].iloc[0] if not internacional.empty else 0
        st.metric("Petróleo Brent", f"${brent:.2f}")
    
    st.markdown("---")
    
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        st.subheader("📈 Inflação vs Taxa de Juro")
        fig = go.Figure()
        if not ipc.empty:
            fig.add_trace(go.Scatter(x=ipc['timestamp'], y=ipc['ipc_geral'], 
                                    name='IPC', line=dict(color='red', width=2)))
        if not juros.empty:
            fig.add_trace(go.Scatter(x=juros['timestamp'], y=juros['taxa_bna'], 
                                    name='Taxa BNA', line=dict(color='blue', width=2), yaxis='y2'))
        fig.update_layout(height=350, yaxis2=dict(overlaying='y', side='right'))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_dir:
        st.subheader("💵 Taxa de Câmbio")
        usd_data = cambio[cambio['moeda']=='USD']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=usd_data['timestamp'], y=usd_data['valor_compra'],
                                fill='tozeroy', line=dict(color='green', width=2)))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

elif pagina == "🔮 Previsões ML":
    st.title("🔮 Previsões de Inflação")
    st.markdown("---")
    
    # ===== LSTM =====
    st.subheader("🤖 Modelo LSTM (Deep Learning)")
    
    modelo_lstm, msg_lstm = carregar_modelo_lstm()
    
    if modelo_lstm is not None:
        st.success(msg_lstm)
        
        try:
            previsoes = modelo_lstm.prever(6)
            
            if previsoes is not None and not previsoes.empty:
                # Gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=previsoes['mes'], y=previsoes['ipc_previsto'],
                    mode='lines+markers', name='IPC Previsto',
                    line=dict(color='#E91E63', width=3),
                    marker=dict(size=12)
                ))
                fig.update_layout(
                    title='Projeção IPC - Próximos 6 Meses (LSTM)',
                    height=400,
                    yaxis_title='IPC (%)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela
                st.dataframe(previsoes.style.highlight_max(subset=['ipc_previsto'], color='#ffcdd2'))
            else:
                st.warning("Não foi possível gerar previsões")
        except Exception as e:
            st.error(f"Erro na previsão: {e}")
    else:
        st.warning(msg_lstm)
        st.info("Execute no terminal: python scripts/ml/modelo_lstm_pytorch.py")
    
    st.markdown("---")
    
    # ===== XGBoost =====
    st.subheader("📊 Modelo XGBoost")
    
    modelo_xgb, features = carregar_modelo_xgboost()
    
    if modelo_xgb is not None:
        st.success("✅ Modelo XGBoost carregado")
        st.write(f"**Features utilizadas:** {len(features)} variáveis")
        
        # Mostrar algumas features
        with st.expander("Ver features"):
            for i, feat in enumerate(features[:15]):
                st.write(f"{i+1}. {feat}")
    else:
        st.info("Modelo XGBoost não encontrado. Execute: python scripts/ml/modelo_inflacao.py")

elif pagina == "📰 Análise NLP":
    st.title("📰 Análise de Sentimento")
    st.markdown("---")
    
    if not sentimento.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição de Sentimento")
            sent_counts = sentimento['sentimento'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=sent_counts.index, 
                values=sent_counts.values,
                marker=dict(colors=['#4CAF50', '#F44336', '#9E9E9E'])
            )])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Tom de Política Monetária")
            tom_counts = sentimento['tom_monetario'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=tom_counts.index, 
                y=tom_counts.values,
                marker_color=['#2196F3', '#FF9800', '#4CAF50']
            )])
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Últimas Análises")
        st.dataframe(sentimento[['timestamp', 'sentimento', 'tom_monetario', 'confianca']].head(20))
    else:
        st.info("Execute o analisador NLP: python scripts/nlp/analisador_sentimento.py")

elif pagina == "🔔 Sistema de Alertas":
    st.title("🔔 Alertas Inteligentes")
    st.markdown("---")
    
    try:
        from scripts.alertas.sistema_alertas import SistemaAlertas
        
        # Botão para atualizar
        if st.button("🔄 Atualizar Alertas"):
            st.cache_data.clear()
        
        sistema = SistemaAlertas()
        relatorio = sistema.gerar_relatorio()
        
        if relatorio['total_alertas'] > 0:
            st.warning(f"⚠️ {relatorio['total_alertas']} alertas ativos - {relatorio['resumo']}")
        else:
            st.success(f"✅ {relatorio['resumo']}")
        
        for alerta in relatorio['alertas']:
            with st.expander(f"{alerta['nivel']} | {alerta['tipo']}"):
                st.write(f"**📝 {alerta['mensagem']}**")
                st.write(f"**🎯 Ação Recomendada:** {alerta['acao']}")
                st.caption(f"Detectado em: {alerta['timestamp'][:19]}")
    except Exception as e:
        st.error(f"Erro ao gerar alertas: {e}")

elif pagina == "📊 Dados Brutos":
    st.title("📊 Dados Brutos")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Câmbio", "IPC", "Juros", "Internacional", "Agregados"])
    
    with tab1:
        st.dataframe(cambio, use_container_width=True)
    with tab2:
        st.dataframe(ipc, use_container_width=True)
    with tab3:
        st.dataframe(juros, use_container_width=True)
    with tab4:
        st.dataframe(internacional, use_container_width=True)
    with tab5:
        st.dataframe(agregados, use_container_width=True)

st.markdown("---")
st.caption("🇦🇴 Observatório Inteligente da Política Monetária Angolana | Powered by Augusto Dumbo/ML")
