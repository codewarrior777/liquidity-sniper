"""
Liquidity Sniper - Advanced Market Analyzer.
Analyzes Order Book imbalance, detects anomalies, and simulates trading with fees.
"""

import pandas as pd
from binance.client import Client

class MarketAnalyzer:
    def __init__(self):
        # Usamos la API pública (no requiere keys para leer datos)
        self.client = Client()
        self.taker_fee = 0.001 # 0.1% de comisión típica en Binance

    def get_klines(self, symbol="BTCUSDT", interval="1m", limit=100):
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "qav", "num_trades", "taker_base", "taker_quote", "ignore"
            ])
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df["price_change_pct"] = df["close"].pct_change() * 100
            return df
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return None

    def get_order_book_imbalance(self, symbol="BTCUSDT", limit=50):
        """
        Lee el Libro de Órdenes y calcula el ratio de compra/venta.
        Un ratio > 1 significa más presión compradora (Bullish).
        """
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=limit)
            
            # Sumamos el volumen total de las ofertas (bids) y demandas (asks)
            bid_volume = sum(float(bid[1]) for bid in depth['bids'])
            ask_volume = sum(float(ask[1]) for ask in depth['asks'])
            
            if ask_volume == 0: return 1.0
            
            imbalance = bid_volume / ask_volume
            return round(imbalance, 2)
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return 1.0

    def detect_anomalies(self, df, volume_multiplier=5.0, price_change_threshold=2.0):
        if df is None or df.empty: return None
        
        # Calculamos el volumen promedio de las últimas 20 velas
        df["avg_volume"] = df["volume"].rolling(window=20).mean()
        
        # Una anomalía ocurre si el volumen es X veces mayor al promedio Y el precio se movió bruscamente
        df["is_anomaly"] = (
            (df["volume"] > df["avg_volume"] * volume_multiplier) & 
            (df["price_change_pct"].abs() > price_change_threshold)
        )
        
        return df[df["is_anomaly"] == True].copy()

    def simulate_trade(self, capital: float, price: float, action: str):
        """Simula una orden a mercado y calcula la comisión de Binance."""
        fee_amount = capital * self.taker_fee
        net_capital = capital - fee_amount
        
        if action == "BUY":
            coins_bought = net_capital / price
            return coins_bought, fee_amount
        elif action == "SELL":
            return net_capital, fee_amount
        return 0, 0