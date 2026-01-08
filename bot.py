import telebot
import time
import datetime
import threading
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from collections import defaultdict, deque

DetectorFactory.seed = 0

# --- CONFIGURATION ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"          # ✅ CORRECTED
LOG_CHANNEL = "@dumodzbotmanager"         # ✅ CORRECTED
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"
BLOG_URL = "https://darkunkwon-modz.blogspot.com"
DEV_URL = "https://t.me/Dark_Unkwon_ModZ"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE ---
user_list = set()
user_banned = set()
user_target_lang = defaultdict(lambda: 'en')
user_history = defaultdict(lambda: deque(maxlen=5))
last_request_time = {}
REQUEST_COOLDOWN = 5

# --- HELPERS ---
def is_joined(user_id):
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"[JOIN CHECK ERROR] {e}")
        return False

def auto_delete(chat_id, msg_id, delay=15):
    def _del():
        try: bot.delete_message(chat_id, msg_id)
        except: pass
    threading.Timer(delay, _del).start()

def animate_edit(chat_id, msg_id, frames, delay=0.7):
    for i, txt in enumerate(frames):
        try:
            bot.edit_message_text(txt, chat_id, msg_id, disable_web_page_preview=True)
            time.sleep(delay if i < len(frames)-1 else 0.5)
        except: break

def is_admin(uid): return uid == ADMIN_ID

# --- WELCOME SCREEN (BEAUTIFUL DESIGN) ---
def get_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭", url=DEV_URL))
    markup.add(
        types.InlineKeyboardButton("🌐 Official Blog", url=BLOG_URL),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    markup.add(types.InlineKeyboardButton("📜 User Guide", callback_data="help"))
    return markup

# --- START HANDLER ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid in user_banned:
        bot.reply_to(message, "🚫 You are banned.")
        return

    user_list.add(uid)

    if not is_joined(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/Dark_Unkwon_ModZ"))
        markup.add(types.InlineKeyboardButton("✅ Verify Now", callback_data="verify"))
        sent = bot.send_photo(
            message.chat.id,
            BANNER_URL,
            caption=(
                "🔐 <b>Security Verification Required!</b>\n\n"
                "To use this <b>Premium Translator Bot</b>, you must join our official channel.\n\n"
                "✨ Benefits of joining:\n"
                "• Exclusive updates\n• Bug fixes & new features\n• Priority support\n\n"
                "<i>Click 'Verify Now' after joining.</i>"
            ),
            reply_markup=markup
        )
        auto_delete(message.chat.id, sent.message_id, 60)
        return

    bot.send_photo(
        message.chat.id,
        BANNER_URL,
        caption=(
            f"🌟 <b>Welcome to {BOT_NAME}</b>!\n\n"
            f"🤖 Your AI-powered multilingual translator is ready!\n\n"
            f"✅ <b>Features:</b>\n"
            f"• Auto-detect 100+ languages\n"
            f"• Translate to your preferred language\n"
            f"• Save translation history\n"
            f"• Ultra-smooth animations\n\n"
            f"<i>Send any text to begin!</i>"
        ),
        reply_markup=get_main_markup()
    )

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda c: True)
def cb_handler(call):
    uid = call.from_user.id
    if uid in user_banned:
        bot.answer_callback_query(call.id, "🚫 Banned.", show_alert=True)
        return

    if call.data == "verify":
        if is_joined(uid):
            # Animated verification
            msg = bot.edit_message_caption("🔄 <b>Verifying membership...</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1.2)
            bot.edit_message_caption("✅ <b>Verified! Access granted.</b>", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)

    elif call.data == "settings":
        current = user_target_lang[uid]
        names = {'en':'English','bn':'Bengali','hi':'Hindi','ar':'Arabic','es':'Spanish','fr':'French'}
        name = names.get(current, current.upper())
        markup = types.InlineKeyboardMarkup(row_width=3)
        langs = [('EN','en'),('BN','bn'),('HI','hi'),('AR','ar'),('ES','es'),('FR','fr')]
        markup.add(*[types.InlineKeyboardButton(n, callback_data=f"lang_{c}") for n,c in langs])
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(
            f"⚙️ <b>Settings</b>\n🎯 Target: <code>{name}</code>\n⏱️ Cooldown: {REQUEST_COOLDOWN}s",
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )

    elif call.data.startswith("lang_"):
        code = call.data.split("_")[1]
        user_target_lang[uid] = code
        bot.answer_callback_query(call.id, f"✅ Language set to {code.upper()}", show_alert=False)
        start(call.message)

    elif call.data in ["help", "back_home"]:
        if call.data == "help":
            txt = (
                "📘 <b>How to Use</b>\n\n"
                "1️⃣ Send any text → auto-translate to your target language.\n"
                "2️⃣ Use commands:\n"
                "   • <code>/bn হ্যালো</code>\n"
                "   • <code>/hi नमस्ते</code>\n"
                "   • <code>/ar مرحبا</code>\n"
                "3️⃣ View history in Settings.\n\n"
                "<b>Need help?</b> Contact @Dark_Unkwon_ModZ"
            )
            bot.edit_message_caption(txt, call.message.chat.id, call.message.message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 Back", callback_data="back_home")
                )
            )
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)

