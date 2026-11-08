"""
AI Market Analyst for Liquidity Sniper.
Uses Groq LLM to explain market anomalies in natural language.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY", "dummy_key")
)

MODEL = "llama-3.3-70b-versatile"

def analyze_market_condition(symbol: str, price: float, imbalance: float, anomalies: int, lang: str = "en") -> str:
    """Genera un reporte de análisis de mercado usando IA."""
    
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "dummy_key":
        return "⚠️ AI Analyst disabled. Add GROQ_API_KEY to .env."

    system_prompt = f"""
    You are a Senior Quantitative Analyst and Crypto Market Expert.
    You are analyzing the live market data for {symbol}.
    
    Current Data:
    - Price: ${price}
    - Order Book Imbalance (Buy/Sell Pressure): {imbalance}x (Values > 1.2 mean strong Buy pressure, < 0.8 means strong Sell pressure).
    - Anomalies Detected (Volume Spikes): {anomalies}
    
    Your Task:
    Write a short, tactical market report (max 3 sentences):
    1. Explain the current market sentiment based on the order book.
    2. If there are anomalies, warn the user about possible "Pump & Dump" manipulation.
    3. Give a quick, objective observation (Not financial advice).
    
    Keep the tone professional, urgent, and analytical. 
    You MUST write the report in {'Spanish' if lang == 'es' else 'English'}.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the current condition for {symbol}."}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ AI Analysis failed: {str(e)}"