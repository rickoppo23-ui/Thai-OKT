import requests
import sqlite3
import time
from bs4 import BeautifulSoup
import os

FORUM_URL = "https://samsguide.work/forumdisplay.php?f=19"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHECK_INTERVAL = 60

conn = sqlite3.connect("posts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts(
    url TEXT PRIMARY KEY
)
""")

conn.commit()


def send_message(title, url):

    message = f"""
🚨 New Forum Post

{title}

{url}
"""

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


def get_posts():

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(FORUM_URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for link in soup.select("a[id^='thread_title']"):

        title = link.text.strip()

        url = "https://samsguide.work/" + link["href"]

        posts.append((title, url))

    return posts


def check_posts():

    posts = get_posts()

    for title, url in posts:

        cursor.execute("SELECT url FROM posts WHERE url=?", (url,))
        exists = cursor.fetchone()

        if not exists:

            send_message(title, url)

            cursor.execute(
                "INSERT INTO posts(url) VALUES(?)",
                (url,)
            )

            conn.commit()


while True:

    try:

        check_posts()

    except Exception as e:

        print("Error:", e)

    time.sleep(CHECK_INTERVAL)
