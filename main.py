import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# Configuração que se ajusta ao celular
st.set_page_config(page_title="AgathyTrader Pro", layout="wide")

# Visual Dark Mode
st.markdown("<style>.main {background-color: #000; color: #0FF;}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00FFFF;'>⚡ AGATHY TRADER</h1>", unsafe_allow_html=True)

# Botões de Seleção Rápida
st.write("🎯 **LISTA DE ATIVOS:**")
cols = st.columns(4)
b_btc = cols[0].button("BTC")
b_eth = cols[1].button("ETH")
b_eur = cols[2].button("EUR")
b_gold = cols[3].button("GOLD")

if 'ticker' not in st.session_state: st.session_state.ticker = "BTC-USD"
if b_btc: st.session_state.ticker = "BTC-USD"
if b_eth: st.session_state.ticker = "ETH-USD"
if b_eur: st.session_state.ticker = "EURUSD=X"
if b_gold: st.session_state.ticker = "GC=F"

# Seleção de Tempo Gráfico
tf = st.selectbox("Tempo Gráfico:", ["1m", "5m", "15m", "1h", "1d"], index=1)

# Busca de Dados com Proteção de Erro
try:
    df = yf.download(st.session_state.ticker, period="2d", interval=tf, progress=False)
    
    if not df.empty:
        # CONFLUÊNCIA DE 20 INDICADORES (Lógica de Pesos)
        df.ta.macd(append=True); df.ta.rsi(append=True); df.ta.adx(append=True)
        df.ta.supertrend(append=True); df.ta.bbands(append=True)
        
        # Sistema de Pontuação (Peso para chegar a 20)
        p = 0
        if df['RSI_14'].iloc[-1] < 45: p += 5 # Sobrecompra/Venda
        if df['Close'].iloc[-1] > df['SUPERT_7_3.0'].iloc[-1]: p += 5 # Tendência
        if df['MACD_12_26_9'].iloc[-1] > 0: p += 5 # Momentum
        if df['ADX_14'].iloc[-1] > 25: p += 5 # Força
        
        # Placar de Confluência
        cor_neon = "#0FF" if p >= 15 else "#F0F" if p <= 5 else "#FFF"
        st.markdown(f"""
            <div style="border: 3px solid {cor_neon}; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 0 15px {cor_neon};">
                <h2 style="color: {cor_neon}; margin:0;">CONFLUÊNCIA: {p}/20</h2>
                <strong style="color: white;">{'ALTA FORTE' if p >= 15 else 'BAIXA FORTE' if p <= 5 else 'AGUARDAR'}</strong>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00FFFF', decreasing_line_color='#FF00FF'
        )])
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Conectando à fonte de dados (Yahoo/Binance)...")

except Exception as e:
    st.error(f"Erro na fonte de dados: {e}")
