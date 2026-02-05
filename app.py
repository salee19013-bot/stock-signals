import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import plotly.graph_objects as go

# إعداد الصفحة
st.set_page_config(page_title="إشارات الأسهم", layout="wide")
st.title("📊 إشارات الأسهم")

# قائمة الأسهم
STOCKS = [
    "AAPL", "NVDA", "TSLA", "AMD", "MSFT", "GOOGL", "META",
    "AMZN", "NFLX", "INTC", "NVTS", "PLUG", "BAC", "JPM",
    "COIN", "SOFI", "RIVN", "NIO", "LCID", "SNAP"
]

# ===== الترجمة =====
SIGNAL_AR = {
    "BUY": "🟢 شراء",
    "SELL": "🔴 بيع",
    "HOLD": "🟡 انتظار",
    "NO DATA": "⚪ لا توجد بيانات"
}

PREDICTION_AR = {
    "📈 Possible Rise": "📈 احتمال صعود",
    "📉 Possible Drop": "📉 احتمال هبوط",
    "➡️ Sideways": "➡️ تذبذب / استقرار",
    "—": "—"
}

# ===== الشريط الجانبي =====
st.sidebar.header("⚙️ الإعدادات")

selected_stocks = st.sidebar.multiselect(
    "اختر الأسهم",
    STOCKS,
    default=STOCKS[:5]
)

signal_filter = st.sidebar.selectbox(
    "فلترة الإشارات",
    ["الكل", "شراء", "بيع", "انتظار"]
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
    return "لا توجد أخبار حديثة"

# ===== تحليل السهم =====
@st.cache_data(ttl=600)
def analyze_stock(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty or "Close" not in df:
        return {
            "السهم": symbol,
            "السعر": None,
            "RSI": None,
            "حالة RSI": "—",
            "المتوسط 20": None,
            "الإشارة": SIGNAL_AR["NO DATA"],
            "التوقع": "—",
            "الخبر": "—"
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
        rsi_status = "تشبع بيعي"
    elif rsi > 70:
        prediction = "📉 Possible Drop"
        rsi_status = "تشبع شرائي"
    else:
        prediction = "➡️ Sideways"
        rsi_status = "منطقة طبيعية"

    return {
        "السهم": symbol,
        "السعر": round(float(price), 2),
        "RSI": round(float(rsi), 2),
        "حالة RSI": rsi_status,
        "المتوسط 20": round(float(sma), 2),
        "الإشارة": SIGNAL_AR.get(signal, signal),
        "التوقع": PREDICTION_AR.get(prediction, prediction),
        "الخبر": get_news(symbol)
    }

# ===== تشغيل التحليل =====
results = []

with st.spinner("⏳ جارٍ تحليل الأسهم..."):
    for stock in selected_stocks:
        results.append(analyze_stock(stock))

df_results = pd.DataFrame(results)

# ===== فلترة الإشارات =====
if signal_filter != "الكل":
    df_results = df_results[df_results["الإشارة"].str.contains(signal_filter)]

# ===== عرض الجدول =====
st.subheader("📋 نتائج التحليل")
st.dataframe(df_results, use_container_width=True)

# ===== إبراز الإشارات =====
st.subheader("📌 التوصيات")

for _, row in df_results.iterrows():
    if "شراء" in row["الإشارة"]:
        st.success(f"🟢 {row['السهم']} → شراء | {row['التوقع']}")
    elif "بيع" in row["الإشارة"]:
        st.error(f"🔴 {row['السهم']} → بيع | {row['التوقع']}")
    elif "انتظار" in row["الإشارة"]:
        st.info(f"🟡 {row['السهم']} → انتظار | {row['التوقع']}")
    else:
        st.warning(f"⚪ {row['السهم']} → لا توجد بيانات")

# ===== رسم RSI =====
st.subheader("📈 مؤشر RSI")

if not df_results.empty:
    fig = go.Figure()
    fig.add_bar(
        x=df_results["السهم"],
        y=df_results["RSI"],
        text=df_results["الإشارة"]
    )
    fig.update_layout(
        title="مؤشر القوة النسبية RSI",
        yaxis_title="RSI",
        xaxis_title="السهم"
    )
    st.plotly_chart(fig, use_container_width=True)
