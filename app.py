import streamlit as st
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import pandas as pd

st.set_page_config(page_title="Stock Signals", layout="wide")
st.title("📊 Stock Signals")

stocks = st.text_input("رموز الأسهم (مفصولة بفاصلة)", "AAPL,NVDA,TSLA,AMD,PLUG")
symbols = [s.strip().upper() for s in stocks.split(",") if s.strip()]

data = []

for stock in symbols:
    try:
        df = yf.download(stock, period="3mo", interval="1d", progress=False)
        if df.empty:
            continue

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

        data.append({
            "Stock": stock,
            "Price": round(float(price), 2),
            "RSI": round(float(rsi), 2),
            "SMA20": round(float(sma), 2),
            "Signal": signal
        })

    except:
        data.append({
            "Stock": stock,
            "Price": "-",
            "RSI": "-",
            "SMA20": "-",
            "Signal": "ERROR"
        })

st.dataframe(pd.DataFrame(data), use_container_width=True)
