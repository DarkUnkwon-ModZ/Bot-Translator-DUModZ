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
    with open(DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {"users": {}, "banned": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- UTILS & HELPERS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- DYNAMIC UI ---
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
    # ১০টি জনপ্রিয় ভাষা যুক্ত করা হয়েছে
    langs = [
        ("English 🇺🇸", "en"), ("Bengali 🇧🇩", "bn"), 
        ("Hindi 🇮🇳", "hi"), ("Arabic 🇸🇦", "ar"), 
        ("Spanish 🇪🇸", "es"), ("French 🇫🇷", "fr"),
        ("German 🇩🇪", "de"), ("Japanese 🇯🇵", "ja"),
        ("Russian 🇷🇺", "ru"), ("Portuguese 🇵🇹", "pt")
    ]
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
    
    # ইউজার রেজিস্ট্রেশন (ডিফল্ট টার্গেট: English)
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": first_name,
            "lang": "en", 
            "date": get_timestamp(),
            "count": 0
        }
        save_db(db)

    if int(uid) in db["banned"]:
        return bot.reply_to(message, "🚫 <b>Access Revoked!</b>\nYou are banned.")

    subscribed = is_subscribed(message.from_user.id)
    sub_status = "✅ Verified Member" if subscribed else "❌ Not Subscribed"
    
    if not subscribed:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub"))
        return bot.send_photo(message.chat.id, BANNER_URL, 
                             caption=f"👋 <b>Welcome {first_name}!</b>\n\n🛡 <b>Status:</b> {sub_status}\n\nPlease join our channel to use the AI Translator.", 
                             reply_markup=markup)

    current_lang = db["users"][uid].get("lang", "en").upper()
    welcome_text = (
        f"🚀 <b>{DEV_NAME} Translator v5.0</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {first_name}\n"
        f"🛡 <b>Status:</b> {sub_status}\n"
        f"🎯 <b>Target Language:</b> <code>{current_lang}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Send any text in <b>Any Language</b> and I will translate it to <b>{current_lang}</b> instantly."
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=welcome_text, reply_markup=get_main_keyboard(uid))

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    
    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)

    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>AI Settings Panel</b>\nSelect your target output language:", 
                                 call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = new_lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Target set to {new_lang.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

    elif call.data == "my_profile":
        u_data = db["users"][uid]
        profile_text = (
            f"👤 <b>User Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Name:</b> {u_data['name']}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Target:</b> {u_data['lang'].upper()}\n"
            f"📊 <b>Usage:</b> {u_data.get('count', 0)} translations\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(profile_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "user_guide":
        guide = (
            "📖 <b>How to Use</b>\n\n"
            "1. Just send any text (e.g., Bengali, Hindi, etc).\n"
            "2. AI will detect it and translate to your target language.\n"
            "3. Change target language via <b>AI Settings</b>.\n\n"
            "<b>Supported:</b> EN, BN, HI, AR, ES, FR, DE, JA, RU, PT."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(guide, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

# --- TRANSLATION ENGINE ---

def dynamic_animation(chat_id, msg_id):
    frames = ["🌀 𝗔𝗜 𝗔𝗻𝗮𝗹𝘆𝘇𝗶𝗻𝗴...", "⚡ 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...", "📡 𝗙𝗶𝗻𝗮𝗹𝗶𝘇𝗶𝗻𝗴..."]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, msg_id)
            time.sleep(0.5)
        except: break

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def translate_text(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return

    target_lang = db["users"].get(uid, {}).get("lang", "en")
    text = message.text
    
    status_msg = bot.reply_to(message, "⏳ 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴...")
    threading.Thread(target=dynamic_animation, args=(message.chat.id, status_msg.message_id)).start()
    
    try:
        # নিখুঁত ডিটেকশন লজিক
        try:
            detected_code = detect(text)
            # যদি ডিটেক্ট করা ভাষা আর টার্গেট ভাষা একই হয় (যেমন EN to EN), তবুও অনুবাদক কল করা নিরাপদ
        except:
            detected_code = "auto"

        # Translation execution
        translator = GoogleTranslator(source='auto', target=target_lang)
        result_text = translator.translate(text)

        # বাগ ফিক্স: যদি ফলাফল খালি আসে বা ইনপুটের সমান হয় (একই ভাষার ক্ষেত্রে)
        if not result_text: result_text = text

        db["users"][uid]["count"] = db["users"][uid].get("count", 0) + 1
        save_db(db)

        response = (
            f"✅ <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected_code.upper()}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target_lang.upper()}):</b>\n<code>{result_text}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        time.sleep(0.5)
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ <b>AI Error:</b> Please try again with shorter text.", message.chat.id, status_msg.message_id)

# --- ADMIN PANEL ---

@bot.message_handler(commands=['admin', 'stats', 'broadcast', 'ban', 'unban'])
def admin_handler(message):
    if message.from_user.id != ADMIN_ID: return

    cmd = message.text.split()[0][1:]

    if cmd == 'stats':
        total = len(db["users"])
        msg = f"📊 <b>User Statistics</b>\nTotal Users: {total}\n\n"
        # শেষ ২০ জন ইউজারের ডিটেইলস
        user_items = list(db["users"].items())[-20:]
        for id, data in user_items:
            msg += f"• {data['name']} | <code>{id}</code> | {data['lang'].upper()}\n"
        bot.reply_to(message, msg)

    elif cmd == 'broadcast':
        content = message.text.replace('/broadcast', '').strip()
        if not content: return
        for u in db["users"]:
            try: bot.send_message(u, f"📢 <b>Announcement:</b>\n\n{content}")
            except: pass
        bot.reply_to(message, "✅ Broadcast Done.")

    elif cmd == 'ban':
        try:
            tid = int(message.text.split()[1])
            if tid not in db["banned"]: db["banned"].append(tid); save_db(db)
            bot.reply_to(message, f"🚫 {tid} Banned.")
        except: pass

    elif cmd == 'unban':
        try:
            tid = int(message.text.split()[1])
            if tid in db["banned"]: db["banned"].remove(tid); save_db(db)
            bot.reply_to(message, f"✅ {tid} Unbanned.")
        except: pass

if __name__ == "__main__":
    print(f"--- {DEV_NAME} BOT ONLINE ---")
    bot.infinity_polling()
