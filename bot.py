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
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "posts.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        POSTS = json.load(f)
else:
    POSTS = {}
    
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
                "Translation ⬇️",
                callback_data=f"translate_{post_id}"
            )
        ]
    ]

    await update.message.reply_text(
        turkish.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard)
  )
    
  async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    post_id = query.data.replace("translate_", "")

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
    app.add_handler(CallbackQueryHandler(button))

    print("Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
