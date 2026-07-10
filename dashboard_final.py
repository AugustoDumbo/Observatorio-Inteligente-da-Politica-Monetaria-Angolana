"""
Dashboard Completo - Observatório Monetário Angolano
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scripts.utils.conexoes import ConexaoPostgres

st.set_page_config(
    page_title="Observatório Monetário Angolano",
    page_icon="🇦🇴",
    layout="wide"
)

# Sidebar
st.sidebar.title("🇦🇴 Observatório Monetário")
st.sidebar.markdown("---")
periodo = st.sidebar.selectbox("Período", ["7 dias", "30 dias", "90 dias", "1 ano"])
dias_map = {"7 dias": 7, "30 dias": 30, "90 dias": 90, "1 ano": 365}
dias = dias_map[periodo]

@st.cache_data(ttl=300)
def carregar_dados(dias):
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    # Dados monetários
    cambio = pd.read_sql(f"""
        SELECT timestamp, moeda, valor_compra 
        FROM raw.taxas_cambio 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    juros = pd.read_sql(f"""
        SELECT * FROM raw.taxas_juro 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    agregados = pd.read_sql(f"""
        SELECT * FROM raw.agregados_monetarios 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    internacional = pd.read_sql(f"""
        SELECT * FROM raw.precos_internacionais 
        WHERE timestamp >= NOW() - INTERVAL '{dias} days'
        ORDER BY timestamp
    """, conn)
    
    # Análise NLP
    try:
        sentimento = pd.read_sql(f"""
            SELECT 
                DATE(timestamp) as data,
                sentimento,
                tom_monetario,
                COUNT(*) as volume
            FROM raw.analise_sentimento
            WHERE timestamp >= NOW() - INTERVAL '{dias} days'
            GROUP BY DATE(timestamp), sentimento, tom_monetario
            ORDER BY data
        """, conn)
    except:
        sentimento = pd.DataFrame()
    
    conn.close()
    return cambio, juros, agregados, internacional, sentimento

# Carregar dados
cambio, juros, agregados, internacional, sentimento = carregar_dados(dias)

# Título principal
st.title("🇦🇴 Observatório Inteligente da Política Monetária Angolana")
st.markdown(f"*Dados dos últimos {periodo} - Atualizado em tempo real*")
st.markdown("---")

# Métricas rápidas
if not cambio.empty and not juros.empty:
    met1, met2, met3, met4, met5 = st.columns(5)
    
    with met1:
        ultimo_usd = cambio[cambio['moeda']=='USD']['valor_compra'].iloc[-1]
        st.metric("USD/AOA", f"{ultimo_usd:,.2f}", "💵")
    
    with met2:
        ultima_taxa = juros['taxa_bna'].iloc[-1]
        st.metric("Taxa BNA", f"{ultima_taxa:.1f}%", "🏦")
    
    with met3:
        ultimo_brent = internacional['brent_crude'].iloc[-1] if not internacional.empty else 0
        st.metric("Petróleo Brent", f"${ultimo_brent:.2f}", "🛢️")
    
    with met4:
        if not agregados.empty:
            reservas = agregados['reservas_internacionais'].iloc[-1]
            st.metric("Reservas Int.", f"${reservas:,.0f}M", "💰")
    
    with met5:
        if not sentimento.empty:
            total_noticias = sentimento['volume'].sum()
            st.metric("Notícias (NLP)", int(total_noticias), "📰")

st.markdown("---")

# Gráficos principais
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Taxa de Câmbio USD/AOA")
    if not cambio.empty:
        usd = cambio[cambio['moeda']=='USD']
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=usd['timestamp'], y=usd['valor_compra'],
            mode='lines+markers', name='USD/AOA',
            line=dict(color='#2E86C1', width=2)
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de câmbio")

with col2:
    st.subheader("🏦 Taxa BNA vs Inflação")
    if not juros.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=juros['timestamp'], y=juros['taxa_bna'],
            mode='lines+markers', name='Taxa BNA',
            line=dict(color='#E74C3C', width=3)
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

# Segunda linha
col3, col4 = st.columns(2)

with col3:
    st.subheader("🛢️ Preço do Petróleo Brent")
    if not internacional.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=internacional['timestamp'], y=internacional['brent_crude'],
            mode='lines+markers', name='Brent',
            line=dict(color='#F39C12', width=2),
            fill='tozeroy', fillcolor='rgba(243,156,18,0.1)'
        ))
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("📊 Análise de Sentimento (NLP)")
    if not sentimento.empty:
        pivot = sentimento.pivot_table(
            values='volume', index='data', 
            columns='sentimento', aggfunc='sum', fill_value=0
        )
        
        fig = go.Figure()
        cores = {'positivo': '#27AE60', 'negativo': '#E74C3C', 'neutro': '#95A5A6'}
        for col in pivot.columns:
            if col in cores:
                fig.add_trace(go.Bar(
                    name=col.capitalize(),
                    x=pivot.index, y=pivot[col],
                    marker_color=cores[col]
                ))
        fig.update_layout(barmode='stack', height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Execute o analisador NLP primeiro")

# Seção NLP Detalhada
st.markdown("---")
st.header("🎯 Índice de Surpresa Monetária (ISM)")

if not sentimento.empty:
    nlp_col1, nlp_col2 = st.columns([2, 1])
    
    with nlp_col1:
        # Calcular ISM
        hawkish = sentimento[sentimento['tom_monetario']=='hawkish']['volume'].sum()
        dovish = sentimento[sentimento['tom_monetario']=='dovish']['volume'].sum()
        total = hawkish + dovish
        ism = (hawkish - dovish) / total if total > 0 else 0
        
        st.metric(
            "ISM (Índice de Surpresa Monetária)",
            f"{ism:.3f}",
            delta="Hawkish 📈" if ism > 0.2 else ("Dovish 📉" if ism < -0.2 else "Neutro ⚖️")
        )
        
        # Barra de progresso
        st.progress(abs(ism), text=f"Intensidade: {abs(ism)*100:.0f}%")
    
    with nlp_col2:
        st.metric("Notícias Hawkish 🦅", int(hawkish))
        st.metric("Notícias Dovish 🕊️", int(dovish))
        st.metric("Total Analisado", int(total))

st.markdown("---")
st.caption("Observatório Inteligente da Política Monetária Angolana © 2024")
st.caption("Dados: BNA, INE, World Bank, FRED | Powered by AI/ML")

# Adicionar seção de previsões no dashboard
# (Execute depois do modelo estar treinado)

def carregar_previsoes():
    """Carrega previsões do modelo"""
    try:
        from scripts.ml.modelo_inflacao import ModeloPrevisaoInflacao
        modelo = ModeloPrevisaoInflacao()
        previsoes = modelo.prever_proximos_meses(6)
        return previsoes
    except Exception as e:
        st.warning(f"Modelo não disponível: {e}")
        return None

# Adicionar na seção principal
st.markdown("---")
st.header("🔮 Previsão de Inflação (ML)")

previsoes = carregar_previsoes()
if previsoes is not None and not previsoes.empty:
    col_p1, col_p2 = st.columns([2, 1])
    
    with col_p1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=previsoes['mes'], y=previsoes['ipc_previsto'],
            mode='lines+markers', name='IPC Previsto',
            line=dict(color='#E74C3C', width=3, dash='dash'),
            marker=dict(size=10)
        ))
        fig.update_layout(
            title='Projeção IPC próximos meses',
            height=300, margin=dict(l=0,r=0,t=30,b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_p2:
        st.metric(
            "Próximo mês",
            f"{previsoes['ipc_previsto'].iloc[0]:.1f}%",
            delta=f"{previsoes['ipc_previsto'].iloc[-1] - previsoes['ipc_previsto'].iloc[0]:.1f}% em 6m"
        )
        st.info("Modelo: XGBoost + Features Econômicas")
