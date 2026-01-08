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
user_target_lang = defaultdict(lambda: 'en')  # Default: English
user_history = defaultdict(lambda: deque(maxlen=5))  # Last 5 translations
last_request_time = {}  # For rate limiting

# --- RATE LIMITING ---
REQUEST_COOLDOWN = 5  # seconds

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

def auto_delete_message(chat_id, message_id, delay=10):
    """Auto-delete message after delay (for clean UX)"""
    def delete():
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    timer = threading.Timer(delay, delete)
    timer.daemon = True
    timer.start()

def animated_loading(chat_id, message_id, text_frames, final_delay=0.8):
    for i, frame in enumerate(text_frames):
        try:
            bot.edit_message_text(frame, chat_id, message_id, disable_web_page_preview=True)
            time.sleep(0.5 if i < len(text_frames) - 1 else final_delay)
        except:
            break

# --- WELCOME SCREEN DESIGN ---
def get_start_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭", url=DEV_URL)
    btn2 = types.InlineKeyboardButton("🌐 Website", url=BLOG_URL)
    btn3 = types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    btn4 = types.InlineKeyboardButton("📜 Help", callback_data="help")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    return markup

def get_language_selection_markup():
    langs = [
        ("English", "en"), ("Bengali", "bn"), ("Hindi", "hi"),
        ("Arabic", "ar"), ("Spanish", "es"), ("French", "fr"),
        ("Russian", "ru"), ("Chinese", "zh"), ("Japanese", "ja")
    ]
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=f"set_lang_{code}") for name, code in langs]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
    return markup

