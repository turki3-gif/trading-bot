import requests

TOKEN = "8869546589:AAF43X5pbCfD3FXpQbpKyuNaOLnJZf9Y2x0"
CHAT_ID = "5905589977"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)