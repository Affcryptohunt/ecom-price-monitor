import requests
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# =========================
# LOAD TELEGRAM CONFIG
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# =========================
# SEND TELEGRAM ALERT
# =========================
def send_telegram_alert(name, price, url):

    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    message = f"""
🚨 PRICE DROP DETECTED 🚨

📦 {name}

💰 Current Price: ${price}

🎯 Target Price Reached!

⚡ This is a potential deal

🔗 {url}
"""

    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(send_url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)