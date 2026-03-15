import os
import json
import requests
from dotenv import load_dotenv
import re

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = 'monitor_list.json'

def extract_price(text):
    # Regex to find currency symbols followed by numbers (e.g., $29.99 or £15.00)
    match = re.search(r'\$\s?(\d+[\.,]\d{2})', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def run_sniper():
    if not os.path.exists(DB_FILE): return
    with open(DB_FILE, 'r') as f:
        products = json.load(f)

    for p in products:
        # Route through the successful Jina Bridge
        bridge_url = f"https://r.jina.ai/{p['url']}"
        try:
            res = requests.get(bridge_url, timeout=30)
            if res.status_code == 200:
                current_price = extract_price(res.text)
                
                if current_price and current_price <= p['target']:
                    msg = f"🔥 **Sniper Alert!**\n\nProduct: {p['name']}\nTarget: ${p['target']}\n**Current: ${current_price}**\n\n[View Product]({p['url']})"
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Error checking {p['name']}: {e}")

if __name__ == "__main__":
    run_sniper()