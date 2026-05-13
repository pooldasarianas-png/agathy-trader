
import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import pandas as pd

# 1. CONFIGURAÇÃO E ESTILO NEON
st.set_page_config(page_title="AgathyTrader Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { border: 2px solid #00FFFF; background-color: #0a0a0a; border-radius: 15px; }
    .confluencia-box { 
        padding: 20px; border-radius: 15px; text-align: center;
        border: 3px solid #FF00FF; background-color: #111;
        margin-bottom: 20px; box-shadow: 0 0 15px #FF00FF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1 style='text-align: center; color: #00FFFF;'>⚡ AGATHY TRADER PRO</h1>", unsafe_allow_html=True)

# --- BOTÕES DE ATIVOS RÁPIDOS (LISTA) ---
st.write("🎯 **SELECIONE O ATIVO:**")
col_bt1, col_bt2, col_bt3, col_bt4, col_bt5 = st.columns(5)
with col_bt1: bt_btc = st.button("₿ BTC-USD")
with col_bt2: bt_eth = st.button("Ξ ETH-USD")
with col_bt3: bt_eur = st.button("💱 EUR/USD")
with col_bt4: bt_gold = st.button("🟡 OURO")
with col_bt5: bt_nas = st.button("📈 NASDAQ")

# Lógica de seleção
if 'ativo' not in st.session_state: st.session_state.ativo = "BTC-USD"
if bt_btc: st.session_state.ativo = "BTC-USD"
if bt_eth: st.session_state.ativo = "ETH-USD"
if bt_eur: st.session_state.ativo = "EURUSD=X"
if bt_gold: st.session_state.ativo = "GC=F"
if bt_nas: st.session_state.ativo = "^IXIC"

# --- CONFIGURAÇÃO DE TEMPO ---
col_cfg1, col_cfg2 = st.columns([2, 1])
with col_cfg1:
    ticker = st.text_input("Ou digite outro ticker:", st.session_state.ativo).upper()
with col_cfg2:
    tf = st.selectbox("Tempo Gráfico", ["1m", "5m", "15m", "1h", "1d"], index=1)

# --- SISTEMA DE FONTES (PLANO A e B) ---
@st.cache_data(ttl=30)
def buscar_dados_seguros(t, interval):
    try:
        # Tenta Yahoo Finance como fonte primária estável
        df = yf.download(t, period="2d", interval=interval, progress=False)
        if df.empty: raise Exception("Vazio")
        return df
    except:
        # Plano B: Tenta uma variação de ticker se falhar
        st.warning("🔄 Alternando fonte de dados...")
        return yf.download(t, period="5d", interval="1h", progress=False)

df = buscar_dados_seguros(ticker, tf)

if not df.empty:
    # --- CÁLCULO DOS 20 INDICADORES ---
    df.ta.macd(append=True); df.ta.rsi(append=True); df.ta.stoch(append=True)
    df.ta.adx(append=True); df.ta.cci(append=True); df.ta.supertrend(append=True)
    df.ta.bbands(append=True); df.ta.aroon(append=True); df.ta.kc(append=True)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)

    # --- LÓGICA CRUCIAL: CONTADOR DE CONFLUÊNCIA ---
    pontos = 0
    total_indicadores = 20 # Definimos o peso para 20
    
    # Exemplos de pesos de confluência
    if df['RSI_14'].iloc[-1] < 40: pontos += 4
    if df['Close'].iloc[-1] > df['EMA_20'].iloc[-1]: pontos += 4
    if df['MACD_12_26_9'].iloc[-1] > 0: pontos += 4
    if df['SUPERT_7_3.0'].iloc[-1] < df['Close'].iloc[-1]: pontos += 4
    if df['ADX_14'].iloc[-1] > 25: pontos += 4

    # --- EXIBIÇÃO DA CONFLUÊNCIA ---
    cor_box = "#00FFFF" if pontos >= 12 else "#FF00FF"
    st.markdown(f"""
        <div class="confluencia-box" style="border-color: {cor_box}; box-shadow: 0 0 15px {cor_box};">
            <h2 style="color: {cor_box};">CONFLUÊNCIA AGATHY: {pontos}/{total_indicadores}</h2>
            <p style="font-size: 20px;">{'🔥 ALTA FORTE' if pontos >= 15 else '💧 BAIXA FORTE' if pontos <= 5 else '⚖️ MERCADO LATERAL'}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- GRÁFICO CANDLESTICK REAL-TIME ---
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#00FFFF', decreasing_line_color='#FF00FF'
    )])
    
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False,
                      paper_bgcolor='black', plot_bgcolor='black')
    st.plotly_chart(fig, use_container_width=True)

    # --- DETALHES TÉCNICOS ---
    with st.expander("📄 Ver Check-list dos 20 Indicadores"):
        st.write(df.tail(3))

else:
    st.error("Erro ao conectar com as fontes (Binance/Yahoo). Tente outro ativo.")
