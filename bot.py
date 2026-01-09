import telebot
import time
import datetime
import threading
import json
import os
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# --- CONFIGURATION (অপরিবর্তিত) ---
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

# ১০টি ভাষার তালিকা
LANG_MAP = {
    "en": "English 🇺🇸", "bn": "Bengali 🇧🇩", "hi": "Hindi 🇮🇳", 
    "ar": "Arabic 🇸🇦", "es": "Spanish 🇪🇸", "fr": "French 🇫🇷",
    "de": "German 🇩🇪", "ru": "Russian 🇷🇺", "ja": "Japanese 🇯🇵", "ur": "Urdu 🇵🇰"
}

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
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"lang_{code}") for code, name in LANG_MAP.items()]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home"))
    return markup

# --- CORE HANDLERS ---

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    first_name = message.from_user.first_name
    
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

    sub_status = "✅ Verified Member" if is_subscribed(message.from_user.id) else "❌ Not Subscribed"
    
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub"))
        return bot.send_photo(message.chat.id, BANNER_URL, 
                             caption=f"👋 <b>Welcome {first_name}!</b>\n\n🛡 <b>Status:</b> {sub_status}\n\nYou must join our channel to use the bot.", 
                             reply_markup=markup)

    current_lang_code = db["users"][uid].get("lang", "en")
    current_lang_name = LANG_MAP.get(current_lang_code, "English")
    
    welcome_text = (
        f"🚀 <b>{DEV_NAME} Translator v5.0</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {first_name}\n"
        f"🛡 <b>Status:</b> {sub_status}\n"
        f"🎯 <b>Target Language:</b> <code>{current_lang_name}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"আমি একটি উন্নত AI অনুবাদক। যেকোনো ভাষায় টেক্সট পাঠান, আমি তা স্বয়ংক্রিয়ভাবে <b>{current_lang_name}</b> এ রূপান্তর করবো।"
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=welcome_text, reply_markup=get_main_keyboard(uid))

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    
    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)

    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>AI Settings Panel</b>\nSelect output language:", 
                                 call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = new_lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Language set to {LANG_MAP[new_lang]}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

    elif call.data == "my_profile":
        u_data = db["users"][uid]
        profile_text = (
            f"👤 <b>User Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Name:</b> {u_data['name']}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"📅 <b>Joined:</b> {u_data['date']}\n"
            f"🌐 <b>Target:</b> {LANG_MAP.get(u_data['lang'], 'English')}\n"
            f"📊 <b>Total Used:</b> {u_data.get('count', 0)}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(profile_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "user_guide":
        guide = (
            "📖 <b>AI Translator Guide</b>\n\n"
            "১. যেকোনো ভাষায় টেক্সট লিখুন, বট অটো ডিটেক্ট করবে।\n"
            "২. ডিফল্ট ভাষা English, সেটিংস থেকে পরিবর্তন করা যায়।\n"
            "৩. <b>Direct Commands:</b>\n"
            "   • <code>/en Hello</code> (English)\n"
            "   • <code>/bn Hello</code> (Bengali)\n"
            "   • <code>/hi Hello</code> (Hindi)\n\n"
            "<b>Available Languages:</b>\n" + ", ".join(LANG_MAP.values())
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(guide, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

# --- TRANSLATION ENGINE ---

def dynamic_animation(chat_id, msg_id):
    frames = ["🌀 AI Is Analyzing...", "⚡ Processing Data...", "📡 Finalizing Output..."]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, msg_id)
            time.sleep(0.5)
        except: break

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return

    text = message.text
    target_lang = db["users"].get(uid, {}).get("lang", "en")

    # হ্যান্ডেল প্রিফিক্স কমান্ড (যেমন: /en টেক্সট)
    if text.startswith('/'):
        parts = text.split(maxsplit=1)
        cmd = parts[0][1:].lower()
        if cmd in LANG_MAP:
            target_lang = cmd
            if len(parts) > 1:
                text = parts[1]
            else:
                return # শুধু কমান্ড দিলে কিছু করবে না
        elif cmd in ['start', 'admin', 'stats', 'broadcast', 'ban', 'unban']:
            return # এগুলো অ্যাডমিন কমান্ডের জন্য

    # Progress
    status_msg = bot.reply_to(message, "⏳ Connecting to AI...")
    threading.Thread(target=dynamic_animation, args=(message.chat.id, status_msg.message_id)).start()
    
    try:
        # নিখুঁত ডিটেকশন
        try:
            detected_code = detect(text)
        except:
            detected_code = "auto"

        # যদি ইনপুট এবং টার্গেট একই হয়, অনুবাদ করার দরকার নেই (বাগ ফিক্স)
        if detected_code == target_lang:
            result_text = text
        else:
            result_text = GoogleTranslator(source='auto', target=target_lang).translate(text)

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
        time.sleep(1)
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ <b>AI Error:</b> সাময়িক সমস্যা হচ্ছে। পরে চেষ্টা করুন।", message.chat.id, status_msg.message_id)

# --- ADVANCED ADMIN PANEL ---

@bot.message_handler(commands=['admin', 'stats', 'broadcast', 'ban', 'unban'])
def admin_handler(message):
    if message.from_user.id != ADMIN_ID: return

    cmd = message.text.split()[0][1:]

    if cmd == 'stats':
        total = len(db["users"])
        msg = f"📊 <b>Detailed User Statistics</b>\nTotal Users: {total}\n\n"
        for i, (uid, data) in enumerate(list(db["users"].items())[-20:], 1): # শেষ ২০ জন
            msg += f"{i}. {data['name']} | ID: <code>{uid}</code> | Lang: {data['lang'].upper()}\n"
        bot.reply_to(message, msg)

    elif cmd == 'broadcast':
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text: return bot.reply_to(message, "Provide message.")
        for user in db["users"]:
            try: bot.send_message(user, f"📢 <b>Announcement</b>\n\n{msg_text}")
            except: pass
        bot.reply_to(message, "✅ Sent.")

    elif cmd == 'ban':
        try:
            tid = int(message.text.split()[1])
            db["banned"].append(tid)
            save_db(db)
            bot.reply_to(message, f"🚫 Banned {tid}")
        except: pass

# --- RUN ---
if __name__ == "__main__":
    print(f"--- {DEV_NAME} BOT STARTED ---")
    bot.infinity_polling()
