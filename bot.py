import asyncio
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8679988126:AAEN69xq-5pzt1I7vfE2kPGtx-9CPa6sAmk"

# ── Ma'lumotlar bazasi (oddiy JSON fayl) ──────────────────
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
        db[uid] = {"ball": 0, "bosqich": 1, "ko'rilgan_darslar": [], "ishlangan_testlar": [], "streak": 0}
    return db[uid]

# ── Kontent (siz qo'shib borasiz) ────────────────────────
BOSQICHLAR = [
    {"id": 1, "nomi": "Kinematika",     "emoji": "🏃", "min_ball": 0,    "max_ball": 150},
    {"id": 2, "nomi": "Mexanika",       "emoji": "⚙️",  "min_ball": 150,  "max_ball": 350},
    {"id": 3, "nomi": "Termodinamika",  "emoji": "🌡️",  "min_ball": 350,  "max_ball": 600},
    {"id": 4, "nomi": "Elektr",         "emoji": "⚡",  "min_ball": 600,  "max_ball": 900},
    {"id": 5, "nomi": "Magnit",         "emoji": "🧲",  "min_ball": 900,  "max_ball": 1250},
    {"id": 6, "nomi": "Optika",         "emoji": "🔭",  "min_ball": 1250, "max_ball": 1650},
    {"id": 7, "nomi": "Kvant fizika",   "emoji": "⚛️",  "min_ball": 1650, "max_ball": 2100},
]

DARSLAR = [
    {"id": 1,  "bosqich": 1, "nomi": "Tezlik va tezlanish",        "video": "https://youtube.com/watch?v=EXAMPLE1", "ball": 30, "vaqt": "8 daq"},
    {"id": 2,  "bosqich": 1, "nomi": "Erkin tushish jismlar",      "video": "https://youtube.com/watch?v=EXAMPLE2", "ball": 30, "vaqt": "10 daq"},
    {"id": 3,  "bosqich": 1, "nomi": "Nishab bo'ylab harakat",     "video": "https://youtube.com/watch?v=EXAMPLE3", "ball": 30, "vaqt": "12 daq"},
    {"id": 4,  "bosqich": 2, "nomi": "1-Newton qonuni",            "video": "https://youtube.com/watch?v=EXAMPLE4", "ball": 30, "vaqt": "10 daq"},
    {"id": 5,  "bosqich": 2, "nomi": "2-Newton qonuni: F=ma",      "video": "https://youtube.com/watch?v=EXAMPLE5", "ball": 30, "vaqt": "12 daq"},
    {"id": 6,  "bosqich": 2, "nomi": "3-Newton qonuni",            "video": "https://youtube.com/watch?v=EXAMPLE6", "ball": 30, "vaqt": "9 daq"},
    {"id": 7,  "bosqich": 3, "nomi": "Issiqlik miqdori",           "video": "https://youtube.com/watch?v=EXAMPLE7", "ball": 30, "vaqt": "11 daq"},
    {"id": 8,  "bosqich": 3, "nomi": "Ideal gaz qonunlari",        "video": "https://youtube.com/watch?v=EXAMPLE8", "ball": 30, "vaqt": "14 daq"},
    {"id": 9,  "bosqich": 4, "nomi": "Elektr zaryadi",             "video": "https://youtube.com/watch?v=EXAMPLE9", "ball": 30, "vaqt": "10 daq"},
    {"id": 10, "bosqich": 4, "nomi": "Tok kuchi va kuchlanish",    "video": "https://youtube.com/watch?v=EXAMPLE10","ball": 30, "vaqt": "13 daq"},
]

