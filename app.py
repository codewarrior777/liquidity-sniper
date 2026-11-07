"""
Liquidity Sniper - Corporate Cyberpunk Trading Dashboard.
Real-time anomaly detection + Order Book analysis + Paper Trading.
"""

import streamlit as st
import plotly.graph_objects as go
from src.market_analyzer import MarketAnalyzer
import time

st.set_page_config(page_title="Liquidity Sniper", page_icon="🎯", layout="wide")

# ==========================================
# 🎨 CORPORATE CYBERPUNK THEME (CSS)
# ==========================================
corporate_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* Fondo general */
.stApp {
    background-color: #0b0c10;
    color: #c5c6c7;
    font-family: 'Share Tech Mono', monospace;
}

/* Título Principal (Verde Militar) */
h1 {
    color: #66fcf1 !important;
    text-shadow: 0 0 10px #45a29e;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 2px solid #ff4c00;
    padding-bottom: 10px;
}

h2, h3 {
    color: #45a29e !important;
    text-transform: uppercase;
}

/* Controles de la barra lateral */
.stSelectbox, .stSlider {
    background-color: #1f2833 !important;
    color: #66fcf1 !important;
}

/* Botones (Estilo táctico) */
.stButton > button {
    background-color: #1f2833 !important;
    color: #ff4c00 !important;
    border: 2px solid #ff4c00 !important;
    border-radius: 0px !important;
    text-transform: uppercase;
    transition: all 0.2s ease !important;
    width: 100%;
    box-shadow: 0 0 10px rgba(255, 76, 0, 0.2);
}

.stButton > button:hover {
    background-color: #ff4c00 !important;
    color: #000000 !important;
    box-shadow: 0 0 20px rgba(255, 76, 0, 0.8) !important;
}

/* Tarjetas de métricas */
div[data-testid="stMetric"] {
    background-color: #1f2833;
    border: 1px solid #45a29e;
    border-top: 3px solid #66fcf1;
    border-radius: 0px;
    padding: 15px;
    box-shadow: 0 0 10px rgba(102, 252, 241, 0.1);
}

div[data-testid="stMetricValue"] {
    color: #66fcf1 !important;
    font-family: 'Share Tech Mono', monospace;
}

