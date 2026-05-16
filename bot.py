import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN", "")

DB_FILE = "users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, uid):
    uid = str(uid)
    if uid not in db:
        db[uid] = {"ball": 0, "korilgan": [], "testlar": [], "streak": 0}
    return db[uid]

BOSQICHLAR = [
    {"id": 1, "nomi": "Kinematika",    "emoji": "🏃", "min": 0,    "max": 150},
    {"id": 2, "nomi": "Mexanika",      "emoji": "⚙",  "min": 150,  "max": 350},
    {"id": 3, "nomi": "Termodinamika", "emoji": "🌡",  "min": 350,  "max": 600},
    {"id": 4, "nomi": "Elektr",        "emoji": "⚡",  "min": 600,  "max": 900},
    {"id": 5, "nomi": "Magnit",        "emoji": "🧲",  "min": 900,  "max": 1250},
    {"id": 6, "nomi": "Optika",        "emoji": "🔭",  "min": 1250, "max": 1650},
    {"id": 7, "nomi": "Kvant fizika",  "emoji": "⚛",  "min": 1650, "max": 2100},
]

DARSLAR = [
    {"id": 1,  "b": 1, "nomi": "Tezlik va tezlanish",     "video": "https://youtube.com/watch?v=EXAMPLE1",  "ball": 30},
    {"id": 2,  "b": 1, "nomi": "Erkin tushish",           "video": "https://youtube.com/watch?v=EXAMPLE2",  "ball": 30},
    {"id": 3,  "b": 1, "nomi": "Nishab harakati",         "video": "https://youtube.com/watch?v=EXAMPLE3",  "ball": 30},
    {"id": 4,  "b": 2, "nomi": "1-Newton qonuni",         "video": "https://youtube.com/watch?v=EXAMPLE4",  "ball": 30},
    {"id": 5,  "b": 2, "nomi": "2-Newton qonuni",         "video": "https://youtube.com/watch?v=EXAMPLE5",  "ball": 30},
    {"id": 6,  "b": 2, "nomi": "3-Newton qonuni",         "video": "https://youtube.com/watch?v=EXAMPLE6",  "ball": 30},
    {"id": 7,  "b": 3, "nomi": "Issiqlik miqdori",        "video": "https://youtube.com/watch?v=EXAMPLE7",  "ball": 30},
    {"id": 8,  "b": 3, "nomi": "Ideal gaz qonunlari",     "video": "https://youtube.com/watch?v=EXAMPLE8",  "ball": 30},
    {"id": 9,  "b": 4, "nomi": "Elektr zaryadi",          "video": "https://youtube.com/watch?v=EXAMPLE9",  "ball": 30},
    {"id": 10, "b": 4, "nomi": "Tok kuchi va kuchlanish", "video": "https://youtube.com/watch?v=EXAMPLE10", "ball": 30},
]

TESTLAR = [
    {"id": 1, "b": 1, "nomi": "Kinematika testi", "savollar": [
        {"s": "Tezlanish formulasi?", "v": ["a=v/t","a=F/m","a=mv","a=s/t"], "j": 0},
        {"s": "Erkin tushish tezlanishi?", "v": ["5 m/s2","9.8 m/s2","15 m/s2","1 m/s2"], "j": 1},
        {"s": "Yol formulasi s=?", "v": ["s=v*t","s=a*t","s=v/t","s=F*t"], "j": 0},
    ]},
    {"id": 2, "b": 2, "nomi": "Mexanika testi", "savollar": [
        {"s": "F=ma da m nima?", "v": ["Tezlanish","Massa","Kuch","Vaqt"], "j": 1},
        {"s": "Impuls p=?", "v": ["p=m*v","p=F*t2","p=m*a","p=E/v"], "j": 0},
        {"s": "1-Newton qonuni nima?", "v": ["Doim harakat","Kuch yoq-tinch yoki tekis","Doim tezlashadi","Doim sekinlashadi"], "j": 1},
    ]},
]

def hozirgi_b(ball):
    for b in reversed(BOSQICHLAR):
        if ball >= b["min"]:
            return b
    return BOSQICHLAR[0]

