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

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE (Simulated) ---
user_list = set()
user_banned = set()
user_target_lang = defaultdict(lambda: 'en')  
user_history = defaultdict(lambda: deque(maxlen=5))  
last_request_time = {}

# --- RATE LIMITING ---
REQUEST_COOLDOWN = 3  # কমানো হয়েছে দ্রুত রেসপন্সের জন্য

def is_rate_limited(user_id):
    now = time.time()
    if user_id in last_request_time:
        if now - last_request_time[user_id] < REQUEST_COOLDOWN:
            return True
    last_request_time[user_id] = now
    return False

# --- HELPER FUNCTIONS ---
def is_joined(user_id):
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def auto_delete_message(chat_id, message_id, delay=15):
    """মেসেজ ক্লিন রাখার জন্য অটো-ডিলিট লজিক"""
    def delete():
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Timer(delay, delete).start()

def animated_loading(chat_id, message_id):
    """Premium Ultra-Motion Animation Frames"""
    frames = [
        "🌐 <b>Connecting to AI Node...</b>",
        "📡 <b>Scanning Neural Networks...</b>",
        "🧠 <b>Analyzing Language Syntax...</b>",
        "⚡ <b>Translating semantic flow...</b>",
        "✨ <b>Applying Premium Polish...</b>",
        "✅ <b>Done! Generating Result...</b>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.4)
        except:
            break

# --- KEYBOARDS ---
def get_start_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✨ Official Channel", url=DEV_URL)
    btn2 = types.InlineKeyboardButton("🌐 Website", url=BLOG_URL)
    btn3 = types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    btn4 = types.InlineKeyboardButton("📜 Help", callback_data="help")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    return markup

def get_language_selection_markup():
    langs = [
        ("English 🇺🇸", "en"), ("Bengali 🇧🇩", "bn"), ("Hindi 🇮🇳", "hi"),
        ("Arabic 🇸🇦", "ar"), ("Spanish 🇪🇸", "es"), ("French 🇫🇷", "fr"),
        ("Russian 🇷🇺", "ru"), ("Chinese 🇨🇳", "zh"), ("Japanese 🇯🇵", "ja")
    ]
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(name.split()[0], callback_data=f"set_lang_{code}") for name, code in langs]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in user_banned:
        bot.reply_to(message, "🚫 <b>Access Denied!</b>\nYou have been banned from using our services.")
        return

    user_list.add(user_id)
    
    if not is_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Verify & Start", callback_data="verify"))
        
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"👋 <b>Hello {message.from_user.first_name}!</b>\n\n"
                               f"To use this premium translator, you must be a member of our official channel.\n\n"
                               f"Please join then click verify.",
                       reply_markup=markup)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>Welcome to {BOT_NAME} v2.0</b>\n\n"
                           f"The fastest AI-driven translator on Telegram. Experience smooth and accurate translations.\n\n"
                           f"🔹 <b>Target Language:</b> {user_target_lang[user_id].upper()}\n"
                           f"🔹 <b>Auto-Detection:</b> Active\n\n"
                           f"<i>Simply send your text or use commands like /bn /hi</i>",
                   reply_markup=get_start_markup())

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    user_id = call.from_user.id
    if user_id in user_banned:
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return

    if call.data == "verify":
        if is_joined(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)

    elif call.data == "settings":
        bot.edit_message_caption("⚙️ <b>Settings Panel</b>\n\nSelect your default target language for auto-translation:",
                                 call.message.chat.id, call.message.message_id,
                                 reply_markup=get_language_selection_markup())

    elif call.data.startswith("set_lang_"):
        lang_code = call.data.split("_")[-1]
        user_target_lang[user_id] = lang_code
        bot.answer_callback_query(call.id, f"✅ Language set to {lang_code.upper()}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    elif call.data == "help":
        help_text = (
            "📜 <b>User Guide</b>\n\n"
            "1️⃣ <b>Auto Mode:</b> Just send any text, I will detect the language and translate it to your target language.\n"
            "2️⃣ <b>Direct Command:</b> Use <code>/bn Hello</code> to translate to Bengali directly.\n"
            "3️⃣ <b>History:</b> Your last 5 translations are saved locally.\n\n"
            "<b>Contact:</b> @Dark_Unkwon_ModZ"
        )
        bot.edit_message_caption(help_text, call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION CORE ---
def perform_translation(message, input_text, source='auto'):
    user_id = message.from_user.id
    target = user_target_lang[user_id]

    if is_rate_limited(user_id):
        bot.reply_to(message, "⚠️ <b>Cooldown!</b> Please wait a few seconds.")
        return

    status_msg = bot.reply_to(message, "🌀 <b>Initializing...</b>")
    
    try:
        # Start Smooth Animation
        animated_loading(message.chat.id, status_msg.message_id)

        translated = GoogleTranslator(source=source, target=target).translate(input_text)
        
        # Detection logic
        try:
            detected_lang = detect(input_text).upper()
        except:
            detected_lang = "Unknown"

        final_response = (
            f"📥 <b>Input ({detected_lang}):</b>\n<code>{input_text}</code>\n\n"
            f"📤 <b>Result ({target.upper()}):</b>\n<code>{translated}</code>\n\n"
            f"✨ <i>Translated by @Dark_Unkwon_ModZ</i>"
        )
        
        bot.edit_message_text(final_response, message.chat.id, status_msg.message_id)
        # auto_delete_message(message.chat.id, status_msg.message_id, 120) # চাইলে ডিলিট করতে পারেন

    except Exception as e:
        bot.edit_message_text(f"❌ <b>Error:</b> Could not translate. Please try again.", message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['bn', 'hi', 'ar', 'es', 'fr', 'ru', 'zh', 'ja', 'en'])
def manual_translation(message):
    if not is_joined(message.from_user.id) or message.from_user.id in user_banned: return
    
    cmd = message.text.split()[0][1:]
    input_text = message.text.replace(f"/{cmd}", "").strip()
    
    if not input_text:
        bot.reply_to(message, "❌ Please provide text! Example: <code>/bn Hello</code>")
        return

    # Temporary set target to command for this request
    old_target = user_target_lang[message.from_user.id]
    user_target_lang[message.from_user.id] = cmd
    perform_translation(message, input_text)
    user_target_lang[message.from_user.id] = old_target

@bot.message_handler(content_types=['text'])
def auto_detect_translation(message):
    if message.text.startswith('/') or not is_joined(message.from_user.id) or message.from_user.id in user_banned:
        return
    perform_translation(message, message.text)

# --- ADVANCED ADMIN SYSTEM ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    panel = (
        f"👑 <b>Premium Admin Dashboard</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Stats:</b>\n"
        f"• Total Users: {len(user_list)}\n"
        f"• Banned Users: {len(user_banned)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 <b>Control Commands:</b>\n"
        f"• <code>/broadcast [msg]</code> - Send global msg\n"
        f"• <code>/ban [ID]</code> - Ban a user\n"
        f"• <code>/unban [ID]</code> - Unban user\n"
        f"• <code>/status</code> - Detailed report\n"
    )
    bot.reply_to(message, panel)

@bot.message_handler(commands=['ban'], func=lambda m: m.from_user.id == ADMIN_ID)
def ban_user(message):
    try:
        uid = int(message.text.split()[1])
        user_banned.add(uid)
        bot.reply_to(message, f"🚫 User {uid} has been banned.")
        notify_manager(f"Admin banned user: {uid}")
    except:
        bot.reply_to(message, "Usage: /ban 12345678")

@bot.message_handler(commands=['unban'], func=lambda m: m.from_user.id == ADMIN_ID)
def unban_user(message):
    try:
        uid = int(message.text.split()[1])
        user_banned.discard(uid)
        bot.reply_to(message, f"✅ User {uid} has been unbanned.")
    except:
        bot.reply_to(message, "Usage: /unban 12345678")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast(message):
    if len(message.text.split()) < 2: return
    text = message.text.split(None, 1)[1]
    count = 0
    for uid in list(user_list):
        try:
            bot.send_message(uid, f"📢 <b>Announcement:</b>\n\n{text}")
            count += 1
            time.sleep(0.1) # Flood prevention
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast finished. Sent to {count} users.")

# --- LOGGING ---
def notify_manager(action):
    log_text = (
        f"📝 <b>Log Entry</b>\n"
        f"Action: {action}\n"
        f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    try:
        bot.send_message(LOG_CHANNEL, log_text)
    except:
        pass

if __name__ == "__main__":
    print(f"🚀 {BOT_NAME} is Online!")
    notify_manager("Bot Server Started Successfully")
    bot.infinity_polling()
