import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import AverageTrueRange

# ================== إعداد الصفحة ==================
st.set_page_config(page_title="التحليل الذكي للأسهم", layout="wide")
st.title("🧠 منصة التحليل الذكي للأسهم")

# ================== سجل الصفقات ==================
if "trades" not in st.session_state:
    st.session_state.trades = []

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

# ================== الأسهم ==================
ALL_STOCKS = [
    "AAPL","NVDA","TSLA","AMD","MSFT","GOOGL","META","AMZN","NFLX",
    "PLUG","NVTS","SOFI","COIN","INTC","BABA","RIVN","UBER","PYPL","SNAP"
]

manual = st.text_input("✍️ أدخل رموز الأسهم (مثال: AAPL,TSLA,PLUG)")
if manual:
    selected_stocks = [s.strip().upper() for s in manual.split(",")]

# ================== دوال مساعدة ==================
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
@st.cache_data(ttl=300)
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

    # ===== ذكاء التقييم =====
    score = 50
    score += 25 if rsi < 30 else -15 if rsi > 70 else 0
    score += 15 if price > sma else -10

    if INTERVAL in ["5m", "15m"]:
        score *= 0.9

    score = int(max(0, min(100, score)))

    # ===== الأهداف =====
    target1 = price + atr
    target2 = price + atr * 2
    target3 = price + atr * 3
    stop_loss = price - atr * 1.5

    allocation = CAPITAL * RISK_FACTOR * (score / 100)
    quantity = int(allocation / price) if score >= 60 else 0

    return {
        "السهم": stock,
        "السعر": round(price, 2),
        "RSI": round(rsi, 2),
        "حالة RSI": rsi_state(rsi),
        "📍 نوع الدخول": entry,
        "التقييم %": score,
        "الإشارة": signal_ar(score),
        "التوقع": prediction_ar(score),
        "🎯 هدف 1": round(target1, 2),
        "🎯 هدف 2": round(target2, 2),
        "🎯 هدف 3": round(target3, 2),
        "🛑 وقف الخسارة": round(stop_loss, 2),
        "📦 الكمية المقترحة": quantity
    }

# ================== التشغيل ==================
results = []
for stock in selected_stocks:
    res = analyze_stock(stock)
    if res:
        results.append(res)

df_results = pd.DataFrame(results)

st.subheader("📊 جدول التحليل الذكي")
st.dataframe(df_results, use_container_width=True)

# ================== التنبيهات ==================
st.subheader("🚨 إشارات فورية")
for _, row in df_results.iterrows():
    if "شراء" in row["الإشارة"]:
        st.success(
            f"{row['السهم']} | {row['الإشارة']} | {row['📍 نوع الدخول']} | "
            f"هدف: {row['🎯 هدف 2']} | وقف: {row['🛑 وقف الخسارة']}"
        )
    elif "بيع" in row["الإشارة"]:
        st.error(f"{row['السهم']} | {row['الإشارة']} | خطر مرتفع")
    else:
        st.info(f"{row['السهم']} | {row['الإشارة']} | {row['التوقع']}")

# ================== سجل الصفقات ==================
st.subheader("🧾 سجل الصفقات")

for _, row in df_results.iterrows():
    if "شراء" in row["الإشارة"]:
        if st.button(f"➕ إضافة صفقة {row['السهم']}"):
            st.session_state.trades.append({
                "السهم": row["السهم"],
                "سعر الدخول": row["السعر"],
                "الكمية": row["📦 الكمية المقترحة"],
                "الهدف": row["🎯 هدف 2"],
                "وقف الخسارة": row["🛑 وقف الخسارة"],
                "التقييم": row["التقييم %"]
            })

if st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades)
    st.dataframe(trades_df, use_container_width=True)
else:
    st.info("لا توجد صفقات مسجلة حتى الآن")
