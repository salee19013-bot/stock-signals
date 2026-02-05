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

AUTO_REFRESH_SECONDS = 60

if time.time() - st.session_state.last_refresh > AUTO_REFRESH_SECONDS:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

st.button("🔄 تحديث الآن", on_click=lambda: st.experimental_rerun())

# ================== إدخال المستخدم ==================
st.subheader("✏️ أدخل اسم السهم")
user_stock = st.text_input(
    "مثال: AAPL أو TSLA أو NVDA",
    value="AAPL"
).upper().strip()

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

        if rsi < 30:
            signal = "شراء 🟢"
            outlook = "تشبع بيعي واحتمال ارتداد صاعد"
        elif rsi > 70:
            signal = "بيع 🔴"
            outlook = "تشبع شرائي واحتمال هبوط"
        else:
            signal = "انتظار 🟡"
            outlook = "حركة عرضية"

        score = round((50 - abs(50 - rsi)) / 10, 2)

        return {
            "السهم": symbol,
            "السعر الحالي": round(price, 2),
            "RSI": round(rsi, 2),
            "المتوسط 20": round(sma, 2),
            "الإشارة": signal,
            "التوقع": outlook,
            "التقييم": score,
            "هدف صعود": round(price * 1.05, 2),
            "هدف هبوط": round(price * 0.95, 2)
        }

    except Exception:
        return None

# ================== تشغيل ==================
st.title("📊 إشارات الأسهم الذكية")

if user_stock:
    result = analyze_stock(user_stock)

    if result:
        st.success(f"تم تحليل السهم {user_stock}")
        st.dataframe(pd.DataFrame([result]), use_container_width=True)
    else:
        st.error("❌ السهم غير موجود أو لا توجد بيانات حالياً")
