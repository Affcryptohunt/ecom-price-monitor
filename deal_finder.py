import requests
import re

def find_deals(keyword):

    search_url = f"https://r.jina.ai/https://www.amazon.com/s?k={keyword.replace(' ', '+')}"

    try:
        response = requests.get(search_url, timeout=15)

        if response.status_code != 200:
            return []

        content = response.text

        # Extract possible titles (longer text chunks)
        titles = re.findall(r'>([^<>]{30,150})<', content)

        # Extract prices
        prices = re.findall(r'(\d+\.\d{2})', content)

        deals = []

        # Pair loosely (not perfect but works)
        for i in range(min(len(titles), len(prices))):

            try:
                price = float(prices[i])

                # 🔥 relaxed filter (IMPORTANT)
                if 5 < price < 1000:

                    deals.append({
                        "title": titles[i].strip(),
                        "price": price
                    })

            except:
                continue

        # Remove duplicates
        unique = []
        seen = set()

        for d in deals:
            if d["title"] not in seen:
                unique.append(d)
                seen.add(d["title"])

        return unique[:10]

    except Exception as e:
        print("Error:", e)
        return []