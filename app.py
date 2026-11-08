"""
Liquidity Sniper - Corporate Cyberpunk Trading Dashboard.
Bilingual (EN/ES) + Strong Legal Disclaimer + Real-time Anomalies.
"""

import streamlit as st
import plotly.graph_objects as go
from src.market_analyzer import MarketAnalyzer
import time

st.set_page_config(page_title="Liquidity Sniper", page_icon="🎯", layout="wide")

# ==========================================
# 🌐 TRANSLATIONS DICTIONARY
# ==========================================
TRANSLATIONS = {
    "en": {
        "title": "🎯 LIQUIDITY SNIPER // OPS TERMINAL",
        "subtitle": "Real-Time Market Anomaly Detection & Order Book Analysis",
        "sidebar_disclaimer": "⚠️ **Risk Warning:** This is a Paper Trading simulation for educational purposes only. Not financial advice.",
        "strong_disclaimer": """
        **🚨 STRICT RISK WARNING & DISCLAIMER**
        
        1. **NOT FINANCIAL ADVICE:** This software is for educational, research, and defensive (compliance) purposes only. Nothing in this application constitutes financial, investment, or trading advice.
        2. **SIMULATION ONLY:** This app uses "Paper Trading". It does not execute real trades, nor is it connected to any live exchange account.
        3. **HIGH RISK:** Cryptocurrency markets are highly volatile. Algorithmic trading involves a substantial risk of loss. Past performance or backtesting does not guarantee future results.
        4. **NO LIABILITY:** The developer (Gustavo Ramos) is not responsible or liable for any financial losses incurred if you modify this code for real-world trading.
        5. **COMPLIANCE:** This tool is intended to *detect* market manipulation, not to participate in it. Market manipulation is illegal.
        """,
        "strategy_params": "⚙️ STRATEGY PARAMETERS",
        "select_asset": "Select Asset",
        "timeframe": "Timeframe",
        "vol_mult": "Volume Multiplier (Threshold)",
        "price_thresh": "Price Change Threshold (%)",
        "paper_wallet": "💼 PAPER WALLET",
        "usdt_bal": "USDT Balance",
        "coin_bal": "{symbol} Balance",
        "reset_wallet": "🔄 Reset Wallet",
        "scan_btn": "🚀 SCAN MARKET NOW",
        "telemetry": "📊 BATTLEFIELD TELEMETRY",
        "current_price": "Current Price",
        "imbalance": "Order Book Imbalance",
        "anomalies": "Anomalies Detected",
        "buy_press": "Buy Pressure",
        "sell_press": "Sell Pressure",
        "neutral": "Neutral",
        "execution": "🤖 ALGORITHMIC EXECUTION",
        "anomaly_detected": "🚨 ANOMALY DETECTED! Order Book Imbalance: {imb}",
        "bullish_buy": "📈 Bullish Imbalance detected. Executing PAPER BUY order for $1,000...",
        "bought": "Bought {coins:.4f} {symbol} at ${price:,.4f}. Fee paid: ${fee:.2f}",
        "bearish_sell": "📉 Bearish Imbalance detected. Executing PAPER SELL order...",
        "sold": "Sold all {symbol} at ${price:,.4f}. Fee paid: ${fee:.2f}",
        "no_trade": "Anomaly detected, but Order Book Imbalance does not meet trade criteria.",
        "stable": "✅ Market looks stable. No anomalies detected.",
        "error_fetch": "Failed to fetch data from Binance.",
        "standby": "💡 **STANDBY MODE:** Adjust parameters on the left and press 'SCAN MARKET NOW' to begin tactical analysis."
    },
    "es": {
        "title": "🎯 FRANCO TIRADOR DE LIQUIDEZ // TERMINAL DE OPS",
        "subtitle": "Detección de Anomalías de Mercado en Tiempo Real y Análisis de Libro de Órdenes",
        "sidebar_disclaimer": "⚠️ **Advertencia de Riesgo:** Esta es una simulación de Paper Trading solo con fines educativos. No es asesoramiento financiero.",
        "strong_disclaimer": """
        **🚨 ADVERTENCIA DE RIESGO ESTRICTA Y AVISO LEGAL**
        
        1. **NO ES ASESORAMIENTO FINANCIERO:** Este software es solo para fines educativos, de investigación y defensivos (cumplimiento). Nada en esta aplicación constituye asesoramiento financiero, de inversión o de trading.
        2. **SOLO SIMULACIÓN:** Esta app usa "Paper Trading". No ejecuta operaciones reales ni está conectada a ninguna cuenta de exchange real.
        3. **ALTO RIESGO:** Los mercados de criptomonedas son altamente volátiles. El trading algorítmico implica un riesgo sustancial de pérdida. El rendimiento pasado no garantiza resultados futuros.
        4. **SIN RESPONSABILIDAD:** El desarrollador (Gustavo Ramos) no se hace responsable de las pérdidas financieras incurridas si modificas este código para trading real.
        5. **CUMPLIMIENTO:** Esta herramienta está destinada a *detectar* manipulación de mercado, no a participar en ella. La manipulación de mercado es ilegal.
        """,
        "strategy_params": "⚙️ PARÁMETROS DE ESTRATEGIA",
        "select_asset": "Seleccionar Activo",
        "timeframe": "Marco Temporal",
        "vol_mult": "Multiplicador de Volumen (Umbral)",
        "price_thresh": "Umbral de Cambio de Precio (%)",
        "paper_wallet": "💼 BILLETERA FICTICIA",
        "usdt_bal": "Balance USDT",
        "coin_bal": "Balance {symbol}",
        "reset_wallet": "🔄 Reiniciar Billetera",
        "scan_btn": "🚀 ESCANEAR MERCADO AHORA",
        "telemetry": "📊 TELEMETRÍA DEL CAMPO DE BATALLA",
        "current_price": "Precio Actual",
        "imbalance": "Desequilibrio Libro de Órdenes",
        "anomalies": "Anomalías Detectadas",
        "buy_press": "Presión de Compra",
        "sell_press": "Presión de Venta",
        "neutral": "Neutral",
        "execution": "🤖 EJECUCIÓN ALGORÍTMICA",
        "anomaly_detected": "🚨 ¡ANOMALÍA DETECTADA! Desequilibrio: {imb}",
        "bullish_buy": "📈 Presión compradora detectada. Ejecutando orden de COMPRA FICTICIA por $1,000...",
        "bought": "Comprado {coins:.4f} {symbol} a ${price:,.4f}. Comisión pagada: ${fee:.2f}",
        "bearish_sell": "📉 Presión vendedora detectada. Ejecutando orden de VENTA FICTICIA...",
        "sold": "Vendido todo {symbol} a ${price:,.4f}. Comisión pagada: ${fee:.2f}",
        "no_trade": "Anomalía detectada, pero el Desequilibrio del Libro no cumple los criterios.",
        "stable": "✅ El mercado parece estable. Sin anomalías detectadas.",
        "error_fetch": "Fallo al obtener datos de Binance.",
        "standby": "💡 **MODO ESPERA:** Ajusta los parámetros a la izquierda y presiona 'ESCANEAR MERCADO AHORA' para comenzar."
    }
}

# ==========================================
# 🎨 CORPORATE CYBERPUNK THEME (CSS)
# ==========================================
corporate_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
.stApp { background-color: #0b0c10; color: #c5c6c7; font-family: 'Share Tech Mono', monospace; }
h1 { color: #66fcf1 !important; text-shadow: 0 0 10px #45a29e; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #ff4c00; padding-bottom: 10px; }
h2, h3 { color: #45a29e !important; text-transform: uppercase; }
.stSelectbox, .stSlider { background-color: #1f2833 !important; color: #66fcf1 !important; }
.stButton > button { background-color: #1f2833 !important; color: #ff4c00 !important; border: 2px solid #ff4c00 !important; border-radius: 0px !important; text-transform: uppercase; transition: all 0.2s ease !important; width: 100%; box-shadow: 0 0 10px rgba(255, 76, 0, 0.2); }
.stButton > button:hover { background-color: #ff4c00 !important; color: #000000 !important; box-shadow: 0 0 20px rgba(255, 76, 0, 0.8) !important; }
div[data-testid="stMetric"] { background-color: #1f2833; border: 1px solid #45a29e; border-top: 3px solid #66fcf1; border-radius: 0px; padding: 15px; box-shadow: 0 0 10px rgba(102, 252, 241, 0.1); }
div[data-testid="stMetricValue"] { color: #66fcf1 !important; font-family: 'Share Tech Mono', monospace; }
.stAlert { background-color: #1f2833; border: 1px solid #ff4c00; color: #ff4c00; border-radius: 0px; }
</style>
"""
st.markdown(corporate_css, unsafe_allow_html=True)

# ==========================================
# WALLET STATE
# ==========================================
if "usdt_balance" not in st.session_state:
    st.session_state.usdt_balance = 10000.0
if "coin_balance" not in st.session_state:
    st.session_state.coin_balance = 0.0

# ==========================================
# LANGUAGE SELECTOR & SIDEBAR
# ==========================================
lang_options = {"en": "🇺🇸 English", "es": "🇪🇸 Español"}
selected_lang = st.sidebar.selectbox("Language / Idioma", options=list(lang_options.keys()), format_func=lambda x: lang_options[x])
t = TRANSLATIONS[selected_lang]

# Disclaimer corto en la barra lateral
st.sidebar.warning(t["sidebar_disclaimer"])

# ==========================================
# HEADER
# ==========================================
st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")
st.divider()

# ==========================================
# LAYOUT
# ==========================================
col_controls, col_telemetry = st.columns([1, 2], gap="large")

with col_controls:
    st.markdown(f"### {t['strategy_params']}")
    
    symbol = st.selectbox(t["select_asset"], ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "PEPEUSDT"])
    interval = st.selectbox(t["timeframe"], ["1m", "5m", "15m"])
    vol_mult = st.slider(t["vol_mult"], 2.0, 10.0, 4.0)
    price_thresh = st.slider(t["price_thresh"], 0.5, 5.0, 1.5)
    
    st.divider()
    
    st.markdown(f"### {t['paper_wallet']}")
    st.metric(t["usdt_bal"], f"${st.session_state.usdt_balance:,.2f}")
    st.metric(t["coin_bal"].format(symbol=symbol[:-4]), f"{st.session_state.coin_balance:.4f}")
    
    if st.button(t["reset_wallet"]):
        st.session_state.usdt_balance = 10000.0
        st.session_state.coin_balance = 0.0
        st.rerun()
        
    st.divider()
    scan_btn = st.button(t["scan_btn"], type="primary")

with col_telemetry:
    st.markdown(f"### {t['telemetry']}")
    
    if scan_btn:
        analyzer = MarketAnalyzer()
        
        with st.spinner("Scanning / Escaneando..."):
            df = analyzer.get_klines(symbol=symbol, interval=interval, limit=100)
            imbalance = analyzer.get_order_book_imbalance(symbol)
            
            if df is not None:
                anomalies = analyzer.detect_anomalies(df, vol_mult, price_thresh)
                current_price = df["close"].iloc[-1]
                
                c1, c2, c3 = st.columns(3)
                c1.metric(t["current_price"], f"${current_price:,.4f}")
                
                if imbalance > 1.2:
                    delta_label = t["buy_press"]
                    delta_color = "normal"
                elif imbalance < 0.8:
                    delta_label = t["sell_press"]
                    delta_color = "inverse"
                else:
                    delta_label = t["neutral"]
                    delta_color = "off"
                
                c2.metric(t["imbalance"], f"{imbalance} x", delta=delta_label, delta_color=delta_color)
                c3.metric(t["anomalies"], len(anomalies))
                
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
                    template="plotly_dark", height=450, margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor="#0b0c10", plot_bgcolor="#1f2833",
                    font=dict(family="Share Tech Mono", color="#66fcf1")
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.markdown(f"### {t['execution']}")
                
                if not anomalies.empty:
                    st.warning(t["anomaly_detected"].format(imb=imbalance))
                    
                    if imbalance > 1.2 and st.session_state.usdt_balance >= 1000:
                        st.info(t["bullish_buy"])
                        trade_amount = 1000.0
                        coins, fee = analyzer.simulate_trade(trade_amount, current_price, "BUY")
                        
                        st.session_state.usdt_balance -= trade_amount
                        st.session_state.coin_balance += coins
                        
                        st.success(t["bought"].format(coins=coins, symbol=symbol[:-4], price=current_price, fee=fee))
                        time.sleep(1.5)
                        st.rerun()
                        
                    elif imbalance < 0.8 and st.session_state.coin_balance > 0:
                        st.info(t["bearish_sell"])
                        trade_value = st.session_state.coin_balance * current_price
                        cash_earned, fee = analyzer.simulate_trade(trade_value, current_price, "SELL")
                        
                        st.session_state.coin_balance = 0.0
                        st.session_state.usdt_balance += cash_earned
                        
                        st.success(t["sold"].format(symbol=symbol[:-4], price=current_price, fee=fee))
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.info(t["no_trade"])
                else:
                    st.success(t["stable"])
            else:
                st.error(t["error_fetch"])
    else:
        st.info(t["standby"])

# ==========================================
# STRONG DISCLAIMER (Footer)
# ==========================================
st.divider()
st.error(t["strong_disclaimer"])