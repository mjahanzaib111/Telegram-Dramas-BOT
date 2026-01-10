import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from googleapiclient.discovery import build
import logging

# Logging (helps debug updates)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Safety check
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY is not set")

# Initialize YouTube client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Welcome!\n\nUse:\n/watch <Drama Name> <Episode Number>\n\nExample:\n/watch Anupama 1"
    )

# /watch command
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /watch <Drama Name> <Episode Number>")
        return

    drama = " ".join(context.args[:-1])
    episode = context.args[-1]
    query = f"{drama} Episode {episode}"

    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=3
        )
        response = request.execute()

        if not response["items"]:
            await update.message.reply_text("No results found.")
            return

        msg = f"🔎 Results for: {query}\n"
        for item in response["items"]:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            msg += f"\n🎥 {title}\nhttps://www.youtube.com/watch?v={video_id}\n"

        await update.message.reply_text(msg)

    except Exception:
        await update.message.reply_text("YouTube error. Try later.")

# Build app and add handlers
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("watch", watch))

print("Bot started...")
app.run_polling()
