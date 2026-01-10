import telebot
import time
import datetime
import json
import os
import sys
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# --- CONFIGURATION (Safe & Secure) ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
DEV_NAME = "𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"

DetectorFactory.seed = 0
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE SYSTEM ---
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "banned": []}
    with open(DB_FILE, 'r') as f:
        try:
            data = json.load(f)
            if "users" not in data: data["users"] = {}
            if "banned" not in data: data["banned"] = []
            return data
        except:
            return {"users": {}, "banned": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- EXTENDED LANGUAGES ---
LANG_MAP = {
    'bn': 'Bengali 🇧🇩', 'en': 'English 🇺🇸', 'hi': 'Hindi 🇮🇳', 'ar': 'Arabic 🇸🇦',
    'es': 'Spanish 🇪🇸', 'fr': 'French 🇫🇷', 'de': 'German 🇩🇪', 'ja': 'Japanese 🇯🇵',
    'ru': 'Russian 🇷🇺', 'pt': 'Portuguese 🇵🇹', 'tr': 'Turkish 🇹🇷', 'it': 'Italian 🇮🇹',
    'ko': 'Korean 🇰🇷', 'zh-CN': 'Chinese 🇨🇳'
}

# --- UTILS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

# --- KEYBOARDS ---
def get_main_keyboard(subbed=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if not subbed:
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=DEV_URL))
        markup.add(types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub"))
    else:
        markup.add(
            types.InlineKeyboardButton("⚙️ AI Settings", callback_data="open_settings"),
            types.InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
        )
        markup.add(types.InlineKeyboardButton("📜 User Guide", callback_data="user_guide"))
        markup.add(types.InlineKeyboardButton("🌐 Visit Blog", url=BLOG_URL))
    return markup

def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"lang_{code}") for code, name in LANG_MAP.items()]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home"))
    return markup

