import os
import time
import threading
from flask import Flask
import yfinance as yf

from telegram_alerts import send_alert

app = Flask(__name__)

stocks = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "META", "GOOGL", "AMD", "SPY", "QQQ"
]

sent_alerts = set()


@app.route("/")
def home():
    return "Telegram market bot is running"


def analyze_stock(symbol):
    hist = yf.Ticker(symbol).history(period="3mo")

    if hist.empty or len(hist) < 30:
        return None

    close = hist["Close"]
    volume = hist["Volume"]

    price = close.iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]

    score = 0

    if price > ma20:
        score += 1

    if close.iloc[-1] > close.iloc[-2]:
        score += 1

    if volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]:
        score += 1

    entry = round(price, 2)
    sl = round(price * 0.98, 2)
    tp = round(price * 1.04, 2)

    return {
        "Symbol": symbol,
        "Price": round(price, 2),
        "Score": score,
        "Entry": entry,
        "SL": sl,
        "TP": tp
    }


def bot_loop():
    time.sleep(15)

    while True:
        try:
            opportunities = []

            for symbol in stocks:
                try:
                    result = analyze_stock(symbol)

                    if result and result["Score"] >= 2:
                        opportunities.append(result)

                    time.sleep(3)

                except Exception as e:
                    print(f"Error {symbol}: {e}")

            if opportunities:
                opportunities = sorted(
                    opportunities,
                    key=lambda x: x["Score"],
                    reverse=True
                )

                message = "Market Opportunities\n\n"

                for r in opportunities[:5]:
                    key = f"{r['Symbol']}_{r['Score']}"

                    if key not in sent_alerts:
                        message += (
                            f"{r['Symbol']}\n"
                            f"Price: {r['Price']}\n"
                            f"Score: {r['Score']}/3\n"
                            f"Entry: {r['Entry']}\n"
                            f"SL: {r['SL']}\n"
                            f"TP: {r['TP']}\n"
                            f"----------------\n"
                        )
                        sent_alerts.add(key)

                if message != "Market Opportunities\n\n":
                    send_alert(message)

            print("Cycle done. Sleeping 10 minutes...")
            time.sleep(600)

        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(600)


threading.Thread(target=bot_loop, daemon=True).start()

port = int(os.environ.get("PORT", 10000))
print("STARTING TELEGRAM BOT SERVER")
app.run(host="0.0.0.0", port=port)