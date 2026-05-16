import time

from analyzer import analyze_stock
from telegram_alerts import send_alert
from alert_state import sent_alerts

stocks = [
    "AAPL","MSFT","TSLA","NVDA","AMZN","META","AMD","GOOGL",
    "NFLX","PLTR","INTC","BABA","ORCL","SPY","QQQ"
]

print("🚀 Engine started... running every 5 minutes")

while True:

    for s in stocks:
        r = analyze_stock(s)

        if r:
            key = f"{r['Symbol']}_{r['Decision']}"

            if r["Decision"] == "STRONG BUY" and key not in sent_alerts:
                send_alert(
                    f"🚨 STRONG BUY\n"
                    f"{r['Symbol']}\n"
                    f"Price: {r['Price']}\n"
                    f"Score: {r['Score']}"
                )
                sent_alerts.add(key)

    print("✅ Cycle done. Sleeping 5 minutes...")
    time.sleep(300)  # 5 minutes