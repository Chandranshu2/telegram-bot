import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import BadRequest

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("8349024296:AAFCSi5VlFM0-wDxLisD5r32Nte_ywe9DVQ")
ADMIN_ID = 8034017217

PUBLIC_CHANNEL = "@sauryasignal4564"
PRIVATE_CHANNEL_LINK = "https://t.me/+yj2ZMJY1G85hZjVl"
# ---------------------------------------

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

logging.basicConfig(level=logging.INFO)


async def is_user_joined(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except BadRequest:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    joined = await is_user_joined(context.bot, user_id)

    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Public Channel", url=f"https://t.me/{PUBLIC_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "❗ You must join our public channel first:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    await show_verify(update, context)


async def show_verify(update, context):
    keyboard = [
        [InlineKeyboardButton("🤖 Verify Human", callback_data="verify")]
    ]
    await update.message.reply_text(
        "✅ Public channel verified.\n\nNow verify you are human:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    joined = await is_user_joined(context.bot, user_id)

    if not joined:
        await query.edit_message_text("❌ You have not joined yet. Join the channel first.")
        return

    await query.edit_message_text("✅ Public channel verified!")
    await show_verify(query, context)


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔐 Join Private Channel", url=PRIVATE_CHANNEL_LINK)]
    ]

    await query.edit_message_text(
        "🎉 Verification successful!\n\nClick below to join the private channel:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("👑 Admin access granted.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify"))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
