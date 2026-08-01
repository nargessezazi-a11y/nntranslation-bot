import os
import json
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1002876005137
DATA_FILE = "posts.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        POSTS = json.load(f)
else:
    POSTS = {}

LAST_VOICE = None
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "من ربات ترجمه هستم.\n\n"
        "برای ساخت پست از دستور /post استفاده کن."
    )


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "فرمت درست:\n"
            "/post متن ترکی | ترجمه فارسی"
        )
        return

    try:
        turkish, persian = text.split("|", 1)
    except:
        await update.message.reply_text(
            "لطفاً بین متن ترکی و ترجمه علامت | بگذار."
        )
        return

    post_id = str(len(POSTS) + 1)

    POSTS[post_id] = {
        "tr": turkish.strip(),
        "fa": persian.strip()
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(POSTS, f, ensure_ascii=False, indent=4)

    keyboard = [
        [
            InlineKeyboardButton(
                "𝐓𝐫𝐚𝐧𝐬𝐥𝐚𝐭𝐢𝐨𝐧",
                callback_data=f"translate_{post_id}"
            )
        ]
    ]

    await context.bot.send_message(
    chat_id=CHANNEL_ID,
    text=turkish.strip(),
    reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
    "✅ پست داخل کانال ارسال شد."
    )
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global LAST_VOICE

    LAST_VOICE = update.message.voice.file_id

    await update.message.reply_text(
        "✅ ویس ذخیره شد.\n\n"
        "فرمت درست:\n"
        "/post متن ترکی | ترجمه فارسی"
    )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("BUTTON WORKED")

    query = update.callback_query



    print("CALLBACK DATA:", query.data)

    post_id = query.data.replace("translate_", "")

    print("POSTS:", POSTS)
    print("POST ID:", post_id, type(post_id))

    if post_id not in POSTS:
        await query.answer(
            "ترجمه پیدا نشد!",
            show_alert=True
        )
        return

    await query.answer(
      POSTS[post_id]["fa"],
      show_alert=True
    )
    
    
def main():
  app = Application.builder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("post", post))
  app.add_handler(MessageHandler(filters.VOICE, voice))  
  app.add_handler(CallbackQueryHandler(button))

  print("Bot Started...")

  app.run_polling()


if __name__ == "__main__":
    main()
