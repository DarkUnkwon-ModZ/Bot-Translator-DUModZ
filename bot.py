import telebot
import time
import datetime
import threading
import json
import os
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Accuracy Stability
DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
DEV_NAME = "𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE SYSTEM ---
USER_DB = "users.json"

def load_data():
    if os.path.exists(USER_DB):
        with open(USER_DB, 'r') as f: return json.load(f)
    return {"users": {}, "banned": []}

def save_data(data):
    with open(USER_DB, 'w') as f: json.dump(data, f, indent=4)

db = load_data()

# --- HELPERS ---
def is_joined(user_id):
    if user_id == ADMIN_ID: return True
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- PREMIUM ANIMATIONS ---
def premium_animation(chat_id, message_id, frames):
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id, disable_web_page_preview=True)
            time.sleep(0.6)
        except: break

# --- KEYBOARDS ---
def welcome_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(f"✨ {DEV_NAME}", url=DEV_URL))
    markup.add(types.InlineKeyboardButton("🌐 Official Website", url=BLOG_URL))
    markup.add(types.InlineKeyboardButton("⚙️ AI Settings", callback_data="settings"),
               types.InlineKeyboardButton("📜 User Guide", callback_data="help"))
    return markup

# --- START HANDLER ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "N/A"

    # Save User Info
    if uid not in db["users"]:
        db["users"][uid] = {"name": first_name, "user": username, "lang": "en"}
        save_data(db)

    if int(uid) in db["banned"]:
        bot.reply_to(message, "🚫 <b>Access Revoked!</b>\nYou are blacklisted by the Administrator.")
        return

    if not is_joined(message.from_user.id):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📢 Join Official Channel", url=DEV_URL))
        m.add(types.InlineKeyboardButton("✅ Verify & Access", callback_data="verify_join"))
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"🛡️ <b>Security Verification</b>\n\nHello {first_name}!\nTo maintain our server quality, you must join our channel first.", 
                       reply_markup=m)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>{DEV_NAME} Translator v3.0</b>\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"Welcome to the most advanced AI Translator.\n\n"
                           f"👤 <b>User:</b> {first_name}\n"
                           f"🆔 <b>ID:</b> <code>{uid}</code>\n"
                           f"🎯 <b>Default Mode:</b> Auto → {db['users'][uid]['lang'].upper()}\n"
                           f"━━━━━━━━━━━━━━━━━━━━", reply_markup=welcome_markup())

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = str(call.from_user.id)
    
    if call.data == "verify_join":
        if is_joined(call.from_user.id):
            msg = bot.edit_message_caption("🔄 <b>Verifying Access...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ <b>Access Granted!</b>", call.message.chat.id, call.message.message_id)
            time.sleep(0.5)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please Join First!", show_alert=True)

    elif call.data == "settings":
        langs = [("Bengali", "bn"), ("English", "en"), ("Hindi", "hi"), ("Arabic", "ar"), ("Spanish", "es")]
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(*[types.InlineKeyboardButton(n, callback_data=f"set_{c}") for n, c in langs])
        m.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption("⚙️ <b>AI Translation Settings</b>\nChoose your target language:", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data.startswith("set_"):
        lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = lang
        save_data(db)
        bot.answer_callback_query(call.id, f"✅ Language set to {lang.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION LOGIC ---
@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_joined(message.from_user.id) or int(uid) in db["banned"]: return

    target = db["users"].get(uid, {}).get("lang", "en")
    status = bot.reply_to(message, "🌌")
    
    frames = [
        "💎 <b>Analyzing Linguistic Data...</b>",
        "🧠 <b>Neural AI Processing...</b>",
        "⚡ <b>Translating Context...</b>",
        "✅ <b>Finalizing Output...</b>"
    ]
    
    threading.Thread(target=premium_animation, args=(message.chat.id, status.message_id, frames)).start()
    
    try:
        time.sleep(2.5)
        text = message.text
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        detected = detect(text).upper()
        
        result = (
            f"🌐 <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        bot.edit_message_text(result, message.chat.id, status.message_id)
    except:
        bot.edit_message_text("❌ <b>Translation Error!</b> Try again later.", message.chat.id, status_msg.message_id)

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin', 'adminhelp'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, f"👑 <b>Admin Dashboard</b>\n\n"
                          f"📊 /stats - Detailed User List\n"
                          f"📣 /broadcast [msg] - Send Global Msg\n"
                          f"🚫 /ban [id] - Ban User\n"
                          f"✅ /unban [id] - Unban User")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID: return
    users = db["users"]
    text = f"📊 <b>Total Active Users: {len(users)}</b>\n━━━━━━━━━━━━━━━\n"
    for uid, info in list(users.items())[-15:]: # Show last 15
        text += f"👤 {info['name']}\n🆔 <code>{uid}</code> | {info['user']}\n\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    msg_text = message.text.split(None, 1)
    if len(msg_text) < 2: return
    
    success = 0
    for uid in db["users"]:
        try:
            bot.send_message(uid, f"📢 <b>Announcement</b>\n\n{msg_text[1]}")
            success += 1
        except: pass
    bot.reply_to(message, f"✅ Broadcast sent to {success} users.")

@bot.message_handler(commands=['ban'])
def ban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target = int(message.text.split()[1])
        db["banned"].append(target)
        save_data(db)
        bot.reply_to(message, f"🚫 User {target} Banned!")
    except: pass

# --- LOGGING ---
def notify_start():
    try:
        log_msg = (
            f"🚀 <b>System Live!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot:</b> {DEV_NAME}\n"
            f"🔑 <b>Token:</b> <code>{BOT_TOKEN[:10]}***</code>\n"
            f"⏰ <b>Time:</b> {get_time()}\n"
            f"📡 <b>Status:</b> 100% Smooth & Working\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(LOG_CHANNEL, log_msg)
    except: pass

if __name__ == "__main__":
    notify_start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
