import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import os
import time

# --- CONFIGURATION ---
# We force sorting by 'dateline' (Creation Date) and 'desc' (Newest first)
TARGET_URL = "https://samsguide.work/forumdisplay.php?f=19&sort=dateline&order=desc&daysprune=-1"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SCRAPEOPS_API_KEY = os.environ["SCRAPEOPS_API_KEY"]
DATA_FILE = "posts.json"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def get_scrapeops_url(url):
    payload = {
        'api_key': SCRAPEOPS_API_KEY,
        'url': url,
        'bypass': 'cloudflare_level_2',
        'render_js': 'true'
    }
    return 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)

def get_posts():
    try:
        # Increased timeout to handle the Level 2 JS rendering
        response = requests.get(get_scrapeops_url(TARGET_URL), timeout=60)
        if response.status_code != 200:
            print(f"Proxy failed: {response.status_code}")
            return None # Return None to indicate a connection error

        soup = BeautifulSoup(response.text, "html.parser")
        posts = []
        # Find thread links - targeting the specific vBulletin ID pattern
        for link in soup.select("a[id^='thread_title']"):
            title = link.text.strip()
            url = "https://samsguide.work/" + link["href"]
            posts.append((title, url))
        
        return posts
    except Exception as e:
        print(f"Error: {e}")
        return None

def load_seen():
    try:
        with open(DATA_FILE) as f: return json.load(f)
    except: return []

def save_seen(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# --- EXECUTION ---
seen = load_seen()
current_posts = get_posts()

if current_posts is None:
    send_telegram("⚠️ *Bot Alert*: Failed to connect to the forum. Check logs.")
else:
    new_found = False
    for title, url in current_posts:
        if url not in seen:
            send_telegram(f"✨ *New Post Found!*\n\n{title}\n[Link to Post]({url})")
            seen.append(url)
            new_found = True
            time.sleep(1) # Prevent Telegram spam block

    if not new_found:
        send_telegram("✅ *System Check*: No new posts found this hour.")

    save_seen(seen)
