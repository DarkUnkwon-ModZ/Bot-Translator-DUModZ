import telebot
import time
import datetime
import threading
import json
import os
from telebot import types, apihelper
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Accuracy Stability for Language Detection
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
        try:
            with open(USER_DB, 'r') as f: return json.load(f)
        except: return {"users": {}, "banned": []}
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
    return datetime.datetime.now().strftime("%I:%M %p | %d-%b-%Y")

# --- UI COMPONENTS ---
def welcome_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(f"✨ {DEV_NAME}", url=DEV_URL)
    btn2 = types.InlineKeyboardButton("🌐 Website", url=BLOG_URL)
    btn3 = types.InlineKeyboardButton("⚙️ AI Settings", callback_data="settings")
    btn4 = types.InlineKeyboardButton("📜 User Guide", callback_data="help")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# --- START HANDLER ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "N/A"

    # User Registration
    if uid not in db["users"]:
        db["users"][uid] = {"name": first_name, "user": username, "lang": "bn", "joined": get_time()}
        save_data(db)

    # Ban Check
    if int(uid) in db["banned"]:
        bot.send_message(message.chat.id, "🚫 <b>Access Denied!</b>\n\nYou have been blacklisted by the Administrator for violating terms.")
        return

    # Join Check
    if not is_joined(message.from_user.id):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📢 Join Official Channel", url=DEV_URL))
        m.add(types.InlineKeyboardButton("✅ I Have Joined", callback_data="verify_join"))
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"🛡️ <b>Verification Required</b>\n\nHello {first_name}!\nTo access our <b>Premium AI Translator</b>, please join our official channel first.", 
                       reply_markup=m)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>{DEV_NAME} Translator v3.5</b>\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"Welcome to the high-speed Neural AI Translator.\n\n"
                           f"👤 <b>User:</b> {first_name}\n"
                           f"🆔 <b>ID:</b> <code>{uid}</code>\n"
                           f"🎯 <b>Default Output:</b> {db['users'][uid]['lang'].upper()}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"<i>Type any message to start translating...</i>", reply_markup=welcome_markup())

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = str(call.from_user.id)
    
    if call.data == "verify_join":
        if is_joined(call.from_user.id):
            bot.edit_message_caption("✅ <b>Verified!</b> Accessing system...", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)

    elif call.data == "settings":
        langs = [("Bengali 🇧🇩", "bn"), ("English 🇺🇸", "en"), ("Hindi 🇮🇳", "hi"), 
                 ("Arabic 🇸🇦", "ar"), ("Spanish 🇪🇸", "es"), ("Urdu 🇵🇰", "ur")]
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(*[types.InlineKeyboardButton(n, callback_data=f"set_{c}") for n, c in langs])
        m.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_caption("⚙️ <b>AI Language Settings</b>\nSelect your target translation language:", 
                                 call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data.startswith("set_"):
        lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = lang
        save_data(db)
        bot.answer_callback_query(call.id, f"✅ Target Language set to {lang.upper()}", show_alert=False)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    elif call.data == "help":
        help_text = (
            "📖 <b>How to use the Bot:</b>\n\n"
            "1️⃣ <b>Direct Translation:</b> Just send any text in any language, the bot will auto-detect it.\n"
            "2️⃣ <b>Change Language:</b> Use ⚙️ Settings to change your output language.\n"
            "3️⃣ <b>Admin:</b> If you are admin, use /admin to see commands.\n\n"
            "💎 <i>The bot uses Deep-L and Google AI for 99.9% accuracy.</i>"
        )
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(help_text, call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION LOGIC ---
@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_joined(message.from_user.id): return
    if int(uid) in db["banned"]: return

    target = db["users"].get(uid, {}).get("lang", "en")
    
    # Smooth Animation
    status = bot.reply_to(message, "💫")
    
    try:
        text = message.text
        # Detection logic
        try:
            detected = detect(text).upper()
        except:
            detected = "Unknown"

        # Translation
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        
        # Premium Result UI
        result = (
            f"🌐 <b>AI Translation Success</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        
        time.sleep(0.5)
        bot.edit_message_text(result, message.chat.id, status.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ <b>AI Error:</b> {str(e)}\nTry again with simpler text.", message.chat.id, status.message_id)

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin', 'adminhelp'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ <b>Access Denied!</b>\nOnly the authorized Developer can use this command.")
        return
    
    admin_msg = (
        f"👑 <b>Master Admin Dashboard</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 /stats - Bot Global Statistics\n"
        f"📣 /broadcast - Send message to all\n"
        f"🚫 /ban [ID] - Blacklist a user\n"
        f"✅ /unban [ID] - Whitelist a user\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, admin_msg)

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID: return
    
    total_users = len(db["users"])
    total_banned = len(db["banned"])
    
    stats_text = (
        f"📊 <b>System Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: {total_users}\n"
        f"🚫 Banned Users: {total_banned}\n"
        f"📡 Server: Active\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, stats_text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    
    command_text = message.text.split(None, 1)
    if len(command_text) < 2:
        bot.reply_to(message, "❌ <b>Usage:</b> /broadcast [Your Message]")
        return
    
    msg_to_send = command_text[1]
    users = db["users"]
    success = 0
    fail = 0
    
    progress = bot.send_message(message.chat.id, "🚀 <b>Starting Global Broadcast...</b>")
    
    for uid in users:
        try:
            bot.send_message(uid, f"📢 <b>Important Announcement</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{msg_to_send}\n\n━━━━━━━━━━━━━━━━━━━━")
            success += 1
        except:
            fail += 1
    
    bot.edit_message_text(f"✅ <b>Broadcast Finished!</b>\n\n🟢 Success: {success}\n🔴 Failed: {fail}", message.chat.id, progress.message_id)

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        if uid not in db["banned"]:
            db["banned"].append(uid)
            save_data(db)
            bot.reply_to(message, f"✅ User <code>{uid}</code> has been banned.")
        else:
            bot.reply_to(message, "ℹ️ User is already banned.")
    except:
        bot.reply_to(message, "❌ <b>Usage:</b> /ban [User_ID]")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        if uid in db["banned"]:
            db["banned"].remove(uid)
            save_data(db)
            bot.reply_to(message, f"✅ User <code>{uid}</code> has been unbanned.")
        else:
            bot.reply_to(message, "ℹ️ User is not in the ban list.")
    except:
        bot.reply_to(message, "❌ <b>Usage:</b> /unban [User_ID]")

# --- SYSTEM NOTIFICATION ---
def notify_start():
    try:
        log_msg = (
            f"⭐ <b>System Online!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot:</b> {DEV_NAME}\n"
            f"📅 <b>Date:</b> {get_time()}\n"
            f"🚀 <b>Status:</b> Premium & Smooth\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(LOG_CHANNEL, log_msg)
    except: pass

# --- POLLING ---
if __name__ == "__main__":
    print("--- BOT IS RUNNING ---")
    notify_start()
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(5)
