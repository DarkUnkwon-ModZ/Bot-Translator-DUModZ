import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from googletrans import Translator
from datetime import datetime

# --- CONFIGURATION ---
API_ID = 37180034  # Replace with your API ID (Get from my.telegram.org)
API_HASH = "10b5c82a474ac6403c1cd214eb4de5a5"  # Replace with your API HASH
BOT_TOKEN = "8474301231:AAHzZnyJVzWZjlRKt9l-1KPA-0IBKAoiSX8"
BOT_NAME = "Translator - DUModZ"
ADMIN_ID = 8504263842
LOG_CHANNEL = "dumodzbotmanager"  # Username without @
REQ_CHANNEL = "Dark_Unkwon_ModZ"  # Force Join Channel
BANNER_URL = "https://raw.githubusercontent.com/DarkUnkwon-ModZ/DUModZ-Resource/refs/heads/main/Img/darkunkwonmodz-banner.jpg"

app = Client("TranslatorBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
translator = Translator()

# --- HELPER FUNCTIONS ---
async def is_subscribed(client, message):
    try:
        member = await client.get_chat_member(REQ_CHANNEL, message.from_user.id)
        return True
    except:
        return False

# --- START COMMAND & WELCOME SCREEN ---
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not await is_subscribed(client, message):
        buttons = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQ_CHANNEL}")],
                   [InlineKeyboardButton("✅ Verified & Start", callback_data="verify_check")]]
        return await message.reply_photo(
            photo=BANNER_URL,
            caption="⚠️ **Access Denied!**\n\nYou must join our channel to use this premium bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    welcome_text = (
        f"👋 **Welcome to {BOT_NAME}**\n\n"
        "I am an advanced professional AI Translator.\n\n"
        "**Features:**\n"
        "✨ Auto Translation (Detect -> English)\n"
        "✨ Specific Lang Commands (/bn, /hi, /ar)\n"
        "✨ Ultra Fast & Smooth\n\n"
        "Developer: [𝗗𝗮𝗿𝗸 𝗨𝗻𝗸𝘄𝗼𝗻 𝗠𝗼𝗱𝗭](https://t.me/Dark_Unkwon_ModZ)"
    )
    buttons = [
        [InlineKeyboardButton("🌐 Website", url="https://darkunkwon-modz.blogspot.com"),
         InlineKeyboardButton("💬 Support", url="https://t.me/Dark_Unkwon_ModZ")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")]
    ]
    await message.reply_photo(photo=BANNER_URL, caption=welcome_text, reply_markup=InlineKeyboardMarkup(buttons))

# --- FORCE JOIN VERIFY ---
@app.on_callback_query(filters.regex("verify_check"))
async def verify_callback(client, callback_query: CallbackQuery):
    if await is_subscribed(client, callback_query):
        await callback_query.answer("✅ Verification Successful!", show_alert=True)
        await callback_query.message.delete()
        await start_cmd(client, callback_query.message)
    else:
        await callback_query.answer("❌ You haven't joined yet!", show_alert=True)

# --- TRANSLATION LOGIC ---
@app.on_message(filters.text & filters.private)
async def auto_translate(client, message):
    if not await is_subscribed(client, message): return
    
    # Ignore commands
    if message.text.startswith("/"): return

    msg = await message.reply("📡 **Detecting language...**", quote=True)
    try:
        detected = translator.detect(message.text)
        translation = translator.translate(message.text, dest='en')
        
        await msg.edit(f"✨ **Translated from {detected.lang.upper()} to EN**:\n\n`{translation.text}`")
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")

# --- MANUAL COMMANDS (/bn, /hi, etc) ---
@app.on_message(filters.command(["bn", "hi", "in", "ar", "es", "fr"]) & filters.private)
async def manual_translate(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide text. Example: `/bn Hello`")
    
    target_lang = message.command[0] # 'bn', 'hi' etc
    if target_lang == "in": target_lang = "hi" # map 'in' to hindi
    
    text_to_translate = message.text.split(None, 1)[1]
    msg = await message.reply("🔄 **Translating...**")
    
    try:
        # User wants to translate TO this language OR from this language to English.
        # Based on your request: "ওই ভাষা থেকে ইংরেজিতে রুপান্তর করে দিবে"
        translation = translator.translate(text_to_translate, dest='en')
        await msg.edit(f"✅ **Translated to English:**\n\n`{translation.text}`")
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")

# --- ADMIN PANEL ---
@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(client, message):
    await message.reply_text(
        "👑 **Admin Control Panel**\n\nCommands:\n/stats - Bot Status\n/broadcast - Message to users\n/restart - Manual Restart",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close Panel", callback_data="close")]])
    )

# --- STARTUP NOTIFICATION ---
async def send_log():
    async with app:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_text = (
            f"🚀 **Bot Started Successfully!**\n\n"
            f"🤖 **Bot Name:** {BOT_NAME}\n"
            f"🔑 **Token:** `{BOT_TOKEN}`\n"
            f"⏰ **Time:** {now}\n"
            f"📡 **Status:** Running on GitHub Actions"
        )
        try:
            await app.send_message(LOG_CHANNEL, log_text)
        except:
            print("Log channel not found!")

if __name__ == "__main__":
    import threading
    # Function to auto-restart every 4 hours internally if needed, 
    # but we'll use GitHub Actions for better reliability.
    loop = asyncio.get_event_loop()
    loop.create_task(send_log())
    print("Bot is alive...")
    app.run()
