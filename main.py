import os
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# 🔐 Your TON payment address
TON_PAYMENT_ADDRESS = "EQAjMmgE2W0K8kIxd1WivjwTO_XBE2wJ06pzIfzHFWnWlZWm"

# ================== TEXT CONTENT ==================

WELCOME_TEXT = (
    "👋 <b>Welcome to TON Meme Trends Bot</b>\n\n"
    "This bot handles <b>paid visibility requests</b> for the TON Meme Trends channel.\n\n"
    "⚡ What we offer:\n"
    "• Project visibility\n"
    "• Launch exposure\n"
    "• No endorsements\n\n"
    "Choose an option below 👇"
)

PRICING_TEXT = (
    "💰 <b>TON Meme Trends — Pricing</b>\n\n"
    "🟢 <b>Starter Visibility — 4 TON</b>\n"
    "• Basic post\n"
    "• 24h window\n\n"
    "🔵 <b>Launch Boost — 8 TON</b>\n"
    "• Image + text\n"
    "• Same-day posting\n\n"
    "🟣 <b>Spotlight — 15 TON</b>\n"
    "• Image + text\n"
    "• Pinned (6–12h)\n\n"
    "⚠️ Visibility only. Not endorsement."
)

HOW_IT_WORKS_TEXT = (
    "❓ <b>How It Works</b>\n\n"
    "1️⃣ Submit your project\n"
    "2️⃣ Choose a visibility tier\n"
    "3️⃣ Make payment\n"
    "4️⃣ Admin confirms\n"
    "5️⃣ Post goes live\n\n"
    "We provide visibility only. Always DYOR."
)

PAID_INSTRUCTIONS = (
    "🟢 <b>Paid Visibility Application</b>\n\n"
    "Send your project details in <b>ONE message</b> using this format:\n\n"
    "🪙 Project Name:\n"
    "💰 Marketcap:\n"
    "📜 Contract Address:\n"
    "🔗 Telegram:\n"
    "🌐 Website (if any):\n"
    "📸 Image (optional):\n\n"
    "After submission, you’ll receive payment instructions."
)

FREE_INSTRUCTIONS = (
    "🆓 <b>Free Listing (Limited)</b>\n\n"
    "Free listings are limited and <b>not guaranteed</b>.\n\n"
    "Send your project details in <b>ONE message</b> like this:\n\n"
    "🪙 Project Name:\n"
    "📜 Contract Address:\n"
    "🔗 Telegram:\n"
)

PAYMENT_TEXT = (
    "💰 <b>Payment Details</b>\n\n"
    f"<b>TON Address:</b>\n<code>{TON_PAYMENT_ADDRESS}</code>\n\n"
    "📌 After payment, send:\n"
    "• TX Hash\n"
    "• Your Telegram username\n\n"
    "⏱ Post will be made after confirmation."
)

# ================== KEYBOARD ==================

def main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 Apply for Paid Visibility", callback_data="paid")],
            [InlineKeyboardButton("🆓 Free Listing (Limited)", callback_data="free")],
            [InlineKeyboardButton("📊 Pricing", callback_data="pricing")],
            [InlineKeyboardButton("❓ How It Works", callback_data="how")],
        ]
    )

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu(),
        parse_mode=ParseMode.HTML
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "paid":
        context.user_data["mode"] = "paid_details"
        await query.message.reply_text(PAID_INSTRUCTIONS, parse_mode=ParseMode.HTML)

    elif query.data == "free":
        context.user_data["mode"] = "free_details"
        await query.message.reply_text(FREE_INSTRUCTIONS, parse_mode=ParseMode.HTML)

    elif query.data == "pricing":
        await query.message.reply_text(PRICING_TEXT, parse_mode=ParseMode.HTML)

    elif query.data == "how":
        await query.message.reply_text(HOW_IT_WORKS_TEXT, parse_mode=ParseMode.HTML)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mode = context.user_data.get("mode")
    text = update.message.text

    if not ADMIN_CHAT_ID:
        await update.message.reply_text("⚠️ ADMIN_CHAT_ID is not set.")
        return

    # PAID SUBMISSION
    if mode == "paid_details":
        context.user_data["mode"] = "paid_tx"

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🟢 <b>NEW PAID VISIBILITY REQUEST</b>\n\n"
                f"👤 User: <b>{user.full_name}</b>\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"🔗 Username: @{user.username}\n\n"
                f"<b>Details:</b>\n{text}"
            ),
            parse_mode=ParseMode.HTML
        )

        await update.message.reply_text(PAYMENT_TEXT, parse_mode=ParseMode.HTML)
        return

    # TX HASH
    if mode == "paid_tx":
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "✅ <b>TX / PAYMENT MESSAGE</b>\n\n"
                f"👤 User: <b>{user.full_name}</b>\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"🔗 Username: @{user.username}\n\n"
                f"🧾 Message:\n{text}"
            ),
            parse_mode=ParseMode.HTML
        )

        await update.message.reply_text(
            "✅ Received. Admin will confirm and post shortly.\n\n"
            "Type /start to return to menu."
        )
        return

    # FREE SUBMISSION
    if mode == "free_details":
        context.user_data.clear()

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🆓 <b>NEW FREE LISTING REQUEST</b>\n\n"
                f"👤 User: <b>{user.full_name}</b>\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"🔗 Username: @{user.username}\n\n"
                f"<b>Details:</b>\n{text}"
            ),
            parse_mode=ParseMode.HTML
        )

        await update.message.reply_text(
            "✅ Submitted. If selected, it will be posted when slots are available.\n\n"
            "Type /start to return to menu."
        )
        return

    await update.message.reply_text("Type /start to open the menu.")

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram ID is: {update.effective_user.id}")

# ================== RUN ==================

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", my_id))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
