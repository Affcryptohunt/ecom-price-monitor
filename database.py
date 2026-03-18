import json
import os

# Path to your products file
DB_FILE = "data/products.json"


# =========================
# LOAD PRODUCTS
# =========================
def load_products():
    """
    Loads all products from JSON file
    """

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
    """
    Saves product list to JSON file
    """

    with open(DB_FILE, "w") as f:
        json.dump(products, f, indent=2)


# =========================
# ADD PRODUCT
# =========================
def add_product(name, url, target_price):
    products = load_products()

    # Generate proper unique ID
    if products:
        new_id = max(p.get("id", 0) for p in products) + 1
    else:
        new_id = 1

    new_product = {
        "id": new_id,
        "name": name,
        "url": url,
        "target": target_price
    }

    products.append(new_product)
    save_products(products)


# =========================
# DELETE PRODUCT
# =========================
def delete_product(product_id):
    """
    Deletes a product by ID
    """

    products = load_products()

    products = [p for p in products if p["id"] != product_id]

    save_products(products)