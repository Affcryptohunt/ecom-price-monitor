from scanner import scan_all_products
from database import load_products, add_product, delete_product, init_db, get_price_history
import streamlit as st
import os
import requests
import re
from deal_finder import find_deals

init_db()

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
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Pro Price Sniper", page_icon="🎯")

# =========================
# HEADER
# =========================
st.title("🎯 Pro Price Sniper")

products = load_products()
total_products = len(products)

st.subheader("📊 Dashboard Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Products Tracked", total_products)

with col2:
    st.metric("Active Alerts", "Live")

with col3:
    st.metric("System Status", "Running")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("⚙️ System Panel")

    if BOT_TOKEN and CHAT_ID:
        st.success("🟢 Telegram Connected")
    else:
        st.error("🔴 Telegram Not Connected")

    st.markdown("---")
    st.caption("Pro Price Sniper v1.0")

# =========================
# ADD PRODUCT
# =========================
st.markdown("---")
st.subheader("➕ Add Product")

name = st.text_input("Product Name")
url = st.text_input("Product URL")
target = st.number_input("Target Price", min_value=0.0)

cost = st.number_input("Your Cost Price ($)", min_value=0.0, key="cost_input")
selling_price = st.number_input("Your Selling Price ($)", min_value=0.0, key="selling_input")

if st.button("Add Product"):

    if not name or not url:
        st.error("Please fill all fields")

    elif not url.startswith("http"):
        st.error("Invalid URL")

    else:
        add_product(name, url, target, cost, selling_price)
        st.success("Product added!")
        st.rerun()

# =========================
# PRODUCT LIST
# =========================
st.markdown("---")
st.subheader("📋 Monitored Products")

products = load_products()

if not products:
    st.info("No products added yet")

for p in products:

    with st.container():
        st.markdown("---")

        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"### 📦 {p['name']}")

            # PRICE HISTORY
            history = get_price_history(p["id"])

            if history:
                prices = [h[0] for h in history]
                timestamps = [h[1] for h in history]
                latest_price = prices[-1]

                if latest_price <= p["target"]:
                    st.success(f"🔥 ${latest_price} — DEAL FOUND")
                else:
                    st.info(f"💲 Current Price: ${latest_price}")

                st.write(f"🎯 Target: ${p['target']}")

                # CHART
                st.line_chart({"Price": prices}, height=150)
                st.caption(f"Last updated: {timestamps[-1]}")

            else:
                st.warning("No price data yet")

            # PROFIT CALCULATOR
            cost = p.get("cost", 0)
            selling = p.get("selling_price", 0)

            if cost > 0 and selling > 0:
                profit = selling - cost
                margin = (profit / cost) * 100 if cost != 0 else 0

                colp1, colp2 = st.columns(2)

                with colp1:
                    st.metric("Profit", f"${profit:.2f}")

                with colp2:
                    st.metric("Margin", f"{margin:.1f}%")

        with col2:
            if st.button("🗑️", key=f"del_{p['id']}"):
                delete_product(p["id"])
                st.rerun()

# =========================
# RUN SCAN
# =========================
st.markdown("---")

if st.button("🚀 RUN ALL SCANS", type="primary", use_container_width=True):

    if not products:
        st.warning("No products to scan")

    else:
        st.info("Scanning all products...")

        results = scan_all_products()

        st.subheader("📊 Scan Results")

        for r in results:

            if isinstance(r["price"], float):

                if r["price"] <= r["target"]:
                    st.success(f"🔥 DEAL: {r['name']} → ${r['price']}")
                else:
                    st.write(f"{r['name']} → ${r['price']}")

            else:
                st.warning(f"{r['name']} → Price not found")

# =========================
# CLEAR ALL
# =========================
if st.button("🗑️ Clear All Products"):

    if os.path.exists("data/products.json"):
        os.remove("data/products.json")
        st.success("All products deleted")
        st.rerun()

# =========================
# DEAL FINDER
# =========================
st.markdown("---")
st.subheader("💰 Deal Finder")

keyword = st.text_input("Enter product keyword")

if st.button("Find Deals"):

    if not keyword:
        st.warning("Enter a keyword")

    else:
        st.info("Searching for deals...")

        deals = find_deals(keyword)

        if not deals:
            st.warning("No deals found")

        for d in deals:
            st.success(f"{d['title']} → ${d['price']}")