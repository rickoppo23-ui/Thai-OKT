import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import os
import time

# --- CONFIGURATION ---
TARGET_URL = "https://samsguide.work/forumdisplay.php?f=19"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SCRAPEOPS_API_KEY = os.environ["SCRAPEOPS_API_KEY"]
DATA_FILE = "posts.json"

def get_scrapeops_url(url):
    payload = {
        'api_key': SCRAPEOPS_API_KEY,
        'url': url,
        'bypass': 'cloudflare_level_1' # This tells the proxy to use anti-Cloudflare settings
    }
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

def send_message(title, url):
    msg = f"🚨 New forum post\n\n{title}\n{url}"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def get_posts():
    try:
        # We send the request through the ScrapeOps Proxy
        response = requests.get(get_scrapeops_url(TARGET_URL), timeout=30)
        
        if response.status_code != 200:
            print(f"Proxy failed. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        posts = []

        # Find the thread links
        links = soup.select("a[id^='thread_title']")
        for link in links:
            title = link.text.strip()
            url = "https://samsguide.work/" + link["href"]
            posts.append((title, url))

        print(f"Successfully found {len(posts)} posts via Proxy.")
        return posts
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

# --- MAIN EXECUTION ---
def load_seen():
    try:
        with open(DATA_FILE) as f: return json.load(f)
    except: return []

def save_seen(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

seen = load_seen()
# seen = [] # UNCOMMENT THIS TO TEST: Sends all current posts once

posts = get_posts()
for title, url in posts:
    if url not in seen:
        send_message(title, url)
        seen.append(url)
        time.sleep(1)

save_seen(seen)
