import streamlit as st
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_KEY = os.getenv('SCRAPER_API_KEY')
DB_FILE = 'monitor_list.json'

def get_price(url, selector=None):
    # If no selector, assume it's a Shopify store and use the .js trick
    target_url = f"{url}.js" if not selector else url
    proxy_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={target_url}"
    
    try:
        response = requests.get(proxy_url, timeout=30)
        if response.status_code == 200:
            if not selector:
                return float(response.json()['price'] / 100)
            else:
                # This part would use BeautifulSoup to find a specific price tag
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                price_text = soup.select_one(selector).text
                return float(''.join(c for c in price_text if c.isdigit() or c == '.'))
        return f"Error {response.status_code}"
    except Exception as e:
        return "Connection Failed"

# --- UI LOGIC ---
st.title("🎯 Pro Price Sniper")

with st.sidebar:
    st.header("🛡️ Backend Status")
    if BOT_TOKEN and API_KEY:
        st.success("Credentials Loaded Privately")
    else:
        st.error("Missing .env keys!")

# Add Section
with st.expander("➕ Add New Tracker"):
    name = st.text_input("Product Name")
    url = st.text_input("URL")
    # New: Optional selector for non-Shopify sites
    selector = st.text_input("CSS Selector (Optional)", help="Leave blank for Anker/Shopify")
    target = st.number_input("Target Price", value=0.0)
    
    if st.button("Add"):
        db = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
        db.append({"name": name, "url": url, "selector": selector, "target": target})
        json.dump(db, open(DB_FILE, 'w'))
        st.rerun()

# Run Section
if os.path.exists(DB_FILE):
    products = json.load(open(DB_FILE))
    if st.button("🚀 RUN ALL SCANS", type="primary"):
        for p in products:
            current = get_price(p['url'], p.get('selector'))
            if isinstance(current, float):
                st.write(f"✅ {p['name']}: `${current}`")
                # Telegram alert logic here...
            else:
                st.error(f"❌ {p['name']}: {current}")