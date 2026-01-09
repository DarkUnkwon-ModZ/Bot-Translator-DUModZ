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
# It is recommended to use os.getenv("BOT_TOKEN") for safety on GitHub
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/heads/main/Img/darkunkwonmodz-banner.jpg".strip()
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

# --- SUPPORTED LANGUAGES ---
LANG_MAP = {
    'en': 'English 🇺🇸', 'bn': 'Bengali 🇧🇩', 'hi': 'Hindi 🇮🇳',
    'ar': 'Arabic 🇸🇦', 'es': 'Spanish 🇪🇸', 'fr': 'French 🇫🇷',
    'de': 'German 🇩🇪', 'ja': 'Japanese 🇯🇵', 'ru': 'Russian 🇷🇺', 'pt': 'Portuguese 🇵🇹'
}

# --- UTILS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(REQ_CHANNEL.strip(), user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

def get_timestamp():
    # FIXED: Removed the double dot syntax error
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
        # FIXED: Added try-except for language detection to prevent crash on symbols/emojis
        try:
            src_lang = detect(text).upper()
        except:
            src_lang = "AUTO"

        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)

        if uid not in db["users"]:
             db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        
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
        bot.edit_message_text(response, status_msg.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ <b>AI Error:</b> Unable to translate. Try again.", status_msg.chat.id, status_msg.message_id)

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    if int(uid) in db.get("banned", []):
        return
    
    if uid not in db["users"]:
        db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        save_db(db)

    sub = is_subscribed(message.from_user.id)
    sub_status = "✅ Verified Member" if sub else "❌ Not Subscribed"
    
    if not sub:
        join_url = f"https://t.me/{REQ_CHANNEL.strip()[1:]}"
        markup = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("📢 Join Channel", url=join_url)],
            [types.InlineKeyboardButton("🔄 Verify", callback_data="verify_sub")]
        ])
        return bot.send_photo(
            message.chat.id,
            BANNER_URL,
            caption=f"👋 <b>Welcome!</b>\n🛡 Status: {sub_status}\n\nPlease join our channel to use the bot.",
            reply_markup=markup
        )

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

