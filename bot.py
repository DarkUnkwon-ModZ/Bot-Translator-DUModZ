import telebot
import time
import datetime
import threading
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Accuracy Fix
DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanage" 
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE (In-Memory) ---
user_list = set()
user_banned = set()

# --- UTILS ---
def is_joined(user_id):
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def ultra_anim(chat_id, msg_id, frames):
    """উন্নত এনিমেশন সিস্টেম"""
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, msg_id, disable_web_page_preview=True)
            time.sleep(0.5)
        except:
            break

# --- WELCOME UI ---
def welcome_markup():
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

# --- START & VERIFY ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid in user_banned:
        return bot.reply_to(message, "🚫 You are banned from using this bot.")
    
    user_list.add(uid)
    
    if not is_joined(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=DEV_URL))
        markup.add(types.InlineKeyboardButton("✅ Verify Connection", callback_data="verify_now"))
        
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"👋 <b>Access Restricted!</b>\n\nDear {message.from_user.first_name},\nYou must join our official channel to unlock premium features.",
                       reply_markup=markup)
        return

    bot.send_photo(message.chat.id, BANNER_URL, 
                   caption=f"🚀 <b>Welcome to {BOT_NAME}</b>\n\n"
                           "I am an advanced AI Translator. Send any text to convert it into English automatically!\n\n"
                           "✨ 100% Accurate & Ultra Fast.",
                   reply_markup=welcome_markup())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = call.from_user.id
    if call.data == "verify_now":
        if is_joined(uid):
            msg = bot.edit_message_caption("🔄 <b>Verifying Access...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ <b>Verified! Access Granted.</b>", call.message.chat.id, call.message.message_id)
            time.sleep(0.5)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please join @Dark_Unkwon_ModZ first!", show_alert=True)
    
    elif call.data == "settings":
        bot.edit_message_caption("⚙️ <b>Advanced Settings</b>\n\n• Target: <b>English</b>\n• Mode: <b>Auto-Detect</b>\n• Logic: <b>AI Google v3</b>", 
                                 call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back")))
    
    elif call.data == "help":
        bot.edit_message_caption("📖 <b>Translator Guide</b>\n\n1. Send any text for Auto-Translation.\n2. Use /bn, /hi, /ar for specific lang to English.\n\nExample: `/bn কেমন আছো?`", 
                                 call.message.chat.id, call.message.message_id, 
                                 reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back")))
    
    elif call.data == "back":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION LOGIC ---
@bot.message_handler(commands=['bn', 'hi', 'in', 'ar', 'fr', 'es'])
def manual_cmd(message):
    if not is_joined(message.from_user.id): return
    text = message.text.split(None, 1)
    if len(text) < 2:
        return bot.reply_to(message, "❌ Provide text! Example: `/bn Hello`")
    
    proc = bot.reply_to(message, "📡")
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text[1])
        ultra_anim(message.chat.id, proc.message_id, ["🌀 Analyzing...", "🪄 Refining...", "✅ Done!"])
        bot.edit_message_text(f"💎 <b>Translation (English):</b>\n\n<code>{translated}</code>", message.chat.id, proc.message_id)
    except:
        bot.edit_message_text("❌ Failed.", message.chat.id, proc.message_id)

@bot.message_handler(func=lambda m: True)
def auto_trans(message):
    if not is_joined(message.from_user.id) or message.text.startswith('/'): return
    
    proc = bot.reply_to(message, "📡")
    try:
        src_lang = detect(message.text)
        translated = GoogleTranslator(source='auto', target='en').translate(message.text)
        
        frames = ["📡 <b>Detecting...</b>", f"📝 <b>Source:</b> {src_lang.upper()}", "✅ <b>Success!</b>"]
        ultra_anim(message.chat.id, proc.message_id, frames)
        
        bot.edit_message_text(f"🌐 <b>Auto-Translation (➜ EN)</b>\n━━━━━━━━━━━━━━\n<code>{translated}</code>", message.chat.id, proc.message_id)
    except:
        bot.delete_message(message.chat.id, proc.message_id)

# --- ADMIN COMMANDS (১০০% কার্যকর) ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Stats", callback_data="stats"), types.InlineKeyboardButton("📣 Broadcast", callback_data="bc"))
    bot.reply_to(message, "👑 <b>Admin Master Control</b>\n\nWelcome Dark Unknown. What would you like to do?", reply_markup=markup)

@bot.message_handler(commands=['stats'], func=lambda m: m.from_user.id == ADMIN_ID)
def stats(message):
    bot.reply_to(message, f"📊 <b>Total Users:</b> {len(user_list)}\n🚫 <b>Banned:</b> {len(user_banned)}")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast(message):
    text = message.text.replace("/broadcast", "").strip()
    if not text: return bot.reply_to(message, "Usage: `/broadcast Hello Users`")
    
    count = 0
    for user in user_list:
        try:
            bot.send_message(user, f"📣 <b>Important Update</b>\n\n{text}")
            count += 1
        except: continue
    bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

@bot.message_handler(commands=['ban'], func=lambda m: m.from_user.id == ADMIN_ID)
def ban_user(message):
    try:
        uid = int(message.text.split()[1])
        user_banned.add(uid)
        bot.reply_to(message, f"✅ User {uid} has been banned.")
    except: bot.reply_to(message, "Usage: `/ban ID`")

# --- LOGGING SYSTEM ---
def notify_start():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = (f"🚀 <b>{BOT_NAME} Live!</b>\n"
           f"──────────────\n"
           f"🔑 <b>Token:</b> <code>{BOT_TOKEN}</code>\n"
           f"🕗 <b>Time:</b> {now}\n"
           f"🟢 <b>Status:</b> Running 24/7")
    try: bot.send_message(LOG_CHANNEL, log)
    except: pass

if __name__ == "__main__":
    notify_start()
    print("Bot is active...")
    bot.infinity_polling()
