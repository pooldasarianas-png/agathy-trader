import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# Configuração de Página
st.set_page_config(page_title="AgathyTrader", layout="wide")

# Título Neon
st.markdown("<h1 style='text-align:center; color:#0FF;'>⚡ AGATHY TRADER</h1>", unsafe_allow_html=True)

# Seleção de Ativo
t_padrao = st.session_state.get('tk', 'BTC-USD')
ticker = st.text_input("Digite o Ativo (ex: BTC-USD):", t_padrao).upper()
st.session_state.tk = ticker

try:
    # Busca de dados
    df = yf.download(ticker, period="2d", interval="5m", progress=False)
    
    if not df.empty:
        # Indicadores Básicos para o Score
        df.ta.rsi(append=True)
        df.ta.macd(append=True)
        
        # Lógica de Confluência (Simplificada para estabilidade)
        p = 0
        if df['RSI_14'].iloc[-1] < 45: p += 10
        if df['MACD_12_26_9'].iloc[-1] > 0: p += 10
        
        cor = "#0FF" if p >= 15 else "#F0F" if p <= 5 else "#FFF"
        
        st.markdown(f"""
            <div style="border:2px solid {cor}; border-radius:10px; text-align:center; padding:10px;">
                <h2 style="color:{cor};">CONFLUÊNCIA: {p}/20</h2>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#0FF', decreasing_line_color='#F0F'
        )])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aguardando dados da API...")
except Exception as e:
    st.error(f"Erro: {e}")
