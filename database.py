import json
import os
import sqlite3
from datetime import datetime

# Path to your products file
DB_FILE = "data/products.json"


# =========================
# LOAD PRODUCTS
# =========================
def load_products():

    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# =========================
# SAVE PRODUCTS
# =========================
def save_products(products):

    with open(DB_FILE, "w") as f:
        json.dump(products, f, indent=2)


# =========================
# ADD PRODUCT
# =========================
def add_product(name, url, target_price, cost=0, selling_price=0):

    products = load_products()

    if products:
        new_id = max(p.get("id", 0) for p in products) + 1
    else:
        new_id = 1

    new_product = {
        "id": new_id,
        "name": name,
        "url": url,
        "target": target_price,
        "cost": cost,
        "selling_price": selling_price
    }

    products.append(new_product)
    save_products(products)


# =========================
# DELETE PRODUCT
# =========================
def delete_product(product_id):

    products = load_products()
    products = [p for p in products if p["id"] != product_id]
    save_products(products)


# =========================
# INIT DATABASE
# =========================
def init_db():

    conn = sqlite3.connect("data/price_history.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# SAVE PRICE
# =========================
def save_price(product_id, price):

    conn = sqlite3.connect("data/price_history.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO price_history (product_id, price, timestamp)
        VALUES (?, ?, ?)
    """, (product_id, price, datetime.now().isoformat()))

    conn.commit()
    conn.close()


# =========================
# GET PRICE HISTORY
# =========================
def get_price_history(product_id):

    conn = sqlite3.connect("data/price_history.db")
    c = conn.cursor()

    c.execute("""
        SELECT price, timestamp
        FROM price_history
        WHERE product_id = ?
        ORDER BY timestamp ASC
    """, (product_id,))

    data = c.fetchall()
    conn.close()

    return data