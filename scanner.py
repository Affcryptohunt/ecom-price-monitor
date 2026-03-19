from database import load_products
from notifier import send_telegram_alert
from database import save_price
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# CONFIG
# =========================
MAX_WORKERS = 10

# =========================
# GET PRICE
# =========================
def get_price(url, target_price):

    bridge_url = f"https://r.jina.ai/{url}"

    try:
        response = requests.get(bridge_url, timeout=15)

        if response.status_code != 200:
            return None

        content = response.text.lower()

        matches = re.findall(r'(\d+\.\d{2})', content)

        prices = []

        for p in matches:
            try:
                val = float(p)

                if (target_price * 0.3) < val < (target_price * 3.0):
                    prices.append(val)

            except:
                continue

        if not prices:
            return None

        return min(prices, key=lambda x: abs(x - target_price))

    except:
        return None


# =========================
# SCAN ONE PRODUCT
# =========================
def scan_product(product):

    price = get_price(product["url"], product["target"])

    # SAVE PRICE IF VALID
    if isinstance(price, float):
        save_price(product["id"], price)

    result = {
        "name": product["name"],
        "price": price,
        "target": product["target"],
        "url": product["url"]
    }

    return result


# =========================
# SCAN ALL PRODUCTS (PARALLEL)
# =========================
def scan_all_products():

    products = load_products()

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [executor.submit(scan_product, p) for p in products]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            # =========================
            # ALERT LOGIC
            # =========================
            if isinstance(result["price"], float):

                if result["price"] <= result["target"]:

                    send_telegram_alert(
                        result["name"],
                        result["price"],
                        result["url"]
                    )

    return results