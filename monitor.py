import time
import requests

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    raise ImportError("Install selenium and webdriver-manager to run this script: pip install selenium webdriver-manager")

# 1. Credentials
BOT_TOKEN = '8660476898:AAHsR8IHxgf2kQGfm33E9aS1MdENjtaxLpI'
CHAT_ID = '7154715567'
URL_TO_TRACK = "https://www.startech.com.bd/tp-link-tl-wn725n-nano-usb-adapter"


def get_price_stealth():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(URL_TO_TRACK)
        wait = WebDriverWait(driver, 15)
        price_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".p-item-price, ins, .price, .prod-price, .price-tag, [id*=price]"))
        )
        price = price_element.text.strip()
        return price
    except Exception as e:
        return f"Error: {e}"
    finally:
        driver.quit()


def send_alert(text):
    try:
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(api_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram send failed: {e}")


if __name__ == "__main__":
    print("🕵️ Opening Stealth Browser...")
    price = get_price_stealth()
    message = f"🎯 *Stealth Price Check*\n\nProduct: TP-Link Nano\nPrice Found: `{price}`"
    send_alert(message)
    print(f"✅ Result: {price}")