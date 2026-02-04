import yfinance as yf
import pandas as pd
import streamlit as st
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import plotly.graph_objects as go

st.set_page_config(page_title="📊 Stock Scanner", layout="wide")
st.title("📈 Smart Stock Screener")

@st.cache_data
STOCKS = [
    "AAPL", "NVDA", "TSLA", "AMD", "MSFT", "GOOGL", "META",
    "AMZN", "NFLX", "INTC", "NVTS", "PLUG", "BAC", "JPM",
    "COIN", "SOFI", "RIVN", "NIO", "LCID", "SNAP"
]

Stocks = STOCKS

selected = st.selectbox("اختر سهم للتحليل التفصيلي", stocks)

results = []

for stock in stocks[:100]:  # أول 100 سهم (خفيف على الجوال)
    df = yf.download(stock, period="3mo", progress=False)
    if df.empty:
        continue

    close = df["Close"].squeeze()
    price = close.iloc[-1]
    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, 20).sma_indicator().iloc[-1]

    stop = round(price * 0.95, 2)
    target = round(price * 1.05, 2)

    if rsi < 30 and price > sma:
        signal = "BUY"
    elif rsi > 70 and price < sma:
        signal = "SELL"
    else:
        signal = "HOLD"

    results.append([stock, price, rsi, sma, stop, target, signal])

df = pd.DataFrame(
    results,
    columns=["Stock", "Price", "RSI", "SMA20", "Stop Loss", "Target", "Signal"]
)

def color_signal(val):
    if val == "BUY":
        return "background-color: #b6fcd5"
    if val == "SELL":
        return "background-color: #ffb6b6"
    return ""

st.subheader("📊 نتائج السوق")
st.dataframe(df.style.applymap(color_signal, subset=["Signal"]))

# 📉 رسم بياني
st.subheader(f"📉 Chart: {selected}")
chart = yf.download(selected, period="6mo", progress=False)
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=chart.index,
    open=chart["Open"],
    high=chart["High"],
    low=chart["Low"],
    close=chart["Close"]
))
st.plotly_chart(fig, use_container_width=True)

# 📰 أخبار
st.subheader("📰 Latest News")
news = yf.Ticker(selected).news[:5]
for n in news:
    st.markdown(f"🔹 [{n['title']}]({n['link']})")
