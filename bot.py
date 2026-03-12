import cloudscraper
from bs4 import BeautifulSoup
import json
import os

URL = "https://samsguide.work/forumdisplay.php?f=19"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
DATA_FILE = "posts.json"

def get_posts():
    # This creates a scraper that can bypass common bot protections
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        # We add a delay to look more human
        response = scraper.get(URL, timeout=20)
        
        if response.status_code == 403:
            print("Access denied (403). The website is blocking the bot.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        posts = []

        # Find the thread titles
        for link in soup.select("a[id^='thread_title']"):
            title = link.text.strip()
            url = "https://samsguide.work/" + link["href"]
            posts.append((title, url))

        print(f"Success! Found {len(posts)} posts.")
        return posts

    except Exception as e:
        print(f"An error occurred: {e}")
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
