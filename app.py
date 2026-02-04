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

# ===== Sidebar =====
st.sidebar.header("⚙️ الإعدادات")

selected_stocks = st.sidebar.multiselect(
    "اختر الأسهم",
    STOCKS,
    default=STOCKS[:5]
)

signal_filter = st.sidebar.selectbox(
    "فلترة الإشارات",
    ["ALL", "BUY", "SELL", "HOLD"]
)

# ===== أخبار السهم =====
def get_news(symbol):
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if news:
            return news[0]["title"]
    except:
        pass
    return "No recent news"

# ===== تحليل السهم =====
@st.cache_data(ttl=600)
def analyze_stock(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty or "Close" not in df:
        return {
            "Stock": symbol,
            "Price": None,
            "RSI": None,
            "SMA20": None,
            "Signal": "NO DATA",
            "Prediction": "—",
            "News": "—"
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

    if rsi < 30:
        prediction = "📈 Possible Rise"
    elif rsi > 70:
        prediction = "📉 Possible Drop"
    else:
        prediction = "➡️ Sideways"

    return {
        "Stock": symbol,
        "Price": round(float(price), 2),
        "RSI": round(float(rsi), 2),
        "SMA20": round(float(sma), 2),
        "Signal": signal,
        "Prediction": prediction,
        "News": get_news(symbol)
    }

# ===== تشغيل التحليل =====
results = []

with st.spinner("⏳ Analyzing stocks..."):
    for stock in selected_stocks:
        results.append(analyze_stock(stock))

df_results = pd.DataFrame(results)

# فلترة الإشارة
if signal_filter != "ALL":
    df_results = df_results[df_results["Signal"] == signal_filter]

# ===== جدول النتائج =====
st.subheader("📋 Stock Analysis")
st.dataframe(df_results, use_container_width=True)

# ===== إبراز الإشارات =====
st.subheader("📌 Trading Signals")

for _, row in df_results.iterrows():
    if row["Signal"] == "BUY":
        st.success(f"🟢 {row['Stock']} → BUY | {row['Prediction']}")
    elif row["Signal"] == "SELL":
        st.error(f"🔴 {row['Stock']} → SELL | {row['Prediction']}")
    elif row["Signal"] == "HOLD":
        st.info(f"🟡 {row['Stock']} → HOLD | {row['Prediction']}")
    else:
        st.warning(f"⚪ {row['Stock']} → NO DATA")

# ===== رسم RSI =====
st.subheader("📈 RSI Chart")

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
