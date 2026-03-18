from database import load_products, add_product, delete_product

import streamlit as st
import os
import requests
import re

# =========================
# SETUP & SECRETS
# =========================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# PRICE ENGINE
# =========================
def get_price(url, target_price):
    bridge_url = f"https://r.jina.ai/{url}"

    try:
        response = requests.get(bridge_url, timeout=20)

        if response.status_code != 200:
            return f"Error {response.status_code}"

        content = response.text.lower()

        matches = re.findall(r'(\d+\.\d{2})', content)

        if not matches:
            return "Price Not Found"

        prices = []
        for p in matches:
            try:
                val = float(p)

                if (target_price * 0.3) < val < (target_price * 3.0):
                    prices.append(val)

            except:
                continue

        if not prices:
            return "No Valid Price"

        return min(prices, key=lambda x: abs(x - target_price))

    except:
        return "Connection Failed"

# =========================
# UI
# =========================
st.set_page_config(page_title="Pro Price Sniper", page_icon="🎯")
st.title("🎯 Pro Price Sniper")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("🛡️ Backend Status")

    if BOT_TOKEN and CHAT_ID:
        st.success("✅ Telegram Connected")
    else:
        st.error("❌ Missing Telegram Secrets")

    st.info("Using Jina AI Bridge (Anti-Bot Bypass)")

# =========================
# ADD PRODUCT
# =========================
st.subheader("➕ Add Product")

name = st.text_input("Product Name")
url = st.text_input("Product URL")
target = st.number_input("Target Price", min_value=0.0)

if st.button("Add Product"):

    if not name or not url:
        st.error("Please fill all fields")

    elif not url.startswith("http"):
        st.error("Invalid URL")

    else:
        add_product(name, url, target)
        st.success("Product added!")
        st.rerun()

st.divider()

# =========================
# PRODUCT LIST
# =========================
st.subheader("📋 Monitored Products")

products = load_products()

if not products:
    st.info("No products added yet")

for p in products:

    col1, col2 = st.columns([5, 1])

    with col1:
        st.write(f"**{p['name']}** — Target: ${p['target']}")

    with col2:
        if st.button("🗑️", key=f"del_{p['id']}"):
            delete_product(p["id"])
            st.rerun()

st.divider()

# =========================
# RUN SCAN
# =========================
if st.button("🚀 RUN ALL SCANS", type="primary", use_container_width=True):

    if not products:
        st.warning("No products to scan")
    else:
        st.info("Scanning prices...")

        for p in products:

            price = get_price(p["url"], p["target"])

            if isinstance(price, float):

                if price <= p["target"]:
                    st.success(f"🔥 DEAL FOUND: {p['name']} → ${price}")
                else:
                    st.write(f"{p['name']} → ${price}")

            else:
                st.warning(f"{p['name']} → {price}")

# =========================
# CLEAR ALL
# =========================
if st.button("🗑️ Clear All Products"):

    if os.path.exists("data/products.json"):
        os.remove("data/products.json")
        st.success("All products deleted")
        st.rerun()