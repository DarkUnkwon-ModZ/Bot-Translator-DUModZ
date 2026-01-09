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
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
DEV_NAME = "𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

DetectorFactory.seed = 0
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE MANAGEMENT ---
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "banned": []}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "banned": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- UTILS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- UI KEYBOARDS ---
def get_main_keyboard(uid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⚙️ AI Settings", callback_data="open_settings"),
        types.InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
    )
    markup.add(types.InlineKeyboardButton("📜 Usage Guide", callback_data="user_guide"))
    markup.add(types.InlineKeyboardButton("✨ Developer", url=DEV_URL))
    return markup

def get_settings_keyboard():
    langs = [("English 🇺🇸", "en"), ("Bengali 🇧🇩", "bn"), ("Hindi 🇮🇳", "hi"), 
             ("Arabic 🇸🇦", "ar"), ("Spanish 🇪🇸", "es"), ("French 🇫🇷", "fr")]
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"lang_{code}") for name, code in langs]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home"))
    return markup

# --- CORE HANDLERS ---

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    first_name = message.from_user.first_name
    
    if uid not in db["users"]:
        db["users"][uid] = {"name": first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        save_db(db)

    if int(uid) in db["banned"]:
        return bot.reply_to(message, "🚫 Access Revoked!")

    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub"))
        return bot.send_photo(message.chat.id, BANNER_URL, caption=f"👋 Welcome {first_name}!\nPlease join our channel to use the bot.", reply_markup=markup)

    current_lang = db["users"][uid].get("lang", "en").upper()
    welcome_text = (
        f"🚀 <b>{DEV_NAME} AI Translator</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Status:</b> ✅ Verified\n"
        f"<b>Target:</b> <code>{current_lang}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Send any text to translate or use quick commands like <code>/bn</code> or <code>/hi</code>."
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=welcome_text, reply_markup=get_main_keyboard(uid))

# --- QUICK COMMANDS (/en, /bn etc) ---
@bot.message_handler(commands=['en', 'bn', 'hi', 'ar', 'es', 'fr'])
def quick_translate(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id): return
    
    target = message.text.split()[0][1:].lower()
    text_to_translate = message.text.replace(f"/{target}", "").strip()
    
    if not text_to_translate:
        return bot.reply_to(message, f"❌ Please provide text. Example: <code>/{target} Hello</code>")
    
    process_translation(message, text_to_translate, target)

# --- AUTOMATIC TRANSLATION ---
@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return
    
    target = db["users"].get(uid, {}).get("lang", "en")
    process_translation(message, message.text, target)

def process_translation(message, text, target_lang):
    uid = str(message.from_user.id)
    status_msg = bot.reply_to(message, "🌀 <b>AI Is Analyzing...</b>")
    
    # Threaded animation to prevent blocking
    stop_event = threading.Event()
    def animate():
        frames = ["⚡ Processing...", "📡 Finalizing..."]
        idx = 0
        while not stop_event.is_set():
            try:
                bot.edit_message_text(f"⏳ {frames[idx % len(frames)]}", message.chat.id, status_msg.message_id)
                idx += 1
                time.sleep(0.8)
            except: break

    anim_thread = threading.Thread(target=animate)
    anim_thread.start()

    try:
        # Language Detection
        try:
            detected = detect(text).upper()
        except:
            detected = "AUTO"

        # Translation Logic
        if detected.lower() == target_lang.lower():
            result = text
        else:
            result = GoogleTranslator(source='auto', target=target_lang).translate(text)

        stop_event.set() # Stop animation
        time.sleep(0.5)

        db["users"][uid]["count"] = db["users"][uid].get("count", 0) + 1
        save_db(db)

        response = (
            f"✅ <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target_lang.upper()}):</b>\n<code>{result}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)

    except Exception as e:
        stop_event.set()
        bot.edit_message_text("❌ <b>Error:</b> Translation failed. Try again.", message.chat.id, status_msg.message_id)

# --- CALLBACK ROUTER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Success!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)

    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>Select Output Language:</b>", call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = new_lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Target set to {new_lang.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

    elif call.data == "my_profile":
        u = db["users"][uid]
        profile = (f"👤 <b>Profile</b>\n━━━━━━━━━━\nID: <code>{uid}</code>\nTarget: {u['lang'].upper()}\nTotal: {u['count']}")
        bot.edit_message_caption(profile, call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

# --- ADMIN PANEL ---
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    msg = "📊 <b>User List:</b>\n"
    for uid, data in list(db["users"].items())[-10:]:
        msg += f"• {data['name']} (<code>{uid}</code>) - {data['lang']}\n"
    bot.reply_to(message, f"{msg}\nTotal Users: {len(db['users'])}")

# --- START BOT ---
if __name__ == "__main__":
    print(f"--- {DEV_NAME} SYSTEM RUNNING ---")
    bot.infinity_polling()