/* Cajas de alertas */
.stAlert {
    background-color: #1f2833;
    border: 1px solid #ff4c00;
    color: #ff4c00;
    border-radius: 0px;
}
</style>
"""
st.markdown(corporate_css, unsafe_allow_html=True)

st.title("🎯 LIQUIDITY SNIPER // OPS TERMINAL")
st.markdown("**Real-Time Market Anomaly Detection & Order Book Analysis**")
st.divider()

# ==========================================
# WALLET STATE
# ==========================================
if "usdt_balance" not in st.session_state:
    st.session_state.usdt_balance = 10000.0
if "coin_balance" not in st.session_state:
    st.session_state.coin_balance = 0.0

# ==========================================
# LAYOUT: CONTROLS (LEFT) & TELEMETRY (RIGHT)
# ==========================================
col_controls, col_telemetry = st.columns([1, 2], gap="large")

# ------------------------------------------
# COLUMNA IZQUIERDA: PARÁMETROS Y WALLET
# ------------------------------------------
with col_controls:
    st.markdown("### ⚙️ STRATEGY PARAMETERS")
    
    symbol = st.selectbox("Select Asset", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "PEPEUSDT"])
    interval = st.selectbox("Timeframe", ["1m", "5m", "15m"])
    vol_mult = st.slider("Volume Multiplier (Threshold)", 2.0, 10.0, 4.0)
    price_thresh = st.slider("Price Change Threshold (%)", 0.5, 5.0, 1.5)
    
    st.divider()
    
    st.markdown("### 💼 PAPER WALLET")
    st.metric("USDT Balance", f"${st.session_state.usdt_balance:,.2f}")
    st.metric(f"{symbol[:-4]} Balance", f"{st.session_state.coin_balance:.4f}")
    
    if st.button("🔄 Reset Wallet"):
        st.session_state.usdt_balance = 10000.0
        st.session_state.coin_balance = 0.0
        st.rerun()
        
    st.divider()
    scan_btn = st.button("🚀 SCAN MARKET NOW", type="primary")

# ------------------------------------------
# COLUMNA DERECHA: RESULTADOS Y GRÁFICA
# ------------------------------------------
with col_telemetry:
    st.markdown("### 📊 BATTLEFIELD TELEMETRY")
    
    if scan_btn:
        analyzer = MarketAnalyzer()
        
        with st.spinner(f"Scanning {symbol} and analyzing Order Book..."):
            df = analyzer.get_klines(symbol=symbol, interval=interval, limit=100)
            imbalance = analyzer.get_order_book_imbalance(symbol)
            
            if df is not None:
                anomalies = analyzer.detect_anomalies(df, vol_mult, price_thresh)
                current_price = df["close"].iloc[-1]
                
                # --- METRICS ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Current Price", f"${current_price:,.4f}")
                
                # Delta color logic
                delta_label = "Buy Pressure" if imbalance > 1.2 else ("Sell Pressure" if imbalance < 0.8 else "Neutral")
                delta_color = "normal" if imbalance > 1.2 else ("inverse" if imbalance < 0.8 else "off")
                
                c2.metric("Order Book Imbalance", f"{imbalance} x", delta=delta_label, delta_color=delta_color)
                c3.metric("Anomalies Detected", len(anomalies))
                
                # --- CHART ---
                fig = go.Figure(data=[go.Candlestick(
                    x=df["open_time"], open=df["open"], high=df["high"],
                    low=df["low"], close=df["close"], name="Price"
                )])
                
                if not anomalies.empty:
                    fig.add_trace(go.Scatter(
                        x=anomalies["open_time"], y=anomalies["close"],
                        mode="markers", marker=dict(color="#ff4c00", size=12, symbol="x"),
                        name="Anomaly"
                    ))
                    
                fig.update_layout(
                    template="plotly_dark", 
                    height=450, 
                    margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor="#0b0c10",
                    plot_bgcolor="#1f2833",
                    font=dict(family="Share Tech Mono", color="#66fcf1")
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # --- TRADING LOGIC ---
                st.divider()
                st.markdown("### 🤖 ALGORITHMIC EXECUTION")
                
                if not anomalies.empty:
                    st.warning(f"🚨 ANOMALY DETECTED! Order Book Imbalance: {imbalance}")
                    
                    # BUY LOGIC
                    if imbalance > 1.2 and st.session_state.usdt_balance >= 1000:
                        st.info("📈 Bullish Imbalance detected. Executing PAPER BUY order for $1,000...")
                        trade_amount = 1000.0
                        coins, fee = analyzer.simulate_trade(trade_amount, current_price, "BUY")
                        
                        st.session_state.usdt_balance -= trade_amount
                        st.session_state.coin_balance += coins
                        
                        st.success(f"Bought {coins:.4f} {symbol[:-4]} at ${current_price:,.4f}. Fee paid: ${fee:.2f}")
                        time.sleep(1.5)
                        st.rerun()
                        
                    # SELL LOGIC
                    elif imbalance < 0.8 and st.session_state.coin_balance > 0:
                        st.info("📉 Bearish Imbalance detected. Executing PAPER SELL order...")
                        trade_value = st.session_state.coin_balance * current_price
                        cash_earned, fee = analyzer.simulate_trade(trade_value, current_price, "SELL")
                        
                        st.session_state.coin_balance = 0.0
                        st.session_state.usdt_balance += cash_earned
                        
                        st.success(f"Sold all {symbol[:-4]} at ${current_price:,.4f}. Fee paid: ${fee:.2f}")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.info("Anomaly detected, but Order Book Imbalance does not meet trade criteria.")
                else:
                    st.success("✅ Market looks stable. No anomalies detected.")
            else:
                st.error("Failed to fetch data from Binance.")
    else:
        st.info("💡 **STANDBY MODE:** Adjust parameters on the left and press 'SCAN MARKET NOW' to begin tactical analysis.")