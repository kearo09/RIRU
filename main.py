import os
from dotenv import load_dotenv
from kurigram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# .env file se data load karne ke liye
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION = os.getenv("SESSION")

# Clients Setup
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("UserAssistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(user)

@app.on_message(filters.command("play") & filters.group)
async def play_command(_, message):
    if len(message.command) < 2:
        return await message.reply("🔎 Please provide a song name.\nExample: `/play starboy`")

    m = await message.reply("🔄 Processing...")
    query = message.text.split(None, 1)[1]

    try:
        # YT-DLP configuration to get audio link
        ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']

        # Py-TgCalls v2.x syntax
        await call_py.play(
            message.chat.id,
            MediaStream(url)
        )
        await m.edit(f"🎶 **Started Playing:** {title}")

    except Exception as e:
        await m.edit(f"❌ Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_command(_, message):
    try:
        await call_py.leave_call(message.chat.id)
        await message.reply("⏹ Music stopped successfully.")
    except Exception as e:
        await message.reply(f"❌ Nothing is playing or Error: {e}")

# Start functions
async def main():
    await app.start()
    await user.start()
    await call_py.start()
    print("Bot is online!")
    
# Manual handling for starting the loop
import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
