import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import AverageTrueRange
import time

# ================== إعداد الصفحة ==================
st.set_page_config(page_title="التحليل الذكي للأسهم", layout="wide")
st.title("🧠 منصة التحليل الذكي للأسهم (تحديث فوري)")

# ================== تحديث تلقائي ==================
REFRESH = st.sidebar.slider("🔄 التحديث التلقائي (ثانية)", 15, 300, 60, 15)

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh >= REFRESH:
    st.session_state.last_refresh = time.time()
    st.rerun()

st.caption(f"آخر تحديث: {time.strftime('%H:%M:%S')}")

# ================== الإعدادات ==================
CAPITAL = st.sidebar.number_input(
    "💰 رأس المال", min_value=500, max_value=1_000_000, value=5000, step=500
)

RISK = st.sidebar.selectbox("⚠️ نسبة المخاطرة", ["منخفضة", "متوسطة", "عالية"])
RISK_FACTOR = {"منخفضة": 0.05, "متوسطة": 0.1, "عالية": 0.2}[RISK]

TIMEFRAME_LABEL = st.sidebar.selectbox(
    "⏱️ الإطار الزمني",
    ["تحليل يومي", "مضاربة 15 دقيقة", "سكالبينغ 5 دقائق"]
)

if TIMEFRAME_LABEL == "تحليل يومي":
    INTERVAL = "1d"
    PERIOD = "3mo"
elif TIMEFRAME_LABEL == "مضاربة 15 دقيقة":
    INTERVAL = "15m"
    PERIOD = "7d"
else:
    INTERVAL = "5m"
    PERIOD = "7d"

# ================== إدخال الأسهم ==================
manual = st.text_input(
    "✍️ أدخل رموز الأسهم (مثال: AAPL,TSLA,NVDA,PLUG)",
    value="AAPL,NVDA,TSLA"
)

STOCKS = [s.strip().upper() for s in manual.split(",") if s.strip()]

# ================== دوال ذكية ==================
def signal_ar(score):
    if score >= 75:
        return "🟢 شراء قوي"
    elif score >= 60:
        return "🟢 شراء"
    elif score >= 45:
        return "🟡 انتظار"
    else:
        return "🔴 بيع"

def prediction_ar(score):
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

def entry_type(price, high20, rsi):
    if price > high20 and rsi > 55:
        return "🔼 دخول كسر"
    elif rsi < 30:
        return "🔁 دخول ارتداد"
    else:
        return "—"

# ================== التحليل ==================
@st.cache_data(ttl=30)
def analyze_stock(stock):
    df = yf.download(stock, period=PERIOD, interval=INTERVAL, progress=False)

    if df.empty or len(df) < 30:
        return None

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()

    price = float(close.iloc[-1])
    rsi = float(RSIIndicator(close).rsi().iloc[-1])
    sma = float(SMAIndicator(close, 20).sma_indicator().iloc[-1])
    atr = float(AverageTrueRange(high, low, close).average_true_range().iloc[-1])
    high20 = float(df["High"].rolling(20).max().iloc[-1])

    entry = entry_type(price, high20, rsi)

    score = 50
    score += 25 if rsi < 30 else -15 if rsi > 70 else 0
    score += 15 if price > sma else -10

    if INTERVAL in ["5m", "15m"]:
        score *= 0.9

    score = int(max(0, min(100, score)))

    target1 = price + atr
    target2 = price + atr * 2
    stop_loss = price - atr * 1.5

    allocation = CAPITAL * RISK_FACTOR * (score / 100)
    qty = int(allocation / price) if score >= 60 else 0

    return {
        "السهم": stock,
        "السعر": round(price, 2),
        "RSI": round(rsi, 2),
        "حالة RSI": rsi_state(rsi),
        "📍 الدخول": entry,
        "التقييم %": score,
        "الإشارة": signal_ar(score),
        "التوقع": prediction_ar(score),
        "🎯 هدف": round(target2, 2),
        "🛑 وقف": round(stop_loss, 2),
        "📦 الكمية": qty
    }

# ================== التشغيل ==================
results = []
for s in STOCKS:
    r = analyze_stock(s)
    if r:
        results.append(r)

df = pd.DataFrame(results)

st.subheader("📊 النتائج (تحديث فوري)")
st.dataframe(df, use_container_width=True)

# ================== إشارات ==================
st.subheader("🚨 إشارات مباشرة")
for _, row in df.iterrows():
    if "شراء" in row["الإشارة"]:
        st.success(
            f"{row['السهم']} | {row['الإشارة']} | {row['📍 الدخول']} | "
            f"هدف: {row['🎯 هدف']} | وقف: {row['🛑 وقف']}"
        )
    elif "بيع" in row["الإشارة"]:
        st.error(f"{row['السهم']} | {row['الإشارة']} | خطر")
    else:
        st.info(f"{row['السهم']} | {row['الإشارة']} | {row['التوقع']}")
