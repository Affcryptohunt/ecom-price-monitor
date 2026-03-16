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
            content = response.text
            
            # 1. Clean the content - remove commas to avoid "1,299" becoming "1"
            clean_content = content.replace(',', '')
            
            # 2. Find every dollar amount (e.g., $53.99, $5.99)
            # This regex is specifically built for the Amazon 'superscript' format
            matches = re.findall(r'\$\s?(\d+\.\d{2})', clean_content)
            
            if matches:
                # Convert to floats and remove duplicates
                prices = list(set([float(p) for p in matches]))
                
                # DEBUG: This will show up in your Streamlit 'Manage App' logs
                print(f"DEBUG: Found these prices for {url}: {prices}")
                
                # 3. Pick the price closest to target
                # If target is $60 and prices are [5.99, 53.99], it WILL pick 53.99
                actual_price = min(prices, key=lambda x: abs(x - target_price))
                return actual_price
                
            return "Price Not Found"
        return f"Bridge Error {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

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