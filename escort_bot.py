import cloudscraper
from bs4 import BeautifulSoup
import os

URL = "https://www.ts-dating.com/shemale-escorts/Singapore/"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

DATA_FILE = "escort_last.txt"

scraper = cloudscraper.create_scraper()


def send_message(title, url):
    msg = f"🔥 ESCORT\n\n{title}\n{url}"

    scraper.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )


def get_latest():
    r = scraper.get(URL)

    if r.status_code != 200:
        print("Escort site blocked:", r.status_code)
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.select("a"):
        href = link.get("href")

        if href and "/profile/" in href:
            title = link.text.strip()
            url = "https://www.ts-dating.com" + href
            return title, url

    return None


def load_last():
    try:
        with open(DATA_FILE) as f:
            return f.read().strip()
    except:
        return None


def save_last(url):
    with open(DATA_FILE, "w") as f:
        f.write(url)


last = load_last()
latest = get_latest()

if latest:
    title, url = latest

    if url != last:
        send_message(title, url)
        save_last(url)
        print("New escort post sent")
    else:
        print("No new escort post")
