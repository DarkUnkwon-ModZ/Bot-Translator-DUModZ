import telebot
import time
import datetime
import threading
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from collections import defaultdict, deque

# Accuracy নিশ্চিত করার জন্য
DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

# Use threaded=True for better performance
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True, num_threads=10)

# --- DATABASE (Simulated) ---
user_list = set()
user_banned = set()
user_target_lang = defaultdict(lambda: 'en')  
last_request_time = {}

# --- HELPER FUNCTIONS ---
def is_joined(user_id):
    if user_id == ADMIN_ID: return True # এডমিনের জয়েন চেক লাগবে না
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def animated_loading(chat_id, message_id):
    """Smooth Premium Animation - Optimized to prevent Flood Control"""
    frames = [
        "🌐 <b>Analyzing...</b>",
        "⚡ <b>Neural Processing...</b>",
        "🧠 <b>Translating Context...</b>",
        "✅ <b>Finalizing Output...</b>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.7) # Slightly longer delay to avoid Telegram limits
        except Exception:
            break

# --- KEYBOARDS ---
def get_start_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✨ Official Channel", url=DEV_URL)
    btn2 = types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    btn3 = types.InlineKeyboardButton("📜 Help", callback_data="help")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup

def get_language_selection_markup():
    langs = [
        ("English", "en"), ("Bengali", "bn"), ("Hindi", "hi"),
        ("Arabic", "ar"), ("Spanish", "es"), ("French", "fr"),
        ("Russian", "ru"), ("Chinese", "zh"), ("Japanese", "ja")
    ]
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"set_lang_{code}") for name, code in langs]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
    return markup

# --- CORE LOGIC ---
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    user_list.add(user_id)

    if user_id in user_banned:
        bot.reply_to(message, "🚫 <b>Access Denied!</b>\nYou are banned.")
        return

    if not is_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Verify Connection", callback_data="verify"))
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"⚠️ <b>Action Required!</b>\n\nDear {message.from_user.first_name},\nYou must join our channel to use this AI Translator.",
                       reply_markup=markup)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>{BOT_NAME} v2.5 Online</b>\n\n"
                           f"Welcome! Send any text to translate automatically.\n"
                           f"🎯 <b>Target Language:</b> {user_target_lang[user_id].upper()}\n\n"
                           f"<i>Type /help or /adminhelp for more.</i>",
                   reply_markup=get_start_markup())

# --- ADMIN HELP COMMAND (Fixed) ---
@bot.message_handler(commands=['adminhelp', 'admin'])
def admin_help(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ <b>Admin Only!</b>")
        return
    
    admin_txt = (
        "👑 <b>Premium Admin Dashboard</b>\n\n"
        "📊 <b>Stats:</b> /stats\n"
        "📢 <b>Broadcast:</b> /broadcast [message]\n"
        "🚫 <b>Ban User:</b> /ban [user_id]\n"
        "✅ <b>Unban User:</b> /unban [user_id]\n"
        "ℹ️ <b>Check ID:</b> /id (Reply to user)\n\n"
        "<i>All systems are 100% operational.</i>"
    )
    bot.reply_to(message, admin_txt)

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 <b>Bot Stats:</b>\n\nTotal Users: {len(user_list)}\nBanned: {len(user_banned)}")

@bot.message_handler(commands=['ban'])
def ban_handler(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            user_banned.add(target_id)
            bot.reply_to(message, f"🚫 User {target_id} banned!")
        except:
            bot.reply_to(message, "Use: /ban [id]")

@bot.message_handler(commands=['unban'])
def unban_handler(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            user_banned.discard(target_id)
            bot.reply_to(message, f"✅ User {target_id} unbanned!")
        except:
            bot.reply_to(message, "Use: /unban [id]")

@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.split(None, 1)
    if len(text) < 2: return
    
    success = 0
    for user in list(user_list):
        try:
            bot.send_message(user, f"📣 <b>Broadcast:</b>\n\n{text[1]}")
            success += 1
        except: pass
    bot.reply_to(message, f"✅ Sent to {success} users.")

# --- TRANSLATION CORE (Ultra Smooth) ---
def process_translation(message, text, src='auto'):
    user_id = message.from_user.id
    target = user_target_lang[user_id]
    
    # Check rate limit (1 req every 2 seconds)
    now = time.time()
    if user_id in last_request_time and now - last_request_time[user_id] < 2:
        return
    last_request_time[user_id] = now

    msg = bot.reply_to(message, "🌀 <b>Connecting...</b>")
    
    # Threaded animation to prevent blocking
    threading.Thread(target=animated_loading, args=(message.chat.id, msg.message_id)).start()
    
    try:
        # Delay for animation feel
        time.sleep(2.5) 
        
        translated = GoogleTranslator(source=src, target=target).translate(text)
        detected = detect(text).upper()
        
        res = (
            f"🌐 <b>AI Translation Result</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>From ({detected}):</b>\n<code>{text[:100]}</code>\n\n"
            f"📤 <b>To ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Join @Dark_Unkwon_ModZ</i>"
        )
        bot.edit_message_text(res, message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ <b>Error:</b> Translation failed. Try shorter text.", message.chat.id, msg.message_id)

@bot.message_handler(commands=['bn', 'hi', 'en', 'ar', 'es', 'fr'])
def manual_cmd(message):
    if not is_joined(message.from_user.id): return
    cmd = message.text.split()[0][1:]
    input_text = message.text.replace(f"/{cmd}", "").strip()
    if input_text:
        # Temporary language switch
        old = user_target_lang[message.from_user.id]
        user_target_lang[message.from_user.id] = cmd
        process_translation(message, input_text)
        user_target_lang[message.from_user.id] = old
    else:
        bot.reply_to(message, f"Usage: <code>/{cmd} Hello</code>")

@bot.message_handler(content_types=['text'])
def auto_trans(message):
    if message.text.startswith('/') or not is_joined(message.from_user.id): return
    if message.from_user.id in user_banned: return
    process_translation(message, message.text)

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid = call.from_user.id
    if call.data == "verify":
        if is_joined(uid):
            bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_handler(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Not joined yet!", show_alert=True)
    
    elif call.data == "settings":
        bot.edit_message_caption("⚙️ <b>Select Default Language:</b>", call.message.chat.id, call.message.message_id, reply_markup=get_language_selection_markup())
    
    elif call.data.startswith("set_lang_"):
        lang = call.data.split("_")[-1]
        user_target_lang[uid] = lang
        bot.answer_callback_query(call.id, f"✅ Set to {lang.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_handler(call.message)

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_handler(call.message)

    elif call.data == "help":
        bot.edit_message_caption("📜 <b>Translator Help</b>\n\n1. Just send text for auto-translate.\n2. Use /bn, /hi for quick result.\n3. Change language in Settings.", 
                                 call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

def log_start():
    try: bot.send_message(LOG_CHANNEL, f"🚀 <b>Bot Restarted!</b>\nTime: {datetime.datetime.now()}")
    except: pass

if __name__ == "__main__":
    print("🚀 DUModZ Translator Started...")
    log_start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