# --- LANGUAGE SHORT COMMANDS ---
@bot.message_handler(commands=['en', 'bn', 'hi', 'ar', 'es', 'fr', 'de', 'ja', 'ru', 'pt'])
def language_shortcuts(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db.get("banned", []):
        return

    cmd = message.text.split()[0][1:].lower()
    if cmd not in LANG_MAP:
        return

    args = message.text.replace(f'/{cmd}', '', 1).strip()

    if not args:
        if uid not in db["users"]:
             db["users"][uid] = {"name": message.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
        db["users"][uid]["lang"] = cmd
        save_db(db)
        bot.reply_to(message, f"✅ Your default target language has been set to <b>{LANG_MAP[cmd]}</b>")
    else:
        perform_translation(message, args, cmd, is_cmd=True)

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['stats', 'admin', 'broadcast', 'ban', 'unban'])
def admin_area(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    cmd = parts[0][1:]

    if cmd == 'stats':
        total = len(db["users"])
        banned = len(db.get("banned", []))
        stats = f"📊 <b>Bot Statistics</b>\nTotal Users: {total}\nBanned: {banned}\n\n<b>Recent Users:</b>\n"
        for uid, data in list(db["users"].items())[-10:]:
            stats += f"• {data.get('name', 'User')} (<code>{uid}</code>) -> {data.get('lang', 'en').upper()}\n"
        bot.reply_to(message, stats)
    
    elif cmd == 'broadcast':
        if len(parts) < 2:
            return bot.reply_to(message, "❌ Message missing.")
        txt = parts[1]
        sent = 0
        for u in list(db["users"].keys()):
            try:
                bot.send_message(u, f"📣 <b>Announcement</b>\n\n{txt}")
                sent += 1
                time.sleep(0.1) # Prevent flood
            except:
                pass
        bot.reply_to(message, f"✅ Broadcast sent to {sent} users.")

    elif cmd == 'ban':
        if len(parts) < 2:
            return bot.reply_to(message, "❌ Usage: /ban <user_id>")
        try:
            target_uid = int(parts[1])
            if target_uid not in db["banned"]:
                db["banned"].append(target_uid)
                save_db(db)
                bot.reply_to(message, f"✅ User <code>{target_uid}</code> banned.")
            else:
                bot.reply_to(message, "⚠️ User already banned.")
        except:
            bot.reply_to(message, "❌ Invalid user ID.")

    elif cmd == 'unban':
        if len(parts) < 2:
            return bot.reply_to(message, "❌ Usage: /unban <user_id>")
        try:
            target_uid = int(parts[1])
            if target_uid in db["banned"]:
                db["banned"].remove(target_uid)
                save_db(db)
                bot.reply_to(message, f"✅ User <code>{target_uid}</code> unbanned.")
            else:
                bot.reply_to(message, "⚠️ User not banned.")
        except:
            bot.reply_to(message, "❌ Invalid user ID.")

# --- CALLBACKS & TEXT HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified! You may now use the bot.", show_alert=True)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Still not subscribed!", show_alert=True)
        return

    if int(uid) in db.get("banned", []):
        bot.answer_callback_query(call.id, "❌ You are banned.", show_alert=True)
        return

    if not is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Please subscribe first!", show_alert=True)
        return

    if call.data == "open_settings":
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=msg_id,
            caption="⚙️ <b>Select AI Target Language:</b>",
            reply_markup=get_settings_keyboard()
        )
    elif call.data.startswith("lang_"):
        lang_code = call.data.split("_")[1]
        if lang_code in LANG_MAP:
            if uid not in db["users"]:
                db["users"][uid] = {"name": call.from_user.first_name, "lang": "en", "date": get_timestamp(), "count": 0}
            db["users"][uid]["lang"] = lang_code
            save_db(db)
            bot.answer_callback_query(call.id, f"✅ Language set to {LANG_MAP[lang_code]}")
            
            curr_lang = lang_code.upper()
            welcome_text = (
                f"🚀 <b>{DEV_NAME} Translator v8.0</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>User:</b> {call.from_user.first_name}\n"
                f"🛡 <b>Status:</b> ✅ Verified Member\n"
                f"🎯 <b>Default Mode:</b> Auto → <code>{curr_lang}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Send any text to translate to <b>{curr_lang}</b>."
            )
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=msg_id,
                caption=welcome_text,
                reply_markup=get_main_keyboard()
            )
    elif call.data == "back_home":
        curr_lang = db["users"].get(uid, {}).get("lang", "en").upper()
        welcome_text = (
            f"🚀 <b>{DEV_NAME} Translator v8.0</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {call.from_user.first_name}\n"
            f"🛡 <b>Status:</b> ✅ Verified Member\n"
            f"🎯 <b>Default Mode:</b> Auto → <code>{curr_lang}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Send any text to translate to <b>{curr_lang}</b>."
        )
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=msg_id,
            caption=welcome_text,
            reply_markup=get_main_keyboard()
        )
    elif call.data == "my_profile":
        user_data = db["users"].get(uid, {})
        count = user_data.get("count", 0)
        lang = LANG_MAP.get(user_data.get("lang", "en"), "English")
        joined = user_data.get("date", "Unknown")
        profile_text = (
            f"👤 <b>My Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: <code>{call.from_user.id}</code>\n"
            f"📛 Name: {call.from_user.first_name}\n"
            f"🌐 Language: {lang}\n"
            f"📅 Joined: {joined}\n"
            f"📤 Translations: {count}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=msg_id,
            caption=profile_text,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔙 Back", callback_data="back_home")
            )
        )
    elif call.data == "user_guide":
        guide = (
            "📜 <b>User Guide</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• Send any text to auto-translate.\n"
            "• Use /en, /bn etc. to set language or translate instantly.\n"
            "• Tap ⚙️ AI Settings to change default language.\n"
            "• Must stay subscribed to @Dark_Unkwon_ModZ.\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=msg_id,
            caption=guide,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔙 Back", callback_data="back_home")
            )
        )

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def auto_translate(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db.get("banned", []):
        return
    target = db["users"].get(uid, {}).get("lang", "en")
    perform_translation(message, message.text, target)

if __name__ == "__main__":
    print("--- BOT STARTED SUCCESSFULLY ---")
    bot.infinity_polling()
