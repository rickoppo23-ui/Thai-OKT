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
        'bypass': 'cloudflare_level_2',
        'render_js': 'true' 
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
    # We will try up to 3 times before giving up
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}: Fetching forum posts...")
            response = requests.get(get_scrapeops_url(TARGET_URL), timeout=60)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                posts = []
                for link in soup.select("a[id^='thread_title']"):
                    title = link.text.strip()
                    url = "https://samsguide.work/" + link["href"]
                    posts.append((title, url))
                
                print(f"Successfully found {len(posts)} posts.")
                return posts
            else:
                print(f"Proxy returned status: {response.status_code}. Retrying...")
                
        except requests.exceptions.ReadTimeout:
            print("The request timed out. Retrying...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        # Wait 5 seconds before trying again
        time.sleep(5)

    print("All 3 attempts failed.")
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