TESTLAR = [
    {
        "id": 1, "bosqich": 1, "nomi": "Kinematika — Test",
        "savollar": [
            {"savol": "Tezlanish formulasi qaysi?",
             "variantlar": ["a = v/t", "a = F/m", "a = mv", "a = s/t"],
             "javob": 0},
            {"savol": "Erkin tushish tezlanishi taxminan nechaga teng?",
             "variantlar": ["5 m/s²", "9.8 m/s²", "15 m/s²", "1 m/s²"],
             "javob": 1},
            {"savol": "Yo'l formulasi: s = ?",
             "variantlar": ["s = v·t", "s = a·t", "s = v/t", "s = F·t"],
             "javob": 0},
        ]
    },
    {
        "id": 2, "bosqich": 2, "nomi": "Mexanika — Test",
        "savollar": [
            {"savol": "F = ma formulasida 'm' neni bildiradi?",
             "variantlar": ["Tezlanish", "Massa", "Kuch", "Vaqt"],
             "javob": 1},
            {"savol": "1-Newton qonuniga ko'ra jism...",
             "variantlar": ["Doim harakatda", "Tashqi kuch bo'lmasa tinch yoki tekis harakat qiladi",
                            "Doim tezlashadi", "Doim sekinlashadi"],
             "javob": 1},
            {"savol": "Impuls formulasi p = ?",
             "variantlar": ["p = m·v", "p = F·t²", "p = m·a", "p = E/v"],
             "javob": 0},
        ]
    },
    {
        "id": 3, "bosqich": 3, "nomi": "Termodinamika — Test",
        "savollar": [
            {"savol": "Ideal gaz qonuni: pV = ?",
             "variantlar": ["nRT", "mT", "FV", "aT"],
             "javob": 0},
            {"savol": "Harorat o'lchov birligi SI da?",
             "variantlar": ["Celsius", "Fahrenheit", "Kelvin", "Rankine"],
             "javob": 2},
            {"savol": "Issiqlik miqdori formulasi Q = ?",
             "variantlar": ["Q = mcΔT", "Q = mv²/2", "Q = mgh", "Q = FΔs"],
             "javob": 0},
        ]
    },
]

# ── Yordamchi funksiyalar ─────────────────────────────────
def hozirgi_bosqich(ball):
    for b in reversed(BOSQICHLAR):
        if ball >= b["min_ball"]:
            return b
    return BOSQICHLAR[0]

def progress_bar(ball, bosqich):
    mn = bosqich["min_ball"]
    mx = bosqich["max_ball"]
    pct = min(100, int((ball - mn) / (mx - mn) * 100)) if mx > mn else 100
    filled = pct // 10
    bar = "🟦" * filled + "⬜" * (10 - filled)
    return f"{bar} {pct}%"

# ── Asosiy menyu ──────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user = get_user(db, update.effective_user.id)
    save_db(db)
    bosqich = hozirgi_bosqich(user["ball"])

    kb = [
        [InlineKeyboardButton("📚 Darslar",     callback_data="darslar"),
         InlineKeyboardButton("📝 Testlar",     callback_data="testlar")],
        [InlineKeyboardButton("🏆 Bosqichlar",  callback_data="bosqichlar"),
         InlineKeyboardButton("👤 Profil",      callback_data="profil")],
        [InlineKeyboardButton("📊 Reyting",     callback_data="reyting")],
    ]

    text = (
        f"⚛️ *Fizika Kursi*\n\n"
        f"Salom, *{update.effective_user.first_name}*! 👋\n\n"
        f"🎯 Hozirgi bosqich: *{bosqich['emoji']} {bosqich['nomi']}*\n"
        f"💎 Ballingiz: *{user['ball']}*\n"
        f"{progress_bar(user['ball'], bosqich)}\n\n"
        f"📖 Ko'rilgan darslar: *{len(user['ko'rilgan_darslar'])}*\n"
        f"✅ Ishlangan testlar: *{len(user['ishlangan_testlar'])}*\n\n"
        f"Nima qilmoqchisiz?"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown",
                                              reply_markup=InlineKeyboardMarkup(kb))

# ── Darslar ───────────────────────────────────────────────
async def darslar_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load_db()
    user = get_user(db, query.from_user.id)
    bosqich = hozirgi_bosqich(user["ball"])

    text = f"📚 *Darslar — {bosqich['emoji']} {bosqich['nomi']}*\n\n"
    kb = []

    darslar = [d for d in DARSLAR if d["bosqich"] == bosqich["id"]]
    if not darslar:
        text += "Bu bosqich uchun darslar tez orada qo'shiladi!"
    else:
        for d in darslar:
            done = d["id"] in user["ko'rilgan_darslar"]
            status = "✅" if done else "▶️"
            ball_txt = "bajarildi" if done else f"+{d['ball']} ball"
            kb.append([InlineKeyboardButton(
                f"{status} {d['nomi']} ({ball_txt})",
                callback_data=f"dars_{d['id']}"
            )])

    kb.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

