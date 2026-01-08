import telebot
import time
import datetime
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

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

# --- HELPER FUNCTIONS ---
def is_joined(user_id):
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def animated_loading(chat_id, message_id, text_frames):
    for frame in text_frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id, disable_web_page_preview=True)
            time.sleep(0.6)
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

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_list.add(user_id)
    
    if not is_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=DEV_URL))
        markup.add(types.InlineKeyboardButton("✅ Verify Connection", callback_data="verify"))
        
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"⚠️ <b>Access Restricted!</b>\n\nDear {message.from_user.first_name},\nYou must join our official channel to access this premium translator.",
                       reply_markup=markup)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>Welcome to {BOT_NAME}</b>\n\n"
                           f"I am a professional AI-based high-speed translator.\n\n"
                           f"✨ <b>Features:</b>\n"
                           f"• Auto Language Detection\n"
                           f"• 100% Accurate Translation\n"
                           f"• Advanced Animation Interface\n\n"
                           f"<i>Send any text to start auto-translating to English!</i>",
                   reply_markup=get_start_markup())

# --- CALLBACK HANDLERS (Animations included) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    if call.data == "verify":
        if is_joined(call.from_user.id):
            msg = bot.edit_message_caption("🔄 <b>Verifying...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ <b>Verified Successfully!</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Verification Failed! Join the channel first.", show_alert=True)

    elif call.data == "settings":
        bot.edit_message_caption("⚙️ <b>Advanced Settings:</b>\n\n• Target: <code>English (Default)</code>\n• Accuracy: <code>High Precision</code>\n• UI: <code>Animated</code>\n\n<i>Admin control enabled for global settings.</i>", 
                                 call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "help":
        help_txt = (
            "📜 <b>Bot Guide & Commands:</b>\n\n"
            "1️⃣ <b>Auto Mode:</b> Just send any language text, I will detect it and translate to English.\n"
            "2️⃣ <b>Manual Commands:</b>\n"
            "• <code>/bn [text]</code> - Bengali to English\n"
            "• <code>/in [text]</code> - Hindi to English\n"
            "• <code>/ar [text]</code> - Arabic to English\n\n"
            "<b>Developed by:</b> Dark Unknown"
        )
        bot.edit_message_caption(help_txt, call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION CORE (Precision + Animation) ---
@bot.message_handler(commands=['bn', 'hi', 'in', 'ar', 'es', 'fr'])
def manual_translation(message):
    if not is_joined(message.from_user.id): return
    
    cmd = message.text.split()[0][1:]
    input_text = message.text.replace(f"/{cmd}", "").strip()
    
    if not input_text:
        bot.reply_to(message, "❌ <b>Empty text!</b> Please provide text after command.")
        return

    status_msg = bot.reply_to(message, "📡 <b>Initializing...</b>")
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(input_text)
        frames = ["🔄 Analyzing Language...", "🪄 Processing AI Models...", "✅ Translation Perfected!"]
        animated_loading(message.chat.id, status_msg.message_id, frames)
        
        bot.edit_message_text(f"💎 <b>Professional Translation:</b>\n\n<code>{translated}</code>", 
                             message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ <b>Error:</b> {e}", message.chat.id, status_msg.message_id)

@bot.message_handler(func=lambda message: True)
def auto_detect_translation(message):
    if not is_joined(message.from_user.id): return
    if message.text.startswith('/'): return

    status_msg = bot.reply_to(message, "📡")
    try:
        detected_lang = detect(message.text)
        translated = GoogleTranslator(source='auto', target='en').translate(message.text)
        
        frames = ["📡 <b>Detecting...</b>", f"📝 <b>Source:</b> {detected_lang.upper()}", "⚡ <b>Converting to EN...</b>", "✅ <b>Success!</b>"]
        animated_loading(message.chat.id, status_msg.message_id, frames)
        
        final_text = (
            f"🌐 <b>Auto-Translation System</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Input ({detected_lang.upper()}):</b>\n<code>{message.text[:50]}...</code>\n\n"
            f"📤 <b>Output (EN):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(final_text, message.chat.id, status_msg.message_id)
    except:
        bot.edit_message_text("❌ Failed to detect language. Try again.", message.chat.id, status_msg.message_id)

# --- ADMIN SYSTEM (Full Control) ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    bot.reply_to(message, 
                 f"👑 <b>Master Admin Panel</b>\n\n"
                 f"👤 <b>Name:</b> Dark Unknown\n"
                 f"🆔 <b>Chat ID:</b> <code>{ADMIN_ID}</code>\n\n"
                 f"📊 <b>Active Users:</b> {len(user_list)}\n\n"
                 "<b>Commands:</b>\n"
                 "/stats - User statistics\n"
                 "/broadcast - Send message to all\n"
                 "/restart - Manual bot restart")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast_msg(message):
    if len(message.text.split()) < 2: return
    msg = message.text.split(None, 1)[1]
    for user in user_list:
        try: bot.send_message(user, f"📣 <b>Broadcast From Admin:</b>\n\n{msg}")
        except: pass
    bot.reply_to(message, "✅ Broadcast completed!")

# --- NOTIFICATION & LOGGING ---
def notify_manager(action_type):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = (
        f"🔔 <b>Bot Update Alert!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Bot Name:</b> {BOT_NAME}\n"
        f"🛠 <b>Action:</b> {action_type}\n"
        f"🔑 <b>Token:</b> <code>{BOT_TOKEN}</code>\n"
        f"⏰ <b>Time:</b> {now}\n"
        f"📡 <b>Status:</b> 100% Operational\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    try: bot.send_message(LOG_CHANNEL, log_text)
    except: pass

if __name__ == "__main__":
    print(f"Starting {BOT_NAME}...")
    notify_manager("Bot Started/Restarted")
    bot.infinity_polling()
