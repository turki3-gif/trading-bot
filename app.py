import streamlit as st
import yfinance as yf
import pandas as pd

from analyzer import analyze_stock
from telegram_alerts import send_alert
from alert_state import sent_alerts

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

st.title("📊 Pro Trading Dashboard")

# 🔥 سوق الأسهم
stocks = [
    "AAPL","MSFT","TSLA","NVDA","AMZN","META","AMD","GOOGL",
    "NFLX","PLTR","INTC","BABA","ORCL","SPY","QQQ"
]

results = []

# 🔍 تحليل السوق
for s in stocks:
    r = analyze_stock(s)

    if r:
        results.append(r)

        # 🔔 منع التكرار + إشعار تيليجرام
        key = f"{r['Symbol']}_{r['Decision']}"

        if r["Decision"] == "STRONG BUY" and key not in sent_alerts:
            send_alert(
                f"🚨 STRONG BUY SIGNAL\n"
                f"Stock: {r['Symbol']}\n"
                f"Price: {r['Price']}\n"
                f"Score: {r['Score']}"
            )
            sent_alerts.add(key)

# 📊 عرض النتائج
if results:

    df = pd.DataFrame(results)
    df = df.sort_values("Score", ascending=False)

    # تنسيق الأرقام
    df["Price"] = df["Price"].round(2)
    df["RSI"] = df["RSI"].round(1)
    df["MACD"] = df["MACD"].round(3)
    df["RVOL"] = df["RVOL"].round(2)

    st.subheader("📊 Market Overview")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 🔥 Top 5
    st.subheader("🔥 Top 5 Stocks")
    st.dataframe(df.head(5), use_container_width=True, hide_index=True)

    # 📈 اختيار سهم
    selected = st.selectbox("Select Stock", df["Symbol"].tolist())

    chart = yf.Ticker(selected).history(period="3mo")

    st.subheader(f"📈 {selected} Chart")
    st.line_chart(chart["Close"])

    # 📌 تفاصيل
    st.subheader("📌 Signal Details")
    st.dataframe(df[df["Symbol"] == selected], use_container_width=True, hide_index=True)

else:
    st.warning("No signals found")