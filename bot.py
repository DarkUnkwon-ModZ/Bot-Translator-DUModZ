import telebot
import time
import datetime
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
    return datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

# --- KEYBOARDS ---
def get_start_keyboard(subbed=False):
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
    LANG_MAP = {'en': 'English 🇺🇸', 'bn': 'Bengali 🇧🇩', 'hi': 'Hindi 🇮🇳', 'ar': 'Arabic 🇸🇦', 'es': 'Spanish 🇪🇸', 'fr': 'French 🇫🇷'}
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"lang_{code}") for code, name in LANG_MAP.items()]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home"))
    return markup

# --- LOGGING TO MANAGER ---
def log_to_manager(action_type):
    try:
        bot_info = bot.get_me()
        log_text = (
            f"🔔 <b>Bot Status Update</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot Name:</b> {bot_info.first_name}\n"
            f"🆔 <b>Username:</b> @{bot_info.username}\n"
            f"⚡ <b>Action:</b> {action_type}\n"
            f"⏰ <b>Time:</b> {get_timestamp()}\n"
            f"📡 <b>Status:</b> Live & Operational\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(LOG_CHANNEL, log_text)
    except: pass

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    if int(uid) in db.get("banned", []): return

    bot.send_chat_action(message.chat.id, 'typing')
    
    if uid not in db["users"]:
        db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        save_db(db)

    sub = is_subscribed(message.from_user.id)
    
    caption = (
        f"👋 <b>Welcome to {DEV_NAME} Translator!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Your ultimate AI-powered translation companion. Fast, secure, and accurate.\n\n"
        f"🛡 <b>Subscription:</b> {'✅ Active' if sub else '❌ Required'}\n"
        f"🎯 <b>Target:</b> {db['users'][uid].get('lang', 'en').upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    bot.send_photo(message.chat.id, BANNER_URL, caption=caption, reply_markup=get_start_keyboard(sub))

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    if call.data == "verify_sub":
        bot.edit_message_caption("🔄 <b>Verifying security layers...</b>", call.message.chat.id, call.message.message_id)
        time.sleep(1.5)
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!", show_alert=True)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join @Dark_Unkwon_ModZ first!", show_alert=True)
            start_command(call.message)
            
    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>Select AI Target Language:</b>", call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Language set to {lang.upper()}")
        start_command(call.message)

    elif call.data == "back_home":
        start_command(call.message)

    elif call.data == "my_profile":
        u = db["users"].get(uid, {})
        profile = (
            f"👤 <b>Premium User Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"📛 <b>Name:</b> {call.from_user.first_name}\n"
            f"📊 <b>Total Usage:</b> {u.get('count', 0)}\n"
            f"📅 <b>Joined:</b> {u.get('date', 'N/A')}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_caption(profile, call.message.chat.id, call.message.message_id, reply_markup=get_start_keyboard(True))

# --- TRANSLATION LOGIC ---
@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db.get("banned", []):
        return start_command(message)

    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "✨ <b>AI is thinking...</b>")
    
    try:
        target = db["users"].get(uid, {}).get("lang", "en")
        text = message.text
        
        # Smooth animation feel
        bot.edit_message_text("⚡ <b>AI is translating...</b>", status_msg.chat.id, status_msg.message_id)
        
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        
        try: src_lang = detect(text).upper()
        except: src_lang = "AUTO"

        db["users"][uid]["count"] += 1
        save_db(db)

        res = (
            f"✅ <b>AI Translation Success</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({src_lang}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Translated by {DEV_NAME}</i>"
        )
        bot.edit_message_text(res, status_msg.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ <b>Error:</b> Something went wrong!", status_msg.chat.id, status_msg.message_id)

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin', 'stats', 'broadcast', 'ban', 'unban'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    cmd = message.text.split()[0][1:]
    if cmd == 'admin':
        bot.reply_to(message, "👑 <b>Admin Master Control</b>\n\n/stats - Bot Usage\n/broadcast - Message All\n/ban ID - Ban User\n/unban ID - Unban")
    
    elif cmd == 'stats':
        bot.reply_to(message, f"📊 <b>Total Users:</b> {len(db['users'])}\n🚫 <b>Banned:</b> {len(db.get('banned', []))}")

    elif cmd == 'broadcast':
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text: return bot.reply_to(message, "Provide message!")
        for user_id in db["users"]:
            try: bot.send_message(user_id, f"📣 <b>Broadcast from Admin</b>\n\n{msg_text}")
            except: pass
        bot.reply_to(message, "✅ Broadcast completed.")

if __name__ == "__main__":
    log_to_manager("Bot Started / Restarted")
    print("Bot is running...")
    bot.infinity_polling()