def pbar(ball, b):
    pct = min(100, int((ball - b["min"]) / (b["max"] - b["min"]) * 100)) if b["max"] > b["min"] else 100
    return "🟦" * (pct // 10) + "⬜" * (10 - pct // 10) + f" {pct}%"

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    u = get_user(db, update.effective_user.id)
    save_db(db)
    b = hozirgi_b(u["ball"])
    kb = [
        [InlineKeyboardButton("📚 Darslar", callback_data="darslar"),
         InlineKeyboardButton("📝 Testlar", callback_data="testlar")],
        [InlineKeyboardButton("🏆 Bosqichlar", callback_data="bosqichlar"),
         InlineKeyboardButton("👤 Profil", callback_data="profil")],
        [InlineKeyboardButton("📊 Reyting", callback_data="reyting")],
    ]
    txt = (f"*Fizika Kursi*\n\n"
           f"Salom, *{update.effective_user.first_name}*!\n\n"
           f"Bosqich: *{b['emoji']} {b['nomi']}*\n"
           f"Ball: *{u['ball']}*\n"
           f"{pbar(u['ball'], b)}\n\n"
           f"Darslar: *{len(u['korilgan'])}* | Testlar: *{len(u['testlar'])}*\n\n"
           f"Nima qilmoqchisiz?")
    await update.effective_message.reply_text(txt, parse_mode="Markdown",
                                              reply_markup=InlineKeyboardMarkup(kb))

async def darslar_menu(update, ctx):
    q = update.callback_query
    await q.answer()
    db = load_db()
    u = get_user(db, q.from_user.id)
    b = hozirgi_b(u["ball"])
    darslar = [d for d in DARSLAR if d["b"] == b["id"]]
    kb = []
    for d in darslar:
        done = d["id"] in u["korilgan"]
        st = "✅" if done else "▶️"
        bl = "bajarildi" if done else f"+{d['ball']} ball"
        kb.append([InlineKeyboardButton(f"{st} {d['nomi']} ({bl})", callback_data=f"dars_{d['id']}")])
    kb.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")])
    await q.edit_message_text(f"📚 *Darslar*\n\nDarsni tanlang:",
                              parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def dars_korish(update, ctx):
    q = update.callback_query
    await q.answer()
    did = int(q.data.split("_")[1])
    d = next((x for x in DARSLAR if x["id"] == did), None)
    if not d:
        return
    db = load_db()
    u = get_user(db, q.from_user.id)
    if did in u["korilgan"]:
        kb = [[InlineKeyboardButton("📚 Darslar", callback_data="darslar")]]
        await q.edit_message_text("Bu darsni allaqachon kordingiz!", reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = [
        [InlineKeyboardButton("✅ Kordim! Ball olish", callback_data=f"dtasdi_{did}")],
        [InlineKeyboardButton("📚 Ortga", callback_data="darslar")],
    ]
    await q.edit_message_text(
        f"*{d['nomi']}*\n\nVideo: {d['video']}\n\nKorib boldingizmi?",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def dars_tasdi(update, ctx):
    q = update.callback_query
    await q.answer()
    did = int(q.data.split("_")[1])
    d = next((x for x in DARSLAR if x["id"] == did), None)
    if not d:
        return
    db = load_db()
    u = get_user(db, q.from_user.id)
    msg = ""
    if did not in u["korilgan"]:
        u["korilgan"].append(did)
        u["ball"] += d["ball"]
        save_db(db)
        b_eski = hozirgi_b(u["ball"] - d["ball"])
        b_yangi = hozirgi_b(u["ball"])
        if b_yangi["id"] > b_eski["id"]:
            msg = f"\n\n🎉 *Yangi bosqich: {b_yangi['emoji']} {b_yangi['nomi']}!*"
    kb = [[InlineKeyboardButton("📚 Darslar", callback_data="darslar"),
           InlineKeyboardButton("🏠 Bosh", callback_data="bosh")]]
    await q.edit_message_text(
        f"✅ *Barakalla!*\n\n+{d['ball']} ball!\nJami: *{u['ball']}*{msg}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def testlar_menu(update, ctx):
    q = update.callback_query
    await q.answer()
    db = load_db()
    u = get_user(db, q.from_user.id)
    b = hozirgi_b(u["ball"])
    testlar = [t for t in TESTLAR if t["b"] <= b["id"]]
    kb = []
    for t in testlar:
        done = t["id"] in u["testlar"]
        st = "✅" if done else "📝"
        kb.append([InlineKeyboardButton(f"{st} {t['nomi']}", callback_data=f"test_{t['id']}_0_0")])
    kb.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")])
    await q.edit_message_text("📝 *Testlar*\n\nTestni tanlang:",
                              parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def test_savol(update, ctx):
    q = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    tid, idx, togri = int(parts[1]), int(parts[2]), int(parts[3])
    t = next((x for x in TESTLAR if x["id"] == tid), None)
    if not t:
        return
    if idx >= len(t["savollar"]):
        ball = togri * 15
        db = load_db()
        u = get_user(db, q.from_user.id)
        if tid not in u["testlar"]:
            u["testlar"].append(tid)
            u["ball"] += ball
            save_db(db)
        pct = int(togri / len(t["savollar"]) * 100)
        baho = "🏆 Ajoyib!" if pct >= 90 else "✅ Yaxshi!" if pct >= 70 else "📚 Koproq mashq qiling"
        kb = [[InlineKeyboardButton("📝 Testlar", callback_data="testlar"),
               InlineKeyboardButton("🏠 Bosh", callback_data="bosh")]]
        await q.edit_message_text(
            f"📊 *Test tugadi!*\n\n{togri}/{len(t['savollar'])} togri\n{pct}%\n+{ball} ball\n\n{baho}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return
    sv = t["savollar"][idx]
    kb = [[InlineKeyboardButton(f"{'ABCD'[i]}) {v}",
                                callback_data=f"test_{tid}_{idx+1}_{togri+(1 if i==sv['j'] else 0)}")]
          for i, v in enumerate(sv["v"])]
    await q.edit_message_text(
        f"*{t['nomi']}*\nSavol {idx+1}/{len(t['savollar'])}\n\n*{sv['s']}*",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def bosqichlar_menu(update, ctx):
    q = update.callback_query
    await q.answer()
    db = load_db()
    u = get_user(db, q.from_user.id)
    txt = "🏆 *7 Bosqichli Yol*\n\n"
    for b in BOSQICHLAR:
        if u["ball"] >= b["max"]: st = "✅"
        elif u["ball"] >= b["min"]: st = "▶️"
        else: st = "🔒"
        txt += f"{st} {b['emoji']} *{b['nomi']}* — {b['min']}–{b['max']} ball\n"
    txt += f"\nSizning ballingiz: *{u['ball']}*"
    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def profil_menu(update, ctx):
    q = update.callback_query
    await q.answer()
    db = load_db()
    u = get_user(db, q.from_user.id)
    b = hozirgi_b(u["ball"])
    txt = (f"👤 *Profil*\n\n"
           f"{q.from_user.first_name}\n\n"
           f"Bosqich: *{b['emoji']} {b['nomi']}*\n"
           f"Ball: *{u['ball']}*\n"
           f"{pbar(u['ball'], b)}\n\n"
           f"Korilgan darslar: *{len(u['korilgan'])}*\n"
           f"Ishlangan testlar: *{len(u['testlar'])}*\n\n"
           f"Yutuqlar:\n"
           f"{'🏅' if u['korilgan'] else '⬜'} Birinchi dars\n"
           f"{'🏅' if u['testlar'] else '⬜'} Birinchi test\n"
           f"{'🏅' if u['ball']>=100 else '⬜'} 100 ball\n"
           f"{'🏅' if u['ball']>=500 else '⬜'} 500 ball\n"
           f"{'🏅' if u['ball']>=2100 else '⬜'} Barcha bosqich")
    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def reyting_menu(update, ctx):
    q = update.callback_query
    await q.answer()
    db = load_db()
    top = sorted(db.items(), key=lambda x: x[1].get("ball", 0), reverse=True)[:10]
    txt = "📊 *Top-10 Reyting*\n\n"
    for i, (uid, data) in enumerate(top):
        m = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
        oz = " siz" if uid == str(q.from_user.id) else ""
        txt += f"{m} {data.get('ball',0)} ball{oz}\n"
    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def bosh(update, ctx):
    q = update.callback_query
    await q.answer()
    await start(update, ctx)

async def cb(update, ctx):
    d = update.callback_query.data
    if d == "bosh": await bosh(update, ctx)
    elif d == "darslar": await darslar_menu(update, ctx)
    elif d == "testlar": await testlar_menu(update, ctx)
    elif d == "bosqichlar": await bosqichlar_menu(update, ctx)
    elif d == "profil": await profil_menu(update, ctx)
    elif d == "reyting": await reyting_menu(update, ctx)
    elif d.startswith("dtasdi_"): await dars_tasdi(update, ctx)
    elif d.startswith("dars_"): await dars_korish(update, ctx)
    elif d.startswith("test_"): await test_savol(update, ctx)

def main():
    app = Application.builder().token(TOKEN).updater(None).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
