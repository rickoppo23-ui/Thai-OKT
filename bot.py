import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import os
import time
import base64
import re

# GitHub Configuration
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]
REPO = "rickoppo23-ui/Thai-OKT"  
FILE_PATH = "posts.json"

# Bot & API Configuration
TARGET_URL = "https://www.sbf.net.nz/forumdisplay.php?f=19&sort=dateline&order=desc&daysprune=-1"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SCRAPEOPS_API_KEY = os.environ["SCRAPEOPS_API_KEY"]

def send_telegram(text):
    """Sends a single message to Telegram with Markdown formatting."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload)

def get_posts():
    """Fetches posts using cloudscraper to bypass basic protections."""
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        response = scraper.get(TARGET_URL, timeout=30)
        if response.status_code == 200:
            return parse_posts(response.text)
    except Exception as e:
        print(f"Scraper error: {e}")
    return None

def parse_posts(html):
    """Extracts titles and unique thread IDs from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for link in soup.select("a[id^='thread_title']"):
        title = link.text.strip()
        raw_href = link["href"]
        
        # Regex to find the numeric ID (e.g., t=1110702)
        match = re.search(r't=(\d+)', raw_href)
        if match:
            thread_id = match.group(1)
            # Create a clean link without the volatile session ID
            clean_url = f"https://www.sbf.net.nz/showthread.php?t={thread_id}"
            posts.append({"id": thread_id, "title": title, "url": clean_url})
    return posts

def load_seen():
    """Retrieves the list of previously seen IDs from GitHub."""
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json()["content"]
        decoded = base64.b64decode(content).decode()
        return json.loads(decoded)
    return []

def save_seen(data):
    """Saves the updated list of IDs back to GitHub."""
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Get current file SHA to perform update
    r = requests.get(url, headers=headers)
    sha = r.json()["sha"] if r.status_code == 200 else None

    content = base64.b64encode(json.dumps(data).encode()).decode()
    payload = {
        "message": "Bot update: refreshed seen posts",
        "content": content,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)

# --- EXECUTION LOGIC ---

seen_ids = load_seen()
current_posts = get_posts()

if current_posts is None:
    send_telegram("⚠️ *Bot Alert*: Could not reach the forum.")
else:
    new_posts_to_report = []

    for post in current_posts:
        if post["id"] not in seen_ids:
            new_posts_to_report.append(post)
            seen_ids.append(post["id"])

    if new_posts_to_report:
        # Build a single summary message
        message_lines = ["✨ *New Posts Found*:\n"]
        for p in new_posts_to_report:
            # Format: - [Title](URL)
            line = f"• [{p['title']}]({p['url']})"
            message_lines.append(line)
        
        final_message = "\n".join(message_lines)
        send_telegram(final_message)
    else:
        send_telegram("✅ *System Check*: No new posts since last run.")

    save_seen(seen_ids)
