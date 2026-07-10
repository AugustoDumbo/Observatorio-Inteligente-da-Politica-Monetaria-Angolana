"""
🇦🇴 OBSERVATÓRIO INTELIGENTE DA POLÍTICA MONETÁRIA ANGOLANA
Dashboard Final Integrado
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scripts.utils.conexoes import ConexaoPostgres

# ===== CONFIGURAÇÃO =====
st.set_page_config(
    page_title="Observatório Monetário | BNA",
    page_icon="🇦🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS CUSTOMIZADO =====
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1a237e; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 10px; color: white; 
    }
    .alert-hawkish { background: #ffebee; padding: 10px; border-left: 5px solid #e74c3c; }
    .alert-dovish { background: #e8f5e9; padding: 10px; border-left: 5px solid #27ae60; }
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.image("https://www.bna.ao/assets/images/logo.png", width=100)  # Logo BNA
    st.markdown("# 🇦🇴 Observatório")
    st.markdown("---")
    
    periodo = st.selectbox("📅 Período de Análise", 
                          ["7 dias", "30 dias", "90 dias", "6 meses", "1 ano"])
    
    dias_map = {"7 dias": 7, "30 dias": 30, "90 dias": 90, "6 meses": 180, "1 ano": 365}
    dias = dias_map[periodo]
    
    st.markdown("---")
    st.markdown("### 📊 Módulos Ativos")
    st.success("✅ Coleta BNA (Mensal)")
    st.success("✅ Dados Internacionais (Semanal)")
    st.success("✅ Análise NLP (Diária)")
    st.success("✅ Modelo Preditivo ML")
    
    st.markdown("---")
    st.caption(f"🕐 Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ===== CARREGAR DADOS =====
@st.cache_data(ttl=300)
def carregar_dados(dias):
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    cambio = pd.read_sql(f"""
        SELECT timestamp, moeda, valor_compra 
        FROM raw.taxas_cambio 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    juros = pd.read_sql(f"""
        SELECT timestamp, taxa_bna 
        FROM raw.taxas_juro 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    agregados = pd.read_sql(f"""
        SELECT timestamp, m2, m3, reservas_internacionais 
        FROM raw.agregados_monetarios 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    internacional = pd.read_sql(f"""
        SELECT timestamp, brent_crude, federal_funds_rate, inflacao_global 
        FROM raw.precos_internacionais 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    # Dados NLP
    try:
        sentimento = pd.read_sql(f"""
            SELECT 
                DATE(timestamp) as data,
                sentimento, tom_monetario,
                COUNT(*) as volume
            FROM raw.analise_sentimento
            WHERE timestamp >= NOW() - INTERVAL '{dias} days'
            GROUP BY 1, 2, 3
            ORDER BY 1
        """, conn)
    except:
        sentimento = pd.DataFrame()
    
    conn.close()
    return cambio, juros, agregados, internacional, sentimento

# Carregar
cambio, juros, agregados, internacional, sentimento = carregar_dados(dias)

# ===== HEADER =====
st.markdown('<p class="main-header">🇦🇴 Observatório Inteligente da Política Monetária Angolana</p>', 
           unsafe_allow_html=True)
st.markdown(f"*Plataforma nacional de monitoramento económico baseada em IA • {periodo} de dados*")
st.markdown("---")

# ===== MÉTRICAS EM TEMPO REAL =====
if not cambio.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        usd = cambio[cambio['moeda']=='USD']['valor_compra']
        ultimo = usd.iloc[-1] if not usd.empty else 0
        variacao = ((usd.iloc[-1] - usd.iloc[0]) / usd.iloc[0] * 100) if len(usd) > 1 else 0
        st.metric("💵 USD/AOA", f"{ultimo:,.2f}", f"{variacao:+.2f}%")
    
    with col2:
        eur = cambio[cambio['moeda']=='EUR']['valor_compra']
        ultimo_eur = eur.iloc[-1] if not eur.empty else 0
        st.metric("💶 EUR/AOA", f"{ultimo_eur:,.2f}")
    
    with col3:
        taxa = juros['taxa_bna'].iloc[-1] if not juros.empty else 0
        st.metric("🏦 Taxa BNA", f"{taxa:.1f}%")
    
    with col4:
        brent = internacional['brent_crude'].iloc[-1] if not internacional.empty else 0
        st.metric("🛢️ Brent", f"${brent:.2f}")
    
    with col5:
        if not agregados.empty:
            reservas = agregados['reservas_internacionais'].iloc[-1] / 1000
            st.metric("💰 Reservas", f"${reservas:.1f}B")

st.markdown("---")

# ===== GRÁFICOS PRINCIPAIS =====
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📈 Taxa de Câmbio USD/AOA")
    if not cambio.empty:
        usd = cambio[cambio['moeda']=='USD']
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=usd['timestamp'], y=usd['valor_compra'],
            mode='lines+markers',
            line=dict(color='#2196F3', width=2),
            fill='tozeroy',
            fillcolor='rgba(33,150,243,0.1)',
            name='USD/AOA'
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0),
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

with col_dir:
    st.subheader("🏦 Política Monetária")
    if not juros.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=juros['timestamp'], y=juros['taxa_bna'],
            mode='lines+markers',
            line=dict(color='#E91E63', width=3),
            marker=dict(size=8),
            name='Taxa BNA'
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0),
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

# ===== SEGUNDA LINHA =====
col_esq2, col_dir2 = st.columns(2)

with col_esq2:
    st.subheader("🛢️ Petróleo & Inflação Global")
    if not internacional.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=internacional['timestamp'], y=internacional['brent_crude'],
            name="Brent (USD)", line=dict(color='#FF9800', width=2)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=internacional['timestamp'], y=internacional['inflacao_global'],
            name="Inflação Global (%)", line=dict(color='#F44336', width=2, dash='dot')
        ), secondary_y=True)
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0),
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

with col_dir2:
    st.subheader("📊 Análise de Sentimento (NLP)")
    if not sentimento.empty:
        # Calcular distribuição
        sent_agg = sentimento.groupby('data').agg({
            'volume': 'sum',
            'sentimento': lambda x: x.value_counts().to_dict()
        }).reset_index()
        
        fig = go.Figure()
        cores = {'positivo': '#4CAF50', 'negativo': '#F44336', 'neutro': '#9E9E9E'}
        
        for sent in ['positivo', 'negativo', 'neutro']:
            dados_sent = sentimento[sentimento['sentimento'] == sent]
            if not dados_sent.empty:
                fig.add_trace(go.Bar(
                    name=sent.capitalize(),
                    x=dados_sent['data'],
                    y=dados_sent['volume'],
                    marker_color=cores.get(sent, '#999')
                ))
        
        fig.update_layout(barmode='stack', height=350, 
                         margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📰 Execute o analisador NLP para ver dados de sentimento")

st.markdown("---")

# ===== ÍNDICE DE SURPRESA MONETÁRIA =====
st.subheader("🎯 Índice de Surpresa Monetária (ISM)")

if not sentimento.empty:
    ism_col1, ism_col2, ism_col3 = st.columns([2, 1, 1])
    
    hawkish = sentimento[sentimento['tom_monetario']=='hawkish']['volume'].sum()
    dovish = sentimento[sentimento['tom_monetario']=='dovish']['volume'].sum()
    total = hawkish + dovish
    ism = (hawkish - dovish) / total if total > 0 else 0
    
    with ism_col1:
        st.metric("ISM", f"{ism:.3f}", 
                 delta="Tendência Hawkish 🦅" if ism > 0.2 else 
                       ("Tendência Dovish 🕊️" if ism < -0.2 else "Neutro ⚖️"))
        st.progress(abs(ism))
    
    with ism_col2:
        st.metric("🦅 Hawkish", int(hawkish))
        st.metric("🕊️ Dovish", int(dovish))
    
    with ism_col3:
        if ism > 0.3:
            st.warning("⚠️ Possível aperto monetário")
        elif ism < -0.3:
            st.info("ℹ️ Possível flexibilização")
        else:
            st.success("✅ Expectativas estáveis")
else:
    st.info("Dados NLP não disponíveis")

st.markdown("---")

# ===== PREVISÕES ML =====
st.subheader("🔮 Previsão de Inflação (Machine Learning)")

try:
    from scripts.ml.modelo_inflacao import ModeloPrevisaoInflacao
    modelo = ModeloPrevisaoInflacao()
    
    # Tentar carregar modelo treinado
    if modelo.modelo_path.exists():
        previsoes = modelo.prever_proximos_meses(6)
        
        col_pred1, col_pred2 = st.columns([2, 1])
        
        with col_pred1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=previsoes['mes'], 
                y=previsoes['ipc_previsto'],
                mode='lines+markers',
                name='IPC Previsto',
                line=dict(color='#E91E63', width=3, dash='dash'),
                marker=dict(size=12)
            ))
            # Intervalo de confiança
            fig.add_trace(go.Scatter(
                x=previsoes['mes'].tolist() + previsoes['mes'].tolist()[::-1],
                y=previsoes['intervalo_superior'].tolist() + previsoes['intervalo_inferior'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(233,30,99,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Intervalo ±1.5pp'
            ))
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        with col_pred2:
            st.metric("Próximo Mês", 
                     f"{previsoes['ipc_previsto'].iloc[0]:.1f}%",
                     f"{previsoes['ipc_previsto'].iloc[-1] - previsoes['ipc_previsto'].iloc[0]:+.1f}pp em 6m")
            st.metric("Intervalo", 
                     f"±1.5pp",
                     "95% confiança")
            st.caption("Modelo: XGBoost + Features Econômicas")
    else:
        st.info("🤖 Execute o treino do modelo primeiro: `python scripts/ml/modelo_inflacao.py`")
except Exception as e:
    st.warning(f"Modelo ML não disponível: {e}")

st.markdown("---")

# ===== RODAPÉ =====
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p>🇦🇴 <strong>Observatório Inteligente da Política Monetária Angolana</strong></p>
    <p>Plataforma baseada em IA para monitoramento económico | v1.0</p>
    <p>Fontes: BNA • INE • World Bank • FRED | Tecnologia: Python • ML • NLP • Airflow</p>
</div>
""", unsafe_allow_html=True)
