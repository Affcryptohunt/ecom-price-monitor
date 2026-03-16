import streamlit as st
import os
import requests
import json
import re

# 1. SETUP & SECRETS
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

# These pull from Streamlit Cloud "Secrets" automatically
BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
DB_FILE = 'monitor_list.json'

# 2. THE ENGINE (Firewall Bypass)
def get_price(url, target_price):
    bridge_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(bridge_url, timeout=30)
        if response.status_code == 200:
            # We use .lower() to make searching easier
            content = response.text.lower()
            
            # 1. Look for numbers that look like prices (e.g. 53.99 or 464.99)
            # We don't even look for the '$' anymore because Amazon splits it in the code
            matches = re.findall(r'(\d+\.\d{2})', content)
            
            if matches:
                prices = []
                for p in matches:
                    try:
                        val = float(p)
                        # 2. THE SANITY FLOOR (The most important part!)
                        # Only accept prices that are between 30% and 300% of target
                        # This kills the $5.99 accessories for a $400 camera
                        if (target_price * 0.3) < val < (target_price * 3.0):
                            prices.append(val)
                    except: continue

                if prices:
                    # 3. Pick the one closest to what we want
                    return min(prices, key=lambda x: abs(x - target_price))
                
            return "Main Price Not Found"
        return f"Bridge Error {response.status_code}"
    except Exception:
        return "Connection Failed"

# 3. UI LOGIC
st.set_page_config(page_title="Pro Price Sniper", page_icon="🎯")
st.title("🎯 Pro Price Sniper")

with st.sidebar:
    st.header("🛡️ Backend Status")
    if BOT_TOKEN and CHAT_ID:
        st.success("✅ Stealth Engine Active")
    else:
        st.error("❌ Missing Secrets!")
    st.info("Bypassing Anker/Cloudflare via Jina Bridge")

# Add Section
with st.expander("➕ Add New Tracker", expanded=True):
    name = st.text_input("Product Name (e.g. Anker Power Bank)")
    url = st.text_input("URL")
    target = st.number_input("Target Price ($)", value=0.0)
    
    if st.button("Add Product", use_container_width=True):
        if name and url:
            db = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
            db.append({"name": name, "url": url, "target": target})
            with open(DB_FILE, 'w') as f:
                json.dump(db, f)
            st.success(f"Added {name}!")
            st.rerun()

st.divider()

# List & Run Section
if os.path.exists(DB_FILE):
    products = json.load(open(DB_FILE))
    st.subheader("📋 Active Monitors")
    
    # Create a column layout for each product row
    for i, p in enumerate(products):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{p['name']}** (Target: `${p['target']}`)")
        with col2:
            # Unique key for each button using the index
            if st.button("🗑️", key=f"del_{i}"):
                products.pop(i)
                with open(DB_FILE, 'w') as f:
                    json.dump(products, f)
                st.rerun()

    st.divider()
    
    if st.button("🚀 RUN ALL SCANS", type="primary", use_container_width=True):
        # ... (your existing scan logic remains here)
    
    # Simple Delete Option
    if st.button("🗑️ Clear All Monitors", type="secondary"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()