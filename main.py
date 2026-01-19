import os
import time
import subprocess
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from config import Config

# Render Port Binding
app = Flask(__name__)
@app.route('/')
def health(): return "Bot is Running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

bot = Client("uploader", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

def humanbytes(size):
    if not size: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0: return f"{size:.2f} {unit}"
        size /= 1024.0

async def progress_func(current, total, text, message, start_time):
    now = time.time()
    diff = now - start_time
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        progress = "[{0}{1}] {2}%".format('🟢' * int(percentage / 10), '⚪' * (10 - int(percentage / 10)), round(percentage, 2))
        tmp = f"**{text}**\n\n{progress}\n⚡ **Speed:** {humanbytes(speed)}/s\n📦 **Done:** {humanbytes(current)} / {humanbytes(total)}"
        try: await message.edit(tmp)
        except: pass

@bot.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text("✅ **Bot Online!**\nSend me a `.txt` file with m3u8 links.")

@bot.on_message(filters.document)
async def handle_txt(c, m):
    if not m.document.file_name.endswith(".txt"): return

    status = await m.reply_text("📥 **Downloading TXT...**")
    txt_path = await m.download()
    
    with open(txt_path, "r") as f:
        links = [line.strip() for line in f.readlines() if line.strip().startswith("http")]

    if not links:
        await status.edit("❌ No links found in file.")
        return

    for i, link in enumerate(links):
        await status.edit(f"⏳ **Processing {i+1}/{len(links)}**")
        
        proxied_link = f"{Config.API_URL}{link}"
        output = f"video_{int(time.time())}.mp4"

        # FFmpeg command
        cmd = ["ffmpeg", "-i", proxied_link, "-c", "copy", "-bsf:a", "aac_adtstoasc", output, "-y"]
        
        await status.edit(f"📥 **Downloading {i+1} via API...**")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(output):
            start_t = time.time()
            try:
                await c.send_video(
                    chat_id=m.chat.id, video=output, 
                    caption=f"✅ **Video {i+1}**\n🔗 `{link}`", 
                    supports_streaming=True,
                    progress=progress_func, 
                    progress_args=(f"📤 Uploading...", status, start_t)
                )
            except Exception as e: 
                await m.reply_text(f"❌ Upload Error: {e}")
            if os.path.exists(output): os.remove(output)
        else:
            await m.reply_text(f"❌ API Failed for link {i+1}")

    os.remove(txt_path)
    await status.delete()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run()
  
