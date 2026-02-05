import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(page_title="التحليل الذكي للأسهم", layout="wide")
st.title("🧠 منصة التحليل الذكي للأسهم")

# ===== الإعدادات =====
CAPITAL = st.sidebar.number_input("💰 رأس المال", 500, 1_000_000, 5000, 500)
RISK = st.sidebar.selectbox("⚠️ نسبة المخاطرة", ["منخفضة", "متوسطة", "عالية"])
RISK_FACTOR = {"منخفضة": 0.05, "متوسطة": 0.1, "عالية": 0.2}[RISK]

# ===== الأسهم =====
STOCKS = [
    "AAPL","NVDA","TSLA","AMD","MSFT","GOOGL","META",
    "AMZN","NFLX","PLUG","NVTS","SOFI","COIN","INTC",
    "BABA","RIVN","UBER","PYPL","SNAP"
]

selected = st.multiselect("📌 اختر الأسهم", STOCKS, default=STOCKS[:7])

# ===== ترجمة الإشارات =====
def signal_ar(score):
    if score >= 75:
        return "🟢 شراء قوي"
    elif score >= 60:
        return "🟢 شراء"
    elif score >= 45:
        return "🟡 انتظار"
    else:
        return "🔴 بيع"

def trend_ar(score):
    if score >= 75:
        return "📈 صعود قوي"
    elif score >= 60:
        return "📈 صعود محتمل"
    elif score >= 45:
        return "➡️ تذبذب"
    else:
        return "📉 هبوط محتمل"

def rsi_state(rsi):
    if rsi < 30:
        return "تشبع بيعي"
    elif rsi > 70:
        return "تشبع شرائي"
    else:
        return "طبيعي"

# ===== التحليل =====
@st.cache_data(ttl=600)
def analyze(stock):
    df = yf.download(stock, period="3mo", interval="1d", progress=False)
    if df.empty:
        return None

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()

    price = close.iloc[-1]
    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, 20).sma_indicator().iloc[-1]
    atr = AverageTrueRange(high, low, close).average_true_range().iloc[-1]

    # ===== ذكاء التقييم =====
    score = 50
    score += 25 if rsi < 30 else -15 if rsi > 70 else 0
    score += 15 if price > sma else -10
    score = max(0, min(100, score))

    # ===== الأهداف =====
    t1 = price + atr
    t2 = price + atr * 2
    t3 = price + atr * 3
    sl = price - atr * 1.5

    # ===== الكمية =====
    allocation = CAPITAL * RISK_FACTOR * (score / 100)
    qty = int(allocation / price) if score >= 60 else 0

    return {
        "السهم": stock,
        "السعر": round(price, 2),
        "RSI": round(rsi, 2),
        "حالة RSI": rsi_state(rsi),
        "التقييم %": score,
        "الإشارة": signal_ar(score),
        "التوقع": trend_ar(score),
        "🎯 هدف 1": round(t1, 2),
        "🎯 هدف 2": round(t2, 2),
        "🎯 هدف 3": round(t3, 2),
        "🛑 وقف الخسارة": round(sl, 2),
        "📦 الكمية المقترحة": qty
    }

# ===== تشغيل =====
data = []
for s in selected:
    r = analyze(s)
    if r:
        data.append(r)

df = pd.DataFrame(data)

st.subheader("📊 جدول التحليل الذكي")
st.dataframe(df, use_container_width=True)

# ===== تنبيهات =====
st.subheader("🚨 تنبيهات ذكية")
for _, row in df.iterrows():
    if "شراء" in row["الإشارة"]:
        st.success(
            f"{row['السهم']} | {row['الإشارة']} | "
            f"هدف: {row['🎯 هدف 2']} | وقف: {row['🛑 وقف الخسارة']}"
        )
    elif "بيع" in row["الإشارة"]:
        st.error(f"{row['السهم']} | {row['الإشارة']} | خطر مرتفع")