# --- TRANSLATION ENGINE ---
@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'), content_types=['text'])
def auto_translate(message):
    uid = message.from_user.id
    if uid in user_banned or not is_joined(uid): return
    if is_rate_limited(uid): 
        bot.reply_to(message, f"⏳ Wait {REQUEST_COOLDOWN} sec between requests.")
        return

    status = bot.reply_to(message, "📡 Initializing...")
    try:
        frames = [
            "🌌 Connecting to neural servers...",
            "🔍 Detecting source language...",
            "🧠 Processing with AI v4.1...",
            "⚡ Optimizing translation...",
            "✅ Done! Finalizing..."
        ]
        animate_edit(message.chat.id, status.message_id, frames)

        src_text = message.text
        detected = detect(src_text)
        target = user_target_lang[uid]
        translated = GoogleTranslator(source='auto', target=target).translate(src_text)
        user_history[uid].append((src_text[:50], translated[:50]))

        result = (
            f"🌐 <b>Translation Complete</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📥 <b>From ({detected.upper()}):</b>\n<code>{src_text[:100]}{'' if len(src_text) <= 100 else '...'}</code>\n\n"
            f"📤 <b>To ({target.upper()}):</b>\n<code>{translated}</code>\n"
            f"━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(result, message.chat.id, status.message_id)
        auto_delete(message.chat.id, status.message_id, 30)
    except Exception as e:
        bot.edit_message_text("❌ Translation failed. Try again.", message.chat.id, status.message_id)

def is_rate_limited(uid):
    now = time.time()
    if uid in last_request_time and now - last_request_time[uid] < REQUEST_COOLDOWN:
        return True
    last_request_time[uid] = now
    return False

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'], func=lambda m: is_admin(m.from_user.id))
def admin_cmd(message):
    bot.reply_to(message, 
        "👑 <b>Admin Panel</b>\n"
        "Use /adminhelp to see all commands."
    )

@bot.message_handler(commands=['adminhelp'], func=lambda m: is_admin(m.from_user.id))
def admin_help(message):
    bot.reply_to(message,
        "🛠️ <b>Admin Commands</b>\n\n"
        "• /ban [id] – Ban user\n"
        "• /unban [id] – Unban user\n"
        "• /user_info [id]\n"
        "• /stats – Bot stats\n"
        "• /broadcast [msg]\n"
        "• /clear_hist – Clear all history"
    )

@bot.message_handler(commands=['ban','unban','user_info','stats','broadcast','clear_hist'], func=lambda m: is_admin(m.from_user.id))
def admin_router(message):
    cmd = message.text.split()[0][1:]
    if cmd == 'ban':
        try:
            uid = int(message.text.split()[1])
            user_banned.add(uid)
            bot.reply_to(message, f"🚫 Banned {uid}")
        except: bot.reply_to(message, "UsageId: /ban [user_id]")
    elif cmd == 'unban':
        try:
            uid = int(message.text.split()[1])
            user_banned.discard(uid)
            bot.reply_to(message, f"✅ Unbanned {uid}")
        except: bot.reply_to(message, "UsageId: /unban [user_id]")
    elif cmd == 'user_info':
        try:
            uid = int(message.text.split()[1])
            joined = "✅" if is_joined(uid) else "❌"
            status = "🚫 Banned" if uid in user_banned else "🟢 Active"
            hist = len(user_history[uid])
            bot.reply_to(message, f"👤 ID: <code>{uid}</code>\nChannel: {joined}\nStatus: {status}\nHistory: {hist}")
        except: bot.reply_to(message, "UsageId: /user_info [id]")
    elif cmd == 'stats':
        bot.reply_to(message, f"👥 Users: {len(user_list)}\n🚫 Banned: {len(user_banned)}")
    elif cmd == 'broadcast':
        if len(message.text.split()) < 2:
            bot.reply_to(message, "UsageId: /broadcast [msg]")
            return
        msg = message.text.split(' ', 1)[1]
        sent = 0
        for u in list(user_list):
            try:
                bot.send_message(u, f"📣 <b>Admin Broadcast</b>\n\n{msg}")
                sent += 1
            except: pass
        bot.reply_to(message, f"✅ Sent to {sent} users.")
    elif cmd == 'clear_hist':
        user_history.clear()
        bot.reply_to(message, "🗑️ All histories cleared.")

# --- LOGGING TO MANAGER CHANNEL ---
def notify_manager(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = (
        f"🔔 <b>Bot Status Update</b>\n"
        f"──────────────\n"
        f"🤖 <b>Bot:</b> {BOT_NAME}\n"
        f"🔑 <b>Token:</b> <code>{BOT_TOKEN}</code>\n"
        f"🕗 <b>Time:</b> {now}\n"
        f"📌 <b>Event:</b> {event}\n"
        f"🟢 <b>Status:</b> LIVE & OPERATIONAL\n"
        f"──────────────"
    )
    try:
        bot.send_message(LOG_CHANNEL, log_msg)
    except Exception as e:
        print(f"[LOG FAILED] {e}")

if __name__ == "__main__":
    print("🚀 Starting Translator Bot (Premium Edition)...")
    notify_manager("🟢 Bot Started / Restarted")
    bot.infinity_polling()
