from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os
import time

URL = "https://samsguide.work/forumdisplay.php?f=19"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
DATA_FILE = "posts.json"

def send_message(title, url):
    msg = f"🚨 New forum post\n\n{title}\n{url}"
    # Use standard requests for Telegram as it's not blocked
    import requests as tg_req
    tg_req.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def get_posts():
    try:
        # 'impersonate' makes the request look exactly like Chrome 120 on Windows
        r = requests.get(URL, impersonate="chrome120", timeout=30)
        
        if r.status_code != 200:
            print(f"Cloudflare is still blocking us. Status: {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        posts = []

        for link in soup.select("a[id^='thread_title']"):
            title = link.text.strip()
            url = "https://samsguide.work/" + link["href"]
            posts.append((title, url))

        print(f"Successfully found {len(posts)} posts.")
        return posts
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def load_seen():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []

def save_seen(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- EXECUTION ---
seen = load_seen()
# FORCE RESET FOR TESTING: Un-comment the next line to send all current posts once
# seen = [] 

posts = get_posts()

for title, url in posts:
    if url not in seen:
        send_message(title, url)
        seen.append(url)
        time.sleep(1) # Slow down to avoid Telegram spam limits

save_seen(seen)
