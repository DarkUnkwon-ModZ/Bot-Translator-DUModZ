import telebot
import time
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Accuracy নিশ্চিত করতে seed সেট করা
DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"
LOG_CHANNEL = "@dumodzbotmanager"
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- FUNCTIONS ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(REQ_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def animated_loader(chat_id, message_id, text_list):
    """মেসেজ এডিট করে এনিমেশন তৈরি করার ফাংশন"""
    for frame in text_list:
        try:
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.5)
        except:
            break

# --- WELCOME & START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/Dark_Unkwon_ModZ")
        btn2 = types.InlineKeyboardButton("✅ Verify & Start", callback_data="verify")
        markup.add(btn1)
        markup.add(btn2)
        
        bot.send_photo(message.chat.id, BANNER_URL, 
                       caption=f"⚠️ <b>Access Denied!</b>\n\nHi {message.from_user.first_name}, you must join our channel to use this premium bot.",
                       reply_markup=markup)
        return

    # Welcome Animation
    welcome_msg = bot.send_message(message.chat.id, "⚡")
    animated_loader(message.chat.id, welcome_msg.message_id, ["⚡ Boooting...", "🚀 Launching...", "💎 Professional UI Loaded!"])
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🌐 Website", url="https://darkunkwon-modz.blogspot.com"),
        types.InlineKeyboardButton("💬 Support", url="https://t.me/Dark_Unkwon_ModZ"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        types.InlineKeyboardButton("📜 Help", callback_data="help")
    )
    
    bot.edit_message_text(f"👋 <b>Welcome to {BOT_NAME}</b>\n\n"
                         "I am your AI-powered advanced translator.\n\n"
                         "✨ <b>Auto-Detect:</b> Just send any text.\n"
                         "✨ <b>Precision:</b> 100% Accuracy.\n\n"
                         "Developer: <a href='https://t.me/Dark_Unkwon_ModZ'>𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭</a>",
                         message.chat.id, welcome_msg.message_id, reply_markup=markup, disable_web_page_preview=True)

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "verify":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified Successfully!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)
            
    elif call.data == "help":
        help_text = (
            "📖 <b>How to use the Bot:</b>\n\n"
            "1️⃣ <b>Auto-Translate:</b> Just send any language text, I will convert it to English automatically.\n"
            "2️⃣ <b>Manual Commands:</b>\n"
            "• <code>/bn [text]</code> - Translate to English (from Bengali)\n"
            "• <code>/hi [text]</code> - Translate to English (from Hindi)\n"
            "• <code>/ar [text]</code> - Translate to English (from Arabic)\n\n"
            "3️⃣ <b>Settings:</b> Manage your translation preferences."
        )
        bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, 
                             reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_start")))

    elif call.data == "back_start":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome(call.message)

# --- TRANSLATION LOGIC ---
@bot.message_handler(commands=['bn', 'hi', 'in', 'ar', 'fr', 'es'])
def manual_translate(message):
    if not is_subscribed(message.from_user.id): return
    
    text = message.text.split(None, 1)
    if len(text) < 2:
        bot.reply_to(message, "❌ Please provide text! Example: <code>/bn কেমন আছো?</code>")
        return
    
    status_msg = bot.reply_to(message, "🔍 <i>Analyzing source language...</i>")
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text[1])
        animated_loader(message.chat.id, status_msg.message_id, ["🔄 Translating...", "✨ Refining Text...", "✅ Done!"])
        bot.edit_message_text(f"💎 <b>Translated to English:</b>\n\n<code>{translated}</code>", 
                             message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

@bot.message_handler(func=lambda message: True)
def auto_detect_translate(message):
    if not is_subscribed(message.from_user.id): return
    if message.text.startswith('/'): return

    status_msg = bot.reply_to(message, "📡 <b>Auto-Detecting...</b>")
    try:
        # Language Detection
        src_lang = detect(message.text)
        translated = GoogleTranslator(source='auto', target='en').translate(message.text)
        
        # UI Animation
        frames = ["📡 Detecting...", f"📝 Source: {src_lang.upper()}", "🪄 Converting to EN...", "✅ Finished!"]
        animated_loader(message.chat.id, status_msg.message_id, frames)
        
        bot.edit_message_text(f"🌐 <b>Auto Translation ({src_lang.upper()} ➜ EN)</b>\n\n<code>{translated}</code>", 
                             message.chat.id, status_msg.message_id)
    except:
        bot.edit_message_text("❌ Could not translate. Try again.", message.chat.id, status_msg.message_id)

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['admin'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_panel(message):
    bot.reply_to(message, f"👑 <b>Admin Panel</b>\n\nTotal Stats: Active\n\nUse <code>/broadcast [text]</code> to send message.")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast(message):
    # This is a placeholder for broadcast logic
    bot.reply_to(message, "✅ Broadcast started!")

# --- STARTUP LOGGING ---
def notify_start():
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 <b>Bot Restarted!</b>\n\n<b>Name:</b> {BOT_NAME}\n<b>Time:</b> {time.ctime()}\n<b>Status:</b> Live 🟢")
    except:
        pass

if __name__ == "__main__":
    print("Bot is running...")
    notify_start()
    bot.infinity_polling()
