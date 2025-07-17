import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, MessageHandler,
    filters, CallbackQueryHandler
)

# ⛑️ Admin Telegram ID टाका (तुझा)
ADMIN_ID = 5596196601

# 📂 users.json मध्ये user add/save करणं
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = {"tasks_done": 0}
        with open("users.json", "w") as f:
            json.dump(data, f, indent=4)

# 📥 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text("नमस्कार! तुम्ही बोट वापरायला सुरुवात केली आहे.")

# 🛡️ /admin command (Admin Panel UI)
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔️ तुम्ही Admin नाही!")
        return

    with open("users.json", "r") as f:
        data = json.load(f)

    total_users = len(data)
    text = f"👨‍💼 Admin Panel:\n\n👥 Total Users: {total_users}"

    keyboard = [
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# 📢 Broadcast start
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "broadcast":
        await query.message.reply_text("✍️ Broadcast साठी message टाका:")
        context.user_data["broadcast_mode"] = True

# 📨 Broadcast message पाठवणं
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("broadcast_mode") and update.effective_user.id == ADMIN_ID:
        message = update.message.text
        context.user_data["broadcast_mode"] = False

        with open("users.json", "r") as f:
            data = json.load(f)

        sent = 0
        for user_id in data:
            try:
                await context.bot.send_message(chat_id=int(user_id), text=message)
                sent += 1
            except:
                pass
        await update.message.reply_text(f"📤 Broadcast पाठवला गेला {sent} users ना.")

# ✅ Bot run करणं
def main():
    BOT_TOKEN = ("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
