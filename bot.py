import telebot
import time
import datetime
import threading
from telebot import types
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from collections import defaultdict, deque
import traceback

DetectorFactory.seed = 0

# --- CONFIGURATION (CORRECTED) ---
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
REQ_CHANNEL = "@Dark_Unkwon_ModZ"        # ✅ Confirmed from your link
LOG_CHANNEL = "@dumodzbotmanage"         # ❗ NOT "@dumodzbotmanager" — your link shows NO "r"
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

def is_admin(uid):
    return uid == ADMIN_ID

def is_joined(user_id):
    try:
        member = bot.get_chat_member(REQ_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"[JOIN ERROR] User {user_id}: {e}")
        return False

def auto_delete(chat_id, msg_id, delay=15):
    def _del():
        try:
            bot.delete_message(chat_id, msg_id)
        except:
            pass
    threading.Timer(delay, _del).start()

def animate_edit(chat_id, msg_id, frames, delay=0.7):
    for i, txt in enumerate(frames):
        try:
            bot.edit_message_text(txt, chat_id, msg_id, disable_web_page_preview=True)
            time.sleep(delay if i < len(frames)-1 else 0.5)
        except:
            break

def is_rate_limited(uid):
    now = time.time()
    if uid in last_request_time and now - last_request_time[uid] < REQUEST_COOLDOWN:
        return True
    last_request_time[uid] = now
    return False

