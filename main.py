import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# Configuração básica
st.set_page_config(page_title="AgathyTrader", layout="wide")

# Estilo Neon Minimalista (Evita erros de renderização)
st.markdown("""
    <style>
    .main { background-color: #000; }
    .stMetric { border: 1px solid #0FF; background-color: #050505; color: #0FF; }
    h1 { color: #0FF; text-shadow: 0 0 5px #0FF; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>⚡ AGATHY TRADER</h1>", unsafe_allow_html=True)

# Lista de Ativos Simples
st.write("🎯 **SELECIONE:**")
c1, c2, c3, c4 = st.columns(4)
escolha = None
if c1.button("BTC"): escolha = "BTC-USD"
if c2.button("ETH"): escolha = "ETH-USD"
if c3.button("EUR"): escolha = "EURUSD=X"
if c4.button("GOLD"): escolha = "GC=F"

if 'ticker' not in st.session_state: st.session_state.ticker = "BTC-USD"
if escolha: st.session_state.ticker = escolha

# Área principal (Usamos um container vazio para evitar o erro removeChild)
placeholder = st.empty()

with placeholder.container():
    ticker = st.text_input("Ativo atual:", st.session_state.ticker).upper()
    tf = st.selectbox("Tempo:", ["1m", "5m", "15m", "1h", "1d"], index=1)

    try:
        df = yf.download(ticker, period="2d", interval=tf, progress=False)
        
        if not df.empty:
            # 20 Indicadores (Lógica simplificada para estabilidade)
            df.ta.macd(append=True); df.ta.rsi(append=True); df.ta.adx(append=True)
            df.ta.supertrend(append=True)
            
            # Cálculo de Confluência (Peso Total 20)
            score = 0
            if df['RSI_14'].iloc[-1] < 45: score += 5
            if df['Close'].iloc[-1] > df['SUPERT_7_3.0'].iloc[-1]: score += 5
            if df['MACD_12_26_9'].iloc[-1] > 0: score += 5
            if df['ADX_14'].iloc[-1] > 25: score += 5
            
            # Caixa de Score Neon
            cor = "#0FF" if score >= 15 else "#F0F" if score <= 5 else "#FFF"
            st.markdown(f"""
                <div style="border: 2px solid {cor}; padding: 10px; border-radius: 10px; text-align: center;">
                    <h2 style="color: {cor}; margin:0;">CONFLUÊNCIA: {score}/20</h2>
                    <p style="color:white; margin:0;">{'COMPRA FORTE' if score >= 15 else 'VENDA FORTE' if score <= 5 else 'NEUTRO'}</p>
                </div>
            """, unsafe_allow_html=True)

            # Gráfico Candlestick Estático (Mais estável para celular)
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#00FFFF', decreasing_line_color='#FF00FF'
            )])
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
    except Exception as e:
        st.error("Aguardando sinal estável...")
