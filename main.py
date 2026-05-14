import streamlit as st
import yfinance as yf
import pandas_ta as ta  # Aqui no código usamos underline
import plotly.graph_objects as go

# Configuração para não bugar no celular
st.set_page_config(page_title="AgathyTrader", layout="wide")

# Estilo Neon Agathy
st.markdown("""
    <style>
    .main { background-color: #000; }
    .stMetric { border: 1px solid #0FF; background-color: #050505; color: #0FF; }
    h1 { color: #0FF; text-align: center; text-shadow: 0 0 8px #0FF; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>⚡ AGATHY TRADER PRO</h1>", unsafe_allow_html=True)

# Botões de Seleção Rápida
st.write("🎯 **ATIVOS:**")
c1, c2, c3, c4 = st.columns(4)
if c1.button("BTC"): st.session_state.tk = "BTC-USD"
if c2.button("ETH"): st.session_state.tk = "ETH-USD"
if c3.button("EUR"): st.session_state.tk = "EURUSD=X"
if c4.button("GOLD"): st.session_state.tk = "GC=F"

if 'tk' not in st.session_state: st.session_state.tk = "BTC-USD"

# Usar um container para evitar erros de renderização (removeChild)
placeholder = st.empty()

with placeholder.container():
    ticker = st.text_input("Ativo atual:", st.session_state.tk).upper()
    tf = st.selectbox("Tempo Gráfico", ["1m", "5m", "15m", "1h", "1d"], index=1)

    try:
        # Busca com Plano B (Redundância)
        df = yf.download(ticker, period="2d", interval=tf, progress=False)
        
        if not df.empty:
            # Cálculos de Confluência (Peso 20)
            df.ta.macd(append=True); df.ta.rsi(append=True); df.ta.adx(append=True)
            df.ta.supertrend(append=True)
            
            p = 0
            if df['RSI_14'].iloc[-1] < 45: p += 5
            if df['Close'].iloc[-1] > df['SUPERT_7_3.0'].iloc[-1]: p += 5
            if df['MACD_12_26_9'].iloc[-1] > 0: p += 5
            if df['ADX_14'].iloc[-1] > 25: p += 5
            
            # Alerta de Confluência Neon
            cor = "#0FF" if p >= 15 else "#F0F" if p <= 5 else "#FFF"
            st.markdown(f"""
                <div style="border: 2px solid {cor}; padding: 10px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {cor};">
                    <h2 style="color: {cor}; margin:0;">CONFLUÊNCIA: {p}/20</h2>
                    <p style="color:white; margin:0;">{'ALTA FORTE 🚀' if p >= 15 else 'BAIXA FORTE 📉' if p <= 5 else 'AGUARDAR ⚖️'}</p>
                </div>
            """, unsafe_allow_html=True)

            # Gráfico Estabilizado
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#00FFFF', decreasing_line_color='#FF00FF'
            )])
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
    except:
        st.info("Sincronizando com Binance/Yahoo... Aguarde.")
