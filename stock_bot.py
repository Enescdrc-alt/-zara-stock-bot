import os
import re
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://www.zara.com/tr/tr/yun-karisimli-kusakli-kruvaze-kaban-p02949150.html?v1=496682900"
TARGET_SIZES = ["M", "L"]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )

def is_available_word(value):
    value = str(value).lower()
    return any(word in value for word in [
        "in_stock", "instock", "available", "add", "buyable", "sellable",
        "stokta", "sepete ekle"
    ]) and not any(word in value for word in [
        "out_of_stock", "sold_out", "unavailable", "tükendi", "stokta yok"
    ])

def find_sizes(obj, found=None):
    if found is None:
        found = {}

    if isinstance(obj, dict):
        text = json.dumps(obj, ensure_ascii=False).lower()

        size_name = None
        for key in ["name", "sizeName", "label", "description"]:
            if key in obj and str(obj[key]).upper() in TARGET_SIZES:
                size_name = str(obj[key]).upper()

        if size_name:
            found[size_name] = is_available_word(text)

        for value in obj.values():
            find_sizes(value, found)

    elif isinstance(obj, list):
        for item in obj:
            find_sizes(item, found)

    return found

html = requests.get(URL, headers=HEADERS, timeout=30).text

json_blocks = re.findall(
    r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
    html,
    flags=re.DOTALL
)

all_sizes = {}

for block in json_blocks:
    try:
        data = json.loads(block)
        result = find_sizes(data)
        all_sizes.update(result)
    except Exception:
        pass

available = [size for size, ok in all_sizes.items() if size in TARGET_SIZES and ok]

if available:
    send_message(
        "🟢 Zara kaban stoğa gelmiş olabilir!\n"
        f"Beden: {', '.join(available)}\n\n"
        f"{URL}"
    )
else:
    print("M/L için stok görünmüyor.")
    print("Bulunan bedenler:", all_sizes)