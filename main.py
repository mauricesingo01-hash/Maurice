import os, re, sqlite3, telebot
BOT_TOKEN = os.getenv("
8770001740:AAHUhMpp_qzt1FbAI3dvxMzYtmRSrbvMmks","").strip()
ADMIN_ID = int(os.getenv("8710817326","0") or 0)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
conn = sqlite3.connect('bot.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, ref TEXT, transaction_id TEXT UNIQUE, montant TEXT, payeur TEXT, file_id TEXT, chat_id INTEGER)")
conn.commit()
def masque(n):
    n=re.sub(r'\s+','',n or '')
    return f"{n[:5]}****{n[-4:]}" if len(n)>=8 else n
@bot.message_handler(commands=['start','help'])
def s(m): bot.reply_to(m,"Envoie une capture avec ref en legende.\nAdmin: /bilan /get <ref>")
@bot.message_handler(commands=['bilan'])
def bilan(m):
    if ADMIN_ID and m.from_user.id!=ADMIN_ID: return
    cur.execute("SELECT COUNT(*) FROM transactions")
    t=cur.fetchone()[0]
    bot.reply_to(m,f"BILAN\nTotal: {t}")
@bot.message_handler(commands=['get'])
def get_ref(m):
    if ADMIN_ID and m.from_user.id!=ADMIN_ID: return
    p=m.text.split()
    if len(p)<2: bot.reply_to(m,"Usage: /get 041015938130"); return
    ref=p[1].strip()
    cur.execute("SELECT ref,transaction_id,montant,payeur,file_id FROM transactions WHERE ref=? OR transaction_id=?",(ref,ref))
    row=cur.fetchone()
    if not row:
        cur.execute("SELECT ref,transaction_id,montant,payeur,file_id FROM transactions WHERE transaction_id LIKE ?", (f"%{ref}%",))
        row=cur.fetchone()
    if row:
        r_ref,r_tid,mont,pay,file_id=row
        cap=f"TROUVE\nRef: {r_ref}\nMontant: {mont}\nPayeur: {masque(pay)}"
        if file_id: bot.send_photo(m.chat.id,file_id,caption=cap)
        else: bot.reply_to(m,cap)
    else: bot.reply_to(m,f"Ref {ref} introuvable")
@bot.message_handler(content_types=['photo'])
def photo(m):
    file_id=m.photo[-1].file_id
    cap=m.caption or ""
    mm=re.search(r'(\d{9,13})',cap)
    ref=mm.group(1) if mm else None
    if not ref: bot.reply_to(m,"Ajoute la ref en legende ex: 041015938130"); return
    cur.execute("SELECT id FROM transactions WHERE transaction_id=?",(ref,))
    if cur.fetchone(): bot.reply_to(m,f"DOUBLON: {ref}"); return
    cur.execute("INSERT OR IGNORE INTO transactions (ref,transaction_id,montant,payeur,file_id,chat_id) VALUES (?,?,?,?,?,?)",(ref,ref,cap,"",file_id,m.chat.id))
    conn.commit()
    bot.reply_to(m,f"Enregistre: {ref}")
print("Bot demarre...")
bot.infinity_polling()