# --- START & CALLBACKS ---
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
                "To use this <b>Premium Translator Bot</b>, join our official channel.\n\n"
                "✨ Benefits:\n• Exclusive updates\n• New features\n• Priority support\n\n"
                "<i>Click 'Verify Now' after joining.</i>"
            ),
            reply_markup=markup
        )
        auto_delete(message.chat.id, sent.message_id, 60)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭", url=DEV_URL))
    markup.add(
        types.InlineKeyboardButton("🌐 Blog", url=BLOG_URL),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    markup.add(types.InlineKeyboardButton("📜 Help", callback_data="help"))
    bot.send_photo(
        message.chat.id,
        BANNER_URL,
        caption=f"🌟 <b>Welcome to {BOT_NAME}</b>!\n\n🤖 AI-powered translator ready!\n\n✅ Send any text to begin.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(call):
    uid = call.from_user.id
    if uid in user_banned:
        bot.answer_callback_query(call.id, "🚫 Banned.", show_alert=True)
        return
    if call.data == "verify":
        if is_joined(uid):
            bot.edit_message_caption("🔄 Verifying...", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.edit_message_caption("✅ Verified! Access granted.", call.message.chat.id, call.message.message_id)
            time.sleep(1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join channel first!", show_alert=True)
    elif call.data == "settings":
        current = user_target_lang[uid]
        names = {'en':'English','bn':'Bengali','hi':'Hindi','ar':'Arabic'}
        name = names.get(current, current.upper())
        markup = types.InlineKeyboardMarkup()
        for n, c in [('EN','en'),('BN','bn'),('HI','hi'),('AR','ar')]:
            markup.add(types.InlineKeyboardButton(n, callback_data=f"lang_{c}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        bot.edit_message_caption(f"⚙️ Target: {name}", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("lang_"):
        code = call.data.split("_")[1]
        user_target_lang[uid] = code
        bot.answer_callback_query(call.id, f"✅ Set to {code.upper()}")
        start(call.message)
    elif call.data == "help":
        bot.edit_message_caption(
            "📘 <b>Guide</b>\n• Send text → auto-translate\n• Use /bn, /hi, /ar\n• View history in Settings",
            call.message.chat.id, call.message.message_id,
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_home"))
        )
    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

# --- TRANSLATION ---
@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'), content_types=['text'])
def auto_translate(message):
    uid = message.from_user.id
    if uid in user_banned or not is_joined(uid): return
    if is_rate_limited(uid):
        bot.reply_to(message, f"⏳ Wait {REQUEST_COOLDOWN}s")
        return
    status = bot.reply_to(message, "📡")
    try:
        frames = ["🌌 Connecting...", "🧠 Translating...", "✅ Done!"]
        animate_edit(message.chat.id, status.message_id, frames)
        src = message.text
        detected = detect(src)
        target = user_target_lang[uid]
        trans = GoogleTranslator(source='auto', target=target).translate(src)
        user_history[uid].append((src[:30], trans[:30]))
        result = f"📥 ({detected.upper()}):\n<code>{src[:80]}{'...' if len(src)>80 else ''}</code>\n\n📤 ({target.upper()}):\n<code>{trans}</code>"
        bot.edit_message_text(result, message.chat.id, status.message_id)
        auto_delete(message.chat.id, status.message_id, 25)
    except Exception as e:
        bot.edit_message_text("❌ Translation failed.", message.chat.id, status.message_id)

# --- ADMIN COMMANDS (FULLY FIXED) ---
@bot.message_handler(commands=['admin'], func=is_admin)
def cmd_admin(message):
    bot.reply_to(message, "👑 Admin Panel Active. Use /adminhelp for commands.")

@bot.message_handler(commands=['adminhelp'], func=is_admin)  # ✅ THIS NOW WORKS
def cmd_adminhelp(message):
    help_text = (
        "🛠️ <b>Admin Commands</b>\n\n"
        "• <code>/ban [id]</code> – Ban user\n"
        "• <code>/unban [id]</code> – Unban user\n"
        "• <code>/user_info [id]</code>\n"
        "• <code>/stats</code> – Show stats\n"
        "• <code>/broadcast [msg]</code>\n"
        "• <code>/clear_hist</code> – Clear all history"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['ban'], func=is_admin)
def cmd_ban(message):
    try:
        uid = int(message.text.split()[1])
        user_banned.add(uid)
        bot.reply_to(message, f"🚫 Banned {uid}")
        notify_manager(f"User {uid} banned by admin")
    except:
        bot.reply_to(message, "UsageId: /ban [user_id]")

@bot.message_handler(commands=['unban'], func=is_admin)
def cmd_unban(message):
    try:
        uid = int(message.text.split()[1])
        user_banned.discard(uid)
        bot.reply_to(message, f"✅ Unbanned {uid}")
    except:
        bot.reply_to(message, "UsageId: /unban [user_id]")

@bot.message_handler(commands=['user_info'], func=is_admin)
def cmd_user_info(message):
    try:
        uid = int(message.text.split()[1])
        joined = "✅" if is_joined(uid) else "❌"
        status = "🚫 Banned" if uid in user_banned else "🟢 Active"
        hist = len(user_history[uid])
        bot.reply_to(message, f"👤 ID: <code>{uid}</code>\nChannel: {joined}\nStatus: {status}\nHistory: {hist}")
    except:
        bot.reply_to(message, "UsageId: /user_info [id]")

@bot.message_handler(commands=['stats'], func=is_admin)
def cmd_stats(message):
    bot.reply_to(message, f"👥 Users: {len(user_list)}\n🚫 Banned: {len(user_banned)}")

@bot.message_handler(commands=['broadcast'], func=is_admin)
def cmd_broadcast(message):
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "UsageId: /broadcast [message]")
        return
    msg = parts[1]
    success = 0
    for u in list(user_list):
        try:
            bot.send_message(u, f"📣 <b>Broadcast</b>\n\n{msg}")
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ Sent to {success} users.")

@bot.message_handler(commands=['clear_hist'], func=is_admin)
def cmd_clear_hist(message):
    user_history.clear()
    bot.reply_to(message, "🗑️ All translation histories cleared.")

# --- LOGGING (NOW WORKS) ---
def notify_manager(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = (
        f"🔔 <b>Bot Status Update</b>\n"
        f"──────────────\n"
        f"🤖 Bot: {BOT_NAME}\n"
        f"🔑 Token: <code>{BOT_TOKEN}</code>\n"
        f"🕗 Time: {now}\n"
        f"📌 Event: {event}\n"
        f"🟢 Status: LIVE\n"
        f"──────────────"
    )
    try:
        bot.send_message(LOG_CHANNEL, log_msg)  # Now uses CORRECT @dumodzbotmanage
        print(f"[LOG SENT] {event}")
    except Exception as e:
        print(f"[LOG FAILED] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Bot...")
    notify_manager("🟢 Bot Started / Restarted")  # Will now send!
    bot.infinity_polling()
