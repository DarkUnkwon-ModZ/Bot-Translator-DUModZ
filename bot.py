import telebot
import time
import datetime
import threading
import json
import os
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/heads/main/Img/darkunkwonmodz-banner.jpg"
DEV_NAME = "𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

DetectorFactory.seed = 0
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE ---
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "banned": []}
    with open(DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {"users": {}, "banned": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- SUPPORTED LANGUAGES ---
LANG_MAP = {
    'en': 'English 🇺🇸', 'bn': 'Bengali 🇧🇩', 'hi': 'Hindi 🇮🇳',
    'ar': 'Arabic 🇸🇦', 'es': 'Spanish 🇪🇸', 'fr': 'French 🇫🇷',
    'de': 'German 🇩🇪', 'ja': 'Japanese 🇯🇵', 'ru': 'Russian 🇷🇺', 'pt': 'Portuguese 🇵🇹'
}

# --- UTILS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- KEYBOARDS ---
def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⚙️ AI Settings", callback_data="open_settings"),
        types.InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
    )
    markup.add(types.InlineKeyboardButton("📜 User Guide", callback_data="user_guide"))
    markup.add(types.InlineKeyboardButton("✨ Developer", url=DEV_URL))
    return markup

def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"lang_{code}") for code, name in LANG_MAP.items()]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home"))
    return markup

# --- CORE TRANSLATION FUNCTION ---
def perform_translation(message, text, target_lang, is_cmd=False):
    uid = str(message.from_user.id)
    status_msg = bot.reply_to(message, "⏳ 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 𝗔𝗜...")
    
    try:
        # Language Detection
        try: src_lang = detect(text).upper()
        except: src_lang = "AUTO"

        # Translation
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)

        # Bug Fix: If input and output are same or translation fails
        if not result or result.strip() == text.strip() and target_lang != 'en':
             result = translator.translate(text) # Retry once

        db["users"][uid]["count"] = db["users"][uid].get("count", 0) + 1
        save_db(db)

        response = (
            f"✅ <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({src_lang}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target_lang.upper()}):</b>\n<code>{result}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    except Exception:
        bot.edit_message_text("❌ <b>AI Error:</b> Unable to translate. Try again.", message.chat.id, status_msg.message_id)

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    if int(uid) in db["banned"]: return
    
    if uid not in db["users"]:
        db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        save_db(db)

    sub = is_subscribed(message.from_user.id)
    sub_status = "✅ Verified Member" if sub else "❌ Not Subscribed"
    
    if not sub:
        markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}")],
                                           [types.InlineKeyboardButton("🔄 Verify", callback_data="verify_sub")]])
        return bot.send_photo(message.chat.id, BANNER_URL, caption=f"👋 <b>Welcome!</b>\n🛡 Status: {sub_status}\n\nPlease join our channel to use the bot.", reply_markup=markup)

    curr_lang = db["users"][uid].get("lang", "en").upper()
    welcome_text = (
        f"🚀 <b>{DEV_NAME} Translator v8.0</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {message.from_user.first_name}\n"
        f"🛡 <b>Status:</b> {sub_status}\n"
        f"🎯 <b>Default Mode:</b> Auto → <code>{curr_lang}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Send any text to translate to <b>{curr_lang}</b>. Or use commands like <code>/bn [text]</code> to translate to specific languages."
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=welcome_text, reply_markup=get_main_keyboard())

# --- LANGUAGE SHORT COMMANDS (/en, /bn, /hi etc.) ---
@bot.message_handler(commands=['en', 'bn', 'hi', 'ar', 'es', 'fr', 'de', 'ja', 'ru', 'pt'])
def language_shortcuts(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return

    cmd = message.text.split()[0][1:].lower() # Get 'en', 'bn' etc.
    args = message.text.replace(f'/{cmd}', '').strip()

    if not args:
        # Just update default language
        db["users"][uid]["lang"] = cmd
        save_db(db)
        bot.reply_to(message, f"✅ Your default target language has been set to <b>{LANG_MAP[cmd]}</b>")
    else:
        # Translate the provided text directly
        perform_translation(message, args, cmd, is_cmd=True)

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['stats', 'admin', 'broadcast', 'ban', 'unban'])
def admin_area(message):
    if message.from_user.id != ADMIN_ID: return
    cmd = message.text.split()[0][1:]

    if cmd == 'stats':
        total = len(db["users"])
        stats = f"📊 <b>Bot Statistics</b>\nTotal Users: {total}\n\n<b>Recent Users:</b>\n"
        for uid, data in list(db["users"].items())[-10:]:
            stats += f"• {data['name']} (<code>{uid}</code>) -> {data['lang'].upper()}\n"
        bot.reply_to(message, stats)
    
    elif cmd == 'broadcast':
        txt = message.text.replace('/broadcast', '').strip()
        if not txt: return bot.reply_to(message, "❌ Message missing.")
        for u in db["users"]:
            try: bot.send_message(u, f"📣 <b>Announcement</b>\n\n{txt}")
            except: pass
        bot.reply_to(message, "✅ Sent to all.")

# --- CALLBACKS & TEXT HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    if call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>Select AI Target Language:</b>", call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())
    elif call.data.startswith("lang_"):
        db["users"][uid]["lang"] = call.data.split("_")[1]
        save_db(db); bot.delete_message(call.message.chat.id, call.message.message_id); start_command(call.message)
    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id); start_command(call.message)

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return
    target = db["users"].get(uid, {}).get("lang", "en")
    perform_translation(message, message.text, target)

if __name__ == "__main__":
    print("--- BOT STARTED SUCCESSFULLY ---")
    bot.infinity_polling()