def get_history_markup(user_id):
    history = user_history[user_id]
    if not history:
        return None
    markup = types.InlineKeyboardMarkup()
    for i, (src, trans) in enumerate(history, 1):
        markup.add(types.InlineKeyboardButton(f"📌 #{i}: {src[:15]}...", callback_data=f"view_hist_{i}"))
    markup.add(types.InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in user_banned:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    user_list.add(user_id)
    
    if not is_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Verify Connection", callback_data="verify"))
        
        sent = bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"⚠️ <b>Access Restricted!</b>\n\nDear {message.from_user.first_name},\nYou must join our official channel to access this premium translator.",
                       reply_markup=markup)
        auto_delete_message(message.chat.id, sent.message_id, delay=60)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>Welcome to {BOT_NAME}</b>\n\n"
                           f"I am a professional AI-based high-speed translator.\n\n"
                           f"✨ <b>Features:</b>\n"
                           f"• Auto Language Detection\n"
                           f"• 100+ Language Support\n"
                           f"• Translation History\n"
                           f"• Ultra-Smooth Animations\n\n"
                           f"<i>Send any text to start auto-translating!</i>",
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
            msg = bot.edit_message_caption("🔄 <b>Verifying...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ <b>Verified Successfully!</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Verification Failed! Join the channel first.", show_alert=True)

    elif call.data == "settings":
        current_lang = user_target_lang[user_id]
        lang_names = {
            'en': 'English', 'bn': 'Bengali', 'hi': 'Hindi',
            'ar': 'Arabic', 'es': 'Spanish', 'fr': 'French'
        }
        current_name = lang_names.get(current_lang, current_lang.upper())
        bot.edit_message_caption(
            f"⚙️ <b>Advanced Settings</b>\n\n"
            f"🎯 <b>Target Language:</b> {current_name}\n"
            f"⏱️ <b>Rate Limit:</b> 1 req / {REQUEST_COOLDOWN}s\n"
            f"💾 <b>History:</b> Enabled (Last 5)\n\n"
            f"👉 Tap below to change target language:",
            call.message.chat.id, call.message.message_id,
            reply_markup=get_language_selection_markup()
        )

    elif call.data.startswith("set_lang_"):
        lang_code = call.data.split("_")[-1]
        user_target_lang[user_id] = lang_code
        bot.answer_callback_query(call.id, f"✅ Target language set to {lang_code.upper()}", show_alert=False)
        # Return to home
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    elif call.data == "help":
        help_txt = (
            "📜 <b>Premium Translator Guide</b>\n\n"
            "1️⃣ <b>Auto Mode:</b> Send any text → auto-detect & translate to your target language.\n"
            "2️⃣ <b>Manual Commands:</b>\n"
            "   • <code>/bn Hello</code> → Bengali\n"
            "   • <code>/hi नमस्ते</code> → Hindi\n"
            "   • <code>/ar مرحبا</code> → Arabic\n"
            "3️⃣ <b>Voice Messages:</b> Not supported yet (coming soon!)\n"
            "4️⃣ <b>History:</b> View past translations in Settings.\n\n"
            "<b>💡 Pro Tip:</b> Use /start anytime to reload menu!"
        )
        bot.edit_message_caption(help_txt, call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    elif call.data == "clear_history":
        user_history[user_id].clear()
        bot.answer_callback_query(call.id, "🗑️ History cleared!", show_alert=True)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION CORE ---
def perform_translation(message, input_text, source='auto'):
    user_id = message.from_user.id
    target = user_target_lang[user_id]

    if is_rate_limited(user_id):
        bot.reply_to(message, f"⏳ Please wait {REQUEST_COOLDOWN} seconds between requests.")
        return

    status_msg = bot.reply_to(message, "📡")
    try:
        # Ultra-motion animation
        frames = [
            "🌌 <b>Connecting to AI Servers...</b>",
            "🔍 <b>Scanning Linguistic Patterns...</b>",
            "🧠 <b>Engaging Neural Translator v3.2...</b>",
            "⚡ <b>Optimizing Semantic Flow...</b>",
            "💎 <b>Finalizing Premium Output...</b>",
            "✅ <b>Translation Complete!</b>"
        ]
        animated_loading(message.chat.id, status_msg.message_id, frames)

        translated = GoogleTranslator(source=source, target=target).translate(input_text)
        detected = detect(input_text) if source == 'auto' else source

        # Save to history
        user_history[user_id].append((input_text, translated))

        final_text = (
            f"🌐 <b>AI-Powered Translation</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected.upper()}):</b>\n<code>{input_text[:80]}{'' if len(input_text) <= 80 else '...'}</code>\n\n"
            f"📤 <b>Output ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(final_text, message.chat.id, status_msg.message_id)
        auto_delete_message(message.chat.id, status_msg.message_id, delay=30)

    except Exception as e:
        error_msg = "❌ Translation failed. Try again or check input."
        if "No support" in str(e):
            error_msg = "⚠️ This language pair is not supported by Google Translate."
        bot.edit_message_text(error_msg, message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['bn', 'hi', 'in', 'ar', 'es', 'fr', 'ru', 'zh', 'ja'])
def manual_translation(message):
    if not is_joined(message.from_user.id) or message.from_user.id in user_banned:
        return
    
    cmd = message.text.split()[0][1:]
    lang_map = {'in': 'hi'}  # Fix common alias
    source_lang = lang_map.get(cmd, cmd)
    input_text = message.text.replace(f"/{cmd}", "").strip()
    
    if not input_text:
        bot.reply_to(message, "❌ <b>Empty text!</b> Please provide text after command.")
        return

    perform_translation(message, input_text, source=source_lang)

@bot.message_handler(content_types=['text'])
def auto_detect_translation(message):
    if message.text.startswith('/'):
        return
    if not is_joined(message.from_user.id) or message.from_user.id in user_banned:
        return
    perform_translation(message, message.text, source='auto')

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    bot.reply_to(message, "🎙️ <b>Voice Translation</b>\n\nSorry! Voice-to-text is coming soon in v2.0!\n\n👉 Please send text for now.")

# --- ADMIN SYSTEM (Enhanced) ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    bot.reply_to(message, 
                 f"👑 <b>Master Admin Panel</b>\n\n"
                 f"👤 <b>Name:</b> Dark Unknown\n"
                 f"🆔 <b>Chat ID:</b> <code>{ADMIN_ID}</code>\n\n"
                 f"📊 <b>Active Users:</b> {len(user_list)}\n"
                 f"🚫 <b>Banned Users:</b> {len(user_banned)}\n\n"
                 "<b>Commands:</b>\n"
                 "/stats - User statistics\n"
                 "/broadcast [msg] - Send to all\n"
                 "/ban [user_id] - Ban user\n"
                 "/unban [user_id] - Unban user\n"
                 "/user_info [id] - Get user details\n"
                 "/clear_all_hist - Clear all histories")

@bot.message_handler(commands=['ban'], func=lambda m: m.from_user.id == ADMIN_ID)
def ban_user(message):
    try:
        user_id = int(message.text.split()[1])
        user_banned.add(user_id)
        bot.reply_to(message, f"🚫 User <code>{user_id}</code> banned successfully!")
        notify_manager(f"User {user_id} banned by admin")
    except:
        bot.reply_to(message, "UsageId: /ban [user_id]")

@bot.message_handler(commands=['unban'], func=lambda m: m.from_user.id == ADMIN_ID)
def unban_user(message):
    try:
        user_id = int(message.text.split()[1])
        user_banned.discard(user_id)
        bot.reply_to(message, f"✅ User <code>{user_id}</code> unbanned!")
    except:
        bot.reply_to(message, "UsageId: /unban [user_id]")

@bot.message_handler(commands=['user_info'], func=lambda m: m.from_user.id == ADMIN_ID)
def user_info(message):
    try:
        user_id = int(message.text.split()[1])
        joined = "✅" if is_joined(user_id) else "❌"
        banned = "🚫 BANNED" if user_id in user_banned else "🟢 Active"
        history_count = len(user_history[user_id])
        bot.reply_to(message, 
                     f"👤 <b>User Info</b>\n"
                     f"ID: <code>{user_id}</code>\n"
                     f"Channel: {joined}\n"
                     f>Status: {banned}\n"
                     f"History: {history_count} entries")
    except:
        bot.reply_to(message, "UsageId: /user_info [user_id]")

@bot.message_handler(commands=['clear_all_hist'], func=lambda m: m.from_user.id == ADMIN_ID)
def clear_all_hist(message):
    user_history.clear()
    bot.reply_to(message, "🗑️ All translation histories cleared!")

@bot.message_handler(commands=['stats'], func=lambda m: m.from_user.id == ADMIN_ID)
def stats(message):
    bot.reply_to(message,
                 f"📊 <b>Bot Statistics</b>\n\n"
                 f"👥 Total Users: {len(user_list)}\n"
                 f"🚫 Banned: {len(user_banned)}\n"
                 f"💬 Avg. History/User: {sum(len(h) for h in user_history.values()) / max(len(user_history), 1):.1f}")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast_msg(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "UsageId: /broadcast [message]")
        return
    msg = message.text.split(None, 1)[1]
    success = 0
    for user in list(user_list):  # Copy to avoid runtime modification
        try:
            bot.send_message(user, f"📣 <b>Broadcast From Admin:</b>\n\n{msg}")
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {success} users!")

# --- NOTIFICATION & LOGGING ---
def notify_manager(action_type):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = (
        f"🔔 <b>Bot Update Alert!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Bot Name:</b> {BOT_NAME}\n"
        f"🛠 <b>Action:</b> {action_type}\n"
        f"⏰ <b>Time:</b> {now}\n"
        f"📡 <b>Status:</b> 100% Operational\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.send_message(LOG_CHANNEL, log_text)
    except:
        pass

if __name__ == "__main__":
    print(f"🚀 Starting {BOT_NAME} (Premium Edition)...")
    notify_manager("Bot Started/Restarted")
    bot.infinity_polling()
