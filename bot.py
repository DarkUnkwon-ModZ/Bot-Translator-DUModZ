import telebot
import time
import datetime
import threading
import json
import os
import random
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

# --- DATABASE MANAGEMENT (উন্নত করা হয়েছে) ---
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

# --- DYNAMIC UI (আগের সব বাটন অক্ষুণ্ণ) ---
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
    langs = [
        ("English 🇺🇸", "en"), ("Bengali 🇧🇩", "bn"), 
        ("Hindi 🇮🇳", "hi"), ("Arabic 🇸🇦", "ar"), 
        ("Spanish 🇪🇸", "es"), ("French 🇫🇷", "fr")
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
    
    # Register User (Default Target Language: English)
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": first_name,
            "lang": "en", # ডিফল্ট ইংরেজি করা হয়েছে
            "date": get_timestamp(),
            "count": 0
        }
        save_db(db)

    if int(uid) in db["banned"]:
        return bot.reply_to(message, "🚫 <b>Access Revoked!</b>\nYou are banned from using this service.")

    # সাবস্ক্রিপশন চেক
    sub_status = "✅ Verified Member" if is_subscribed(message.from_user.id) else "❌ Not Subscribed"
    
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub"))
        return bot.send_photo(message.chat.id, BANNER_URL, 
                             caption=f"👋 <b>Welcome {first_name}!</b>\n\n🛡 <b>Status:</b> {sub_status}\n\nYou must join our official channel to unlock the <b>Premium Translator</b> features.", 
                             reply_markup=markup)

    current_lang = db["users"][uid].get("lang", "en").upper()
    welcome_text = (
        f"🚀 <b>{DEV_NAME} Translator v4.5</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {first_name}\n"
        f"🛡 <b>Status:</b> {sub_status}\n"
        f"🎯 <b>Current Target:</b> <code>{current_lang}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Hello! I am your advanced AI assistant. Send me any text in <b>Any Language</b> and I will translate it to <b>{current_lang}</b> instantly."
    )
    bot.send_photo(message.chat.id, BANNER_URL, caption=welcome_text, reply_markup=get_main_keyboard(uid))

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = str(call.from_user.id)
    
    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verification Successful!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined yet!", show_alert=True)

    elif call.data == "open_settings":
        bot.edit_message_caption("⚙️ <b>AI Settings Panel</b>\nSelect your desired output language:", 
                                 call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard())

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        db["users"][uid]["lang"] = new_lang
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ Language updated to {new_lang.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

    elif call.data == "my_profile":
        u_data = db["users"][uid]
        profile_text = (
            f"👤 <b>Premium User Profile</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Name:</b> {u_data['name']}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"📅 <b>Registered:</b> {u_data['date']}\n"
            f"🌐 <b>Target Language:</b> {u_data['lang'].upper()}\n"
            f"📊 <b>Total Translations:</b> {u_data.get('count', 0)}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(profile_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "user_guide":
        guide = (
            "📖 <b>AI Translator Guide</b>\n\n"
            "1. Send any text in <b>Any Language</b> (Bengali, Hindi, French etc).\n"
            "2. Bot will auto-detect the input language.\n"
            "3. Result will be in your <b>Target Language</b> (Default: English).\n\n"
            "⚠️ <i>Note: Use settings to change the output language.</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(guide, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

# --- TRANSLATION ENGINE (বাগ ফিক্সড ও শক্তিশালী) ---

def dynamic_animation(chat_id, msg_id):
    frames = ["🌀 𝗔𝗜 𝗜𝘀 𝗔𝗻𝗮𝗹𝘆𝘇𝗶𝗻𝗴...", "⚡ 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗗𝗮𝘁𝗮...", "📡 𝗙𝗶𝗻𝗮𝗹𝗶𝘇𝗶𝗻𝗴 𝗧𝗿𝗮𝗻𝘀𝗹𝗮𝘁𝗶𝗼𝗻..."]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, msg_id)
            time.sleep(0.6)
        except: break

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def translate_text(message):
    uid = str(message.from_user.id)
    if not is_subscribed(message.from_user.id) or int(uid) in db["banned"]: return

    target_lang = db["users"].get(uid, {}).get("lang", "en")
    text = message.text
    
    # Progress Message
    status_msg = bot.reply_to(message, "⏳ 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝗔𝗜...")
    threading.Thread(target=dynamic_animation, args=(message.chat.id, status_msg.message_id)).start()
    
    try:
        # নিখুঁত Language Detection
        try:
            detected_code = detect(text)
            detected_lang = detected_code.upper()
        except:
            detected_code = "auto"
            detected_lang = "AUTO"

        # Translation Logic (নিখুঁত করার জন্য একই ভাষা হলে সরাসরি পাঠানো)
        if detected_code == target_lang:
            result_text = text
        else:
            translator = GoogleTranslator(source='auto', target=target_lang)
            result_text = translator.translate(text)

        # Update Count
        db["users"][uid]["count"] = db["users"][uid].get("count", 0) + 1
        save_db(db)

        response = (
            f"✅ <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected_lang}):</b>\n<code>{text}</code>\n\n"
            f"📤 <b>Output ({target_lang.upper()}):</b>\n<code>{result_text}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Powered by {DEV_NAME}</i>"
        )
        time.sleep(1.2)
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ <b>AI Error:</b> Unable to process. Please try again later.", message.chat.id, status_msg.message_id)

# --- ADVANCED ADMIN PANEL (সব কমান্ড কার্যকরী) ---

@bot.message_handler(commands=['admin', 'stats', 'broadcast', 'ban', 'unban'])
def admin_handler(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⚠️ <b>Access Denied!</b>")

    cmd = message.text.split()[0][1:]

    if cmd == 'admin':
        admin_help = (
            "👑 <b>Admin Control Panel</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 /stats - Show detailed user info\n"
            "📣 /broadcast [msg] - Send global message\n"
            "🚫 /ban [id] - Ban a user\n"
            "✅ /unban [id] - Unban a user\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, admin_help)

    elif cmd == 'stats':
        total_users = len(db["users"])
        banned_users = len(db["banned"])
        
        stat_msg = f"📈 <b>Bot Statistics</b>\n\nTotal Users: {total_users}\nBanned Users: {banned_users}\n\n"
        stat_msg += "📋 <b>Recent Users Details:</b>\n"
        
        # শেষের ১০ জন ইউজারের ডিটেইলস দেখাবে
        user_list = list(db["users"].items())[-10:]
        for uid, data in user_list:
            stat_msg += f"• {data['name']} (<code>{uid}</code>) - {data['lang'].upper()}\n"
            
        bot.reply_to(message, stat_msg)

    elif cmd == 'broadcast':
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text: return bot.reply_to(message, "❌ Provide a message.")
        
        count = 0
        for user in db["users"]:
            try:
                bot.send_message(user, f"📢 <b>Global Announcement</b>\n\n{msg_text}\n\n<i>By Admin</i>")
                count += 1
            except: pass
        bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

    elif cmd == 'ban':
        try:
            target = int(message.text.split()[1])
            if target not in db["banned"]:
                db["banned"].append(target)
                save_db(db)
                bot.reply_to(message, f"🚫 User {target} has been banned.")
        except: bot.reply_to(message, "❌ Invalid ID.")

    elif cmd == 'unban':
        try:
            target = int(message.text.split()[1])
            if target in db["banned"]:
                db["banned"].remove(target)
                save_db(db)
                bot.reply_to(message, f"✅ User {target} has been unbanned.")
        except: bot.reply_to(message, "❌ Invalid ID.")

# --- INITIALIZATION ---
if __name__ == "__main__":
    print(f"--- {DEV_NAME} BOT STARTED ---")
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 <b>Bot System Online!</b>\nTime: {get_timestamp()}")
    except: pass
    bot.infinity_polling()
