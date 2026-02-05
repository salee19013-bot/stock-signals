import streamlit as st
import yfinance as yf
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

st.set_page_config(page_title="إشارات الأسهم", layout="wide")

# ================== تحديث تلقائي ==================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

AUTO_REFRESH_SECONDS = 60  # تحديث كل دقيقة

if time.time() - st.session_state.last_refresh > AUTO_REFRESH_SECONDS:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# زر تحديث يدوي
st.button("🔄 تحديث الآن", on_click=lambda: st.experimental_rerun())

# ================== الأسهم ==================
STOCKS = [
    "AAPL","NVDA","TSLA","AMD","PLUG","META","MSFT","AMZN",
    "GOOGL","NFLX","INTC","BA","COIN","SNAP","NIO",
    "XPEV","PDD","SOFI","LCID"
]

# ================== التحليل ==================
def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if df.empty:
            return None

        close = df["Close"].squeeze()

        rsi = RSIIndicator(close).rsi().iloc[-1]
        sma = SMAIndicator(close, 20).sma_indicator().iloc[-1]
        price = close.iloc[-1]

        # الإشارة
        if rsi < 30:
            signal = "شراء 🟢"
            outlook = "متوقع ارتداد صاعد"
        elif rsi > 70:
            signal = "بيع 🔴"
            outlook = "تشبع شرائي واحتمال هبوط"
        else:
            signal = "انتظار 🟡"
            outlook = "حركة جانبية"

        # تقييم ذكي
        score = round((50 - abs(50 - rsi)) / 10, 2)

        # أهداف
        target_up = round(price * 1.05, 2)
        target_down = round(price * 0.95, 2)

        return {
            "السهم": symbol,
            "السعر": round(price, 2),
            "RSI": round(rsi, 2),
            "المتوسط 20": round(sma, 2),
            "الإشارة": signal,
            "التوقع": outlook,
            "التقييم": score,
            "هدف صعود": target_up,
            "هدف هبوط": target_down
        }

    except Exception:
        return None

# ================== تشغيل ==================
st.title("📊 إشارات الأسهم الذكية")
st.caption("تحديث تلقائي + تحليل فني + توقع اتجاه")

data = []
for s in STOCKS:
    res = analyze_stock(s)
    if res:
        data.append(res)

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)
