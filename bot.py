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

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for link in soup.select("a[id^='thread_title']"):

        title = link.text.strip()
        url = "https://samsguide.work/" + link["href"]

        posts.append((title, url))

    return posts


def load_seen():

    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []


def save_seen(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


seen = load_seen()

posts = get_posts()

for title, url in posts:

    if url not in seen:

        send_message(title, url)

        seen.append(url)

save_seen(seen)
