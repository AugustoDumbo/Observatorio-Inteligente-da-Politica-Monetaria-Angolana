"""
Dashboard do Observatório Monetário Angolano - MVP
Execute: streamlit run dashboard_observatorio.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.utils.conexoes import ConexaoPostgres

st.set_page_config(
    page_title="Observatório Monetário Angolano",
    page_icon="🇦🇴",
    layout="wide"
)

st.title("🇦🇴 Observatório Inteligente da Política Monetária Angolana")
st.markdown("---")

# Conectar ao banco
@st.cache_data(ttl=300)
def carregar_dados():
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    cambio = pd.read_sql("""
        SELECT timestamp, moeda, valor_compra 
        FROM raw.taxas_cambio 
        ORDER BY timestamp DESC
    """, conn)
    
    juros = pd.read_sql("""
        SELECT * FROM raw.taxas_juro 
        ORDER BY timestamp DESC
    """, conn)
    
    agregados = pd.read_sql("""
        SELECT * FROM raw.agregados_monetarios 
        ORDER BY timestamp DESC
    """, conn)
    
    internacional = pd.read_sql("""
        SELECT * FROM raw.precos_internacionais 
        ORDER BY timestamp DESC
    """, conn)
    
    conn.close()
    return cambio, juros, agregados, internacional

try:
    cambio, juros, agregados, internacional = carregar_dados()
    
    # Linha 1: Taxas de Câmbio
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Taxa de Câmbio USD/AOA")
        usd = cambio[cambio['moeda'] == 'USD'].head(30)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=usd['timestamp'], y=usd['valor_compra'],
            mode='lines+markers', name='USD/AOA',
            line=dict(color='#2E86C1', width=2)
        ))
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏦 Taxa BNA (Taxa Diretora)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=juros['timestamp'], y=juros['taxa_bna'],
            mode='lines+markers', name='Taxa BNA',
            line=dict(color='#E74C3C', width=3)
        ))
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Linha 2: Petróleo e Reservas
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🛢️ Preço do Petróleo Brent (USD)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=internacional['timestamp'], y=internacional['brent_crude'],
            mode='lines+markers', name='Brent',
            line=dict(color='#F39C12', width=2)
        ))
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("💰 Reservas Internacionais (Milhões USD)")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=agregados['timestamp'], y=agregados['reservas_internacionais'],
            name='Reservas', marker_color='#27AE60'
        ))
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Métricas rápidas
    st.markdown("---")
    met1, met2, met3, met4 = st.columns(4)
    
    with met1:
        ultimo_usd = usd['valor_compra'].iloc[0] if not usd.empty else 0
        st.metric("USD/AOA", f"{ultimo_usd:.2f}", "📈")
    
    with met2:
        ultima_taxa = juros['taxa_bna'].iloc[0] if not juros.empty else 0
        st.metric("Taxa BNA", f"{ultima_taxa:.2f}%", "🏦")
    
    with met3:
        ultimo_brent = internacional['brent_crude'].iloc[0] if not internacional.empty else 0
        st.metric("Brent", f"${ultimo_brent:.2f}", "🛢️")
    
    with met4:
        ultimas_reservas = agregados['reservas_internacionais'].iloc[0] if not agregados.empty else 0
        st.metric("Reservas", f"${ultimas_reservas:,.0f}M", "💰")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Verifique se as tabelas foram criadas e têm dados.")

# Adicione esta função ao dashboard existente
def carregar_sentimento():
    pg = ConexaoPostgres()
    conn = pg.conectar()
    
    try:
        df = pd.read_sql("""
            SELECT 
                DATE(timestamp) as data,
                sentimento,
                COUNT(*) as volume
            FROM raw.analise_sentimento
            WHERE timestamp >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(timestamp), sentimento
            ORDER BY data DESC;
        """, conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# Adicione no final do arquivo dashboard_observatorio.py
# (após o último st.metric)

st.markdown("---")
st.header("📰 Análise de Sentimento do Mercado")

sent_df = carregar_sentimento()

if not sent_df.empty:
    col_nlp1, col_nlp2 = st.columns(2)
    
    with col_nlp1:
        st.subheader("📊 Evolução do Sentimento")
        pivot = sent_df.pivot_table(
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
        fig.update_layout(barmode='stack', height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_nlp2:
        st.subheader("🎯 Índice de Surpresa Monetária")
        # Aqui você pode adicionar o ISM quando implementar
        st.info("ISM será calculado na próxima atualização")
        st.metric("Notícias analisadas (30d)", sent_df['volume'].sum())
else:
    st.warning("Execute o analisador de sentimento primeiro: python scripts/nlp/analisador_sentimento.py")