# --- LOGGING ---
def log_status(action):
    try:
        bot_info = bot.get_me()
        log_msg = (
            f"🚀 <b>Bot Engine Status</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot:</b> {bot_info.first_name}\n"
            f"🏷 <b>User:</b> @{bot_info.username}\n"
            f"⚡ <b>Event:</b> {action}\n"
            f"⏰ <b>Time:</b> {get_timestamp()}\n"
            f"🟢 <b>System:</b> Online 24/7\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(LOG_CHANNEL, log_msg)
    except: pass

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if int(uid) in db.get("banned", []):
        return bot.reply_to(message, "🚫 You are banned from using this bot.")

    bot.send_chat_action(message.chat.id, 'typing')
    
    if uid not in db["users"]:
        db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        save_db(db)

    sub = is_subscribed(message.from_user.id)
    status_text = "✅ Verified Member" if sub else "❌ Not Joined"
    
    caption = (
        f"🚀 <b>{DEV_NAME} Translator v9.0</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {message.from_user.first_name}\n"
        f"🛡 <b>Security:</b> {status_text}\n"
        f"🎯 <b>Mode:</b> Auto → <code>{db['users'][uid].get('lang', 'en').upper()}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Send any text and watch the AI work its magic!"
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=caption, reply_markup=get_main_keyboard(sub))

# --- LANGUAGE SHORTCUTS ---
@bot.message_handler(commands=list(LANG_MAP.keys()))
def fast_lang_set(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id): return
    
    new_lang = message.text.split()[0][1:].lower()
    args = message.text.replace(f"/{new_lang}", "").strip()
    
    if not args:
        db["users"][uid]["lang"] = new_lang
        save_db(db)
        bot.reply_to(message, f"🎯 Default language set to <b>{LANG_MAP[new_lang]}</b>")
    else:
        perform_translation(message, args, new_lang)

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = str(call.from_user.id)
    mid = call.message.message_id
    cid = call.message.chat.id

    if call.data == "verify_sub":
        bot.edit_message_caption("🔄 <b>Checking API connection...</b>", cid, mid)
        time.sleep(1)
        bot.edit_message_caption("🛡 <b>Verifying Channel Membership...</b>", cid, mid)
        time.sleep(1)
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Access Granted!", show_alert=True)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Verification Failed! Join first.", show_alert=True)
            start(call.message)

    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>Select AI Target Language:</b>", cid, mid, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Target set to {LANG_MAP[lang]}")
        start(call.message)

    elif call.data == "my_profile":
        u = db["users"].get(uid, {})
        profile = (
            f"👤 <b>Your Premium Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Target Lang:</b> {LANG_MAP.get(u.get('lang','en'))}\n"
            f"📊 <b>Total Processed:</b> {u.get('count', 0)}\n"
            f"📅 <b>Joined On:</b> {u.get('date', 'N/A')}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_caption(profile, cid, mid, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        start(call.message)

    elif call.data == "user_guide":
        guide = (
            "📜 <b>DUModZ Translator Guide</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• <b>Auto Translate:</b> Just send text.\n"
            "• <b>Fast Mode:</b> Use /bn [text] for instant Bengali.\n"
            "• <b>Settings:</b> Change default language via ⚙️ button.\n"
            "• <b>Status:</b> Check your usage in Profile.\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_caption(guide, cid, mid, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

# --- TRANSLATION CORE ---
def perform_translation(message, text, target):
    uid = str(message.from_user.id)
    bot.send_chat_action(message.chat.id, 'typing')
    wait = bot.reply_to(message, "📡 <b>Connecting to AI Server...</b>")
    
    try:
        time.sleep(0.5)
        bot.edit_message_text("⚡ <b>AI Processing...</b>", wait.chat.id, wait.message_id)
        
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        try: src = detect(text).upper()
        except: src = "AUTO"

        db["users"][uid]["count"] += 1
        save_db(db)

        res = (
            f"✅ <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({src}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        bot.edit_message_text(res, wait.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text("❌ <b>AI Error:</b> Translation failed.", wait.chat.id, wait.message_id)

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_msg(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id): return start(message)
    target = db["users"].get(uid, {}).get("lang", "en")
    perform_translation(message, message.text, target)

# --- ADVANCED ADMIN COMMANDS ---
@bot.message_handler(commands=['admin', 'stats', 'broadcast', 'ban', 'unban', 'backup'])
def admin_cmds(message):
    if message.from_user.id != ADMIN_ID: return
    
    cmd = message.text.split()[0][1:]
    
    if cmd == 'admin':
        bot.reply_to(message, "👑 <b>Owner Command Center</b>\n\n"
                              "📊 /stats - Bot Statistics\n"
                              "📢 /broadcast - Message to Users\n"
                              "🚫 /ban [ID] - Block User\n"
                              "✅ /unban [ID] - Unblock User\n"
                              "💾 /backup - Get Database File")

    elif cmd == 'stats':
        total = len(db["users"])
        banned = len(db.get("banned", []))
        bot.reply_to(message, f"📊 <b>Stats:</b>\nUsers: {total}\nBanned: {banned}")

    elif cmd == 'broadcast':
        msg = message.text.replace('/broadcast', '').strip()
        if not msg: return bot.reply_to(message, "Usage: /broadcast [msg]")
        count = 0
        for user in list(db["users"].keys()):
            try:
                bot.send_message(user, f"📣 <b>Broadcast Update</b>\n\n{msg}\n\n✨ @{bot.get_me().username}")
                count += 1
                time.sleep(0.05)
            except: pass
        bot.reply_to(message, f"✅ Sent to {count} users.")

    elif cmd == 'ban':
        try:
            target_id = int(message.text.split()[1])
            if target_id not in db["banned"]:
                db["banned"].append(target_id)
                save_db(db)
                bot.reply_to(message, f"🚫 User {target_id} Banned.")
        except: bot.reply_to(message, "Provide valid ID.")

    elif cmd == 'unban':
        try:
            target_id = int(message.text.split()[1])
            if target_id in db["banned"]:
                db["banned"].remove(target_id)
                save_db(db)
                bot.reply_to(message, f"✅ User {target_id} Unbanned.")
        except: bot.reply_to(message, "Provide valid ID.")

    elif cmd == 'backup':
        with open(DB_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="💾 Database Backup")

# --- AUTO RESTART LOGIC ---
if __name__ == "__main__":
    log_status("Bot Restarted & 24/7 Mode Active")
    print("--- DUModZ BOT STARTED ---")
    bot.infinity_polling()
