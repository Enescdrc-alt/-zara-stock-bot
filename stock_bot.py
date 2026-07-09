import os, requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = "https://www.zara.com/tr/tr/yun-karisimli-kusakli-kruvaze-kaban-p02949150.html?v1=496682900"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text.lower()

if "sepete ekle" in html or "add to cart" in html:
    send("Zara kaban stoğa gelmiş olabilir!\n" + URL)
else:
    print("Henüz stok yok.")
