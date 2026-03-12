import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://samsguide.work/forumdisplay.php?f=19"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

DATA_FILE = "posts.json"


def send_message(title, url):

    msg = f"🚨 New forum post\n\n{title}\n{url}"

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


def get_posts():
    # This header set mimics a real Chrome browser on Windows
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        r = requests.get(URL, headers=headers, timeout=15)
        
        # This will print the error in your GitHub Logs if it's blocked
        if r.status_code != 200:
            print(f"Failed to access forum. Status Code: {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        posts = []

        # Find the thread links
        links = soup.select("a[id^='thread_title']")
        print(f"Found {len(links)} posts on the page.") # Logging check

        for link in links:
            title = link.text.strip()
            url = "https://samsguide.work/" + link["href"]
            posts.append((title, url))

        return posts
    except Exception as e:
        print(f"Error during scraping: {e}")
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


seen = []

posts = get_posts()

for title, url in posts:

    if url not in seen:

        send_message(title, url)

        seen.append(url)

save_seen(seen)
send_message("Test System", "If you see this, the bot is connected!")
