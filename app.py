import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import plotly.graph_objects as go

# قائمة الأسهم
STOCKS = [
    "AAPL", "NVDA", "TSLA", "AMD", "MSFT", "GOOGL", "META",
    "AMZN", "NFLX", "INTC", "NVTS", "PLUG", "BAC", "JPM",
    "COIN", "SOFI", "RIVN", "NIO", "LCID", "SNAP"
]

stocks = STOCKS
st.set_page_config(page_title="Stock Signals", layout="wide")
st.title("📊 Stock Signals Dashboard")

@st.cache_data(ttl=600)
def analyze_stock(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)
if df.empty:
    return {
        "Stock": symbol,
        "Price": "—",
        "RSI": "—",
        "SMA20": "—",
        "Signal": "NO DATA"
    }
    
    close = df["Close"].squeeze()

    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, 20).sma_indicator().iloc[-1]
    price = close.iloc[-1]

    if rsi < 30 and price > sma:
        signal = "BUY"
    elif rsi > 70 and price < sma:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "Stock": symbol,
        "Price": round(float(price), 2),
        "RSI": round(float(rsi), 2),
        "SMA20": round(float(sma), 2),
        "Signal": signal
    }

results = []

with st.spinner("⏳ Analyzing stocks..."):
    for s in stocks:
        res = analyze_stock(s)
        if res:
            results.append(res)

df_results = pd.DataFrame(results)

st.dataframe(df_results, use_container_width=True)

# رسم بسيط
if not df_results.empty:
    fig = go.Figure()
    fig.add_bar(
        x=df_results["Stock"],
        y=df_results["RSI"],
        text=df_results["Signal"],
    )
    fig.update_layout(
        title="RSI per Stock",
        yaxis_title="RSI",
        xaxis_title="Stock"
    )
    st.plotly_chart(fig, use_container_width=True)
