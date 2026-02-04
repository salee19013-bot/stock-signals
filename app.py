import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import plotly.graph_objects as go

# إعداد الصفحة
st.set_page_config(page_title="Stock Signals", layout="wide")
st.title("📊 Stock Signals Dashboard")

# قائمة الأسهم
STOCKS = [
    "AAPL", "NVDA", "TSLA", "AMD", "MSFT", "GOOGL", "META",
    "AMZN", "NFLX", "INTC", "NVTS", "PLUG", "BAC", "JPM",
    "COIN", "SOFI", "RIVN", "NIO", "LCID", "SNAP"
]

@st.cache_data(ttl=600)
def analyze_stock(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty or "Close" not in df:
        return {
            "Stock": symbol,
            "Price": None,
            "RSI": None,
            "SMA20": None,
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

# تحليل الأسهم
results = []

with st.spinner("⏳ Analyzing stocks..."):
    for stock in STOCKS:
        results.append(analyze_stock(stock))

df_results = pd.DataFrame(results)

# عرض الجدول
st.subheader("📋 Stock Analysis Table")
st.dataframe(df_results, use_container_width=True)

# إبراز الإشارات
st.subheader("📌 Trading Signals")

for _, row in df_results.iterrows():
    signal = row["Signal"]

    if signal == "BUY":
        st.success(f"🟢 {row['Stock']} → BUY")
    elif signal == "SELL":
        st.error(f"🔴 {row['Stock']} → SELL")
    elif signal == "HOLD":
        st.info(f"🟡 {row['Stock']} → HOLD")
    else:
        st.warning(f"⚪ {row['Stock']} → NO DATA")

# رسم RSI
st.subheader("📈 RSI Chart")

fig = go.Figure()
fig.add_bar(
    x=df_results["Stock"],
    y=df_results["RSI"],
    text=df_results["Signal"],
)

fig.update_layout(
    yaxis_title="RSI",
    xaxis_title="Stock",
    title="RSI per Stock"
)

st.plotly_chart(fig, use_container_width=True)