async def dars_ko_rish(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dars_id = int(query.data.split("_")[1])
    dars = next((d for d in DARSLAR if d["id"] == dars_id), None)
    if not dars:
        return

    db = load_db()
    user = get_user(db, query.from_user.id)

    if dars_id in user["ko'rilgan_darslar"]:
        kb = [[InlineKeyboardButton("📚 Darslarga qaytish", callback_data="darslar")]]
        await query.edit_message_text(
            f"✅ *{dars['nomi']}*\n\nBu darsni allaqachon ko'rgansiz!",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return

    text = (
        f"▶️ *{dars['nomi']}*\n\n"
        f"⏱ Davomiyligi: {dars['vaqt']}\n"
        f"💎 Ball: +{dars['ball']}\n\n"
        f"🔗 Video: {dars['video']}\n\n"
        f"Videoni ko'rib chiqdingizmi?"
    )
    kb = [
        [InlineKeyboardButton("✅ Ha, ko'rdim! (+ball)", callback_data=f"dars_tasdiqlash_{dars_id}")],
        [InlineKeyboardButton("📚 Darslarga qaytish", callback_data="darslar")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

async def dars_tasdiqlash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dars_id = int(query.data.split("_")[2])
    dars = next((d for d in DARSLAR if d["id"] == dars_id), None)
    if not dars:
        return

    db = load_db()
    user = get_user(db, query.from_user.id)

    if dars_id not in user["ko'rilgan_darslar"]:
        user["ko'rilgan_darslar"].append(dars_id)
        user["ball"] += dars["ball"]
        save_db(db)

    bosqich_eski = hozirgi_bosqich(user["ball"] - dars["ball"])
    bosqich_yangi = hozirgi_bosqich(user["ball"])
    bosqich_msg = ""
    if bosqich_yangi["id"] > bosqich_eski["id"]:
        bosqich_msg = (f"\n\n🎉 *Tabriklaymiz! Yangi bosqich:*\n"
                       f"*{bosqich_yangi['emoji']} {bosqich_yangi['nomi']}*")

    text = (
        f"✅ *Barakalla!*\n\n"
        f"📖 {dars['nomi']}\n"
        f"💎 +{dars['ball']} ball qo'shildi!\n"
        f"🏆 Jami ball: *{user['ball']}*"
        f"{bosqich_msg}"
    )
    kb = [
        [InlineKeyboardButton("📚 Darslar", callback_data="darslar"),
         InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

# ── Testlar ───────────────────────────────────────────────
async def testlar_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load_db()
    user = get_user(db, query.from_user.id)
    bosqich = hozirgi_bosqich(user["ball"])

    text = f"📝 *Testlar — {bosqich['emoji']} {bosqich['nomi']}*\n\n"
    kb = []

    testlar = [t for t in TESTLAR if t["bosqich"] <= bosqich["id"]]
    for t in testlar:
        done = t["id"] in user["ishlangan_testlar"]
        status = "✅" if done else "📝"
        kb.append([InlineKeyboardButton(
            f"{status} {t['nomi']}",
            callback_data=f"test_{t['id']}_0"
        )])

    kb.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

async def test_savol(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    test_id = int(parts[1])
    savol_idx = int(parts[2])
    togri = int(parts[3]) if len(parts) > 3 else 0

    test = next((t for t in TESTLAR if t["id"] == test_id), None)
    if not test:
        return

    if savol_idx >= len(test["savollar"]):
        # Test tugadi
        ball_qo_shildi = togri * 15
        db = load_db()
        user = get_user(db, query.from_user.id)
        if test_id not in user["ishlangan_testlar"]:
            user["ishlangan_testlar"].append(test_id)
            user["ball"] += ball_qo_shildi
            save_db(db)

        pct = int(togri / len(test["savollar"]) * 100)
        baho = "🏆 Ajoyib!" if pct >= 90 else "✅ Yaxshi!" if pct >= 70 else "📚 Ko'proq mashq qiling"
        text = (
            f"📊 *Test yakunlandi!*\n\n"
            f"✅ To'g'ri javoblar: {togri}/{len(test['savollar'])}\n"
            f"📈 Natija: {pct}%\n"
            f"💎 +{ball_qo_shildi} ball\n\n"
            f"{baho}"
        )
        kb = [
            [InlineKeyboardButton("📝 Testlarga qaytish", callback_data="testlar"),
             InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")],
        ]
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(kb))
        return

    savol = test["savollar"][savol_idx]
    text = (
        f"📝 *{test['nomi']}*\n"
        f"❓ Savol {savol_idx + 1}/{len(test['savollar'])}\n\n"
        f"*{savol['savol']}*"
    )
    kb = []
    harflar = ["A", "B", "C", "D"]
    for i, variant in enumerate(savol["variantlar"]):
        javob_togri = 1 if i == savol["javob"] else 0
        yangi_togri = togri + javob_togri
        kb.append([InlineKeyboardButton(
            f"{harflar[i]}) {variant}",
            callback_data=f"test_{test_id}_{savol_idx + 1}_{yangi_togri}"
        )])

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

# ── Bosqichlar ────────────────────────────────────────────
async def bosqichlar_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load_db()
    user = get_user(db, query.from_user.id)

    text = "🏆 *7 Bosqichli Yo'l*\n\n"
    for b in BOSQICHLAR:
        if user["ball"] >= b["max_ball"]:
            status = "✅"
        elif user["ball"] >= b["min_ball"]:
            status = "▶️"
        else:
            status = "🔒"
        text += f"{status} {b['emoji']} *{b['nomi']}* — {b['min_ball']}–{b['max_ball']} ball\n"

    text += f"\n💎 Sizning ballingiz: *{user['ball']}*"
    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

# ── Profil ────────────────────────────────────────────────
async def profil_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load_db()
    user = get_user(db, query.from_user.id)
    bosqich = hozirgi_bosqich(user["ball"])

    text = (
        f"👤 *Profil*\n\n"
        f"👋 {query.from_user.first_name}\n\n"
        f"🎯 Bosqich: *{bosqich['emoji']} {bosqich['nomi']}*\n"
        f"💎 Ball: *{user['ball']}*\n"
        f"{progress_bar(user['ball'], bosqich)}\n\n"
        f"📖 Ko'rilgan darslar: *{len(user['ko'rilgan_darslar'])}*\n"
        f"✅ Ishlangan testlar: *{len(user['ishlangan_testlar'])}*\n\n"
        f"🔥 Streak: *{user['streak']} kun*\n\n"
        f"📊 *Yutuqlar:*\n"
        f"{'🏅 Birinchi dars' if user['ko'rilgan_darslar'] else '⬜ Birinchi darsni ko'ring'}\n"
        f"{'🏅 Birinchi test' if user['ishlangan_testlar'] else '⬜ Birinchi testni ishlang'}\n"
        f"{'🏅 100 ball' if user['ball'] >= 100 else '⬜ 100 ball to'plang'}\n"
        f"{'🏅 500 ball' if user['ball'] >= 500 else '⬜ 500 ball to'plang'}\n"
        f"{'🏅 Barcha bosqich' if user['ball'] >= 2100 else '⬜ Barcha bosqichni o'ting'}\n"
    )
    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

# ── Reyting ───────────────────────────────────────────────
async def reyting_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load_db()

    foydalanuvchilar = []
    for uid, data in db.items():
        foydalanuvchilar.append((uid, data.get("ball", 0)))

    foydalanuvchilar.sort(key=lambda x: x[1], reverse=True)
    top = foydalanuvchilar[:10]

    text = "📊 *Top-10 Reyting*\n\n"
    medalllar = ["🥇", "🥈", "🥉"]
    for i, (uid, ball) in enumerate(top):
        medal = medalllar[i] if i < 3 else f"{i+1}."
        o_z = " ← siz" if uid == str(query.from_user.id) else ""
        text += f"{medal} {ball} ball{o_z}\n"

    my_idx = next((i for i, (uid, _) in enumerate(foydalanuvchilar)
                   if uid == str(query.from_user.id)), -1)
    if my_idx >= 10:
        text += f"\n...\n{my_idx+1}. {db[str(query.from_user.id)]['ball']} ball ← siz"

    kb = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb))

# ── Bosh menyu tugmasi ────────────────────────────────────
async def bosh_menyu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, ctx)

# ── Callback router ───────────────────────────────────────
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "bosh":           await bosh_menyu(update, ctx)
    elif data == "darslar":      await darslar_menu(update, ctx)
    elif data == "testlar":      await testlar_menu(update, ctx)
    elif data == "bosqichlar":   await bosqichlar_menu(update, ctx)
    elif data == "profil":       await profil_menu(update, ctx)
    elif data == "reyting":      await reyting_menu(update, ctx)
    elif data.startswith("dars_tasdiqlash_"): await dars_tasdiqlash(update, ctx)
    elif data.startswith("dars_"):            await dars_ko_rish(update, ctx)
    elif data.startswith("test_"):            await test_savol(update, ctx)

# ── Ishga tushirish ───────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
