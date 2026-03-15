import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def test():
    print("🚀 Using Jina Stealth Bridge...")
    
    # We send the URL through Jina's "Reader" which bypasses Cloudflare
    target_url = "https://www.anker.com/products/a1653-anker-nano-power-bank-22-5w-built-in-usb-c-connector"
    jina_url = f"https://r.jina.ai/{target_url}"
    
    try:
        # Jina returns a clean version of the page
        res = requests.get(jina_url, timeout=30)
        
        if res.status_code == 200:
            print("✅ CONNECTION SUCCESS!")
            # The price is in the text. Let's find it.
            # Usually looks like "Price: $29.99" or "$29.99"
            content = res.text
            if "$" in content:
                print("✅ Price detected in page content!")
                
                # Simple extraction: find the dollar sign and grab the next few numbers
                start = content.find("$")
                price_str = content[start:start+7].strip()
                
                # Send to Telegram
                msg = f"🔥 Sniper is LIVE!\nFound Price: {price_str}\nStatus: Firewall Bypassed via Jina"
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg})
            else:
                print("❓ Connected, but no '$' found. Site might be out of stock.")
        else:
            print(f"❌ Jina Bridge failed: {res.status_code}")
            
    except Exception as e:
        print(f"⚠️ System Error: {e}")

if __name__ == "__main__":
    test()