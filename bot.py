import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, filters
)

ADMIN_ID = 5596196601
BOT_TOKEN = os.environ.get("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE")

users = {}

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in users:
        users[user_id] = {"balance": 0, "tasks": [], "referrer": None}
        if context.args:
            ref_id = context.args[0]
            if ref_id != user_id and ref_id in users:
                users[user_id]["referrer"] = ref_id
                users[ref_id]["balance"] += 10
    save_users()

    keyboard = [
        [InlineKeyboardButton("🎯 Daily Task", callback_data="daily_task")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 Welcome to Teem मराठे 🔥", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()

    if query.data == "daily_task":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🔗 Send today's Instagram or YouTube video link to like or watch."
        )
        users[user_id]["awaiting_task"] = True
        save_users()

    elif query.data == "balance":
        bal = users.get(user_id, {}).get("balance", 0)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"💰 Your balance: ₹{bal}"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text

    if users.get(user_id, {}).get("awaiting_task"):
        task_text = message
        users[user_id]["tasks"].append(task_text)
        users[user_id]["awaiting_task"] = False
        save_users()
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 Task from user {user_id}:\n\n{task_text}\n\nUse /approve {user_id} to give ₹10"
        )
        await update.message.reply_text("✅ Task submitted! Wait for admin approval.")
    else:
        await update.message.reply_text("❗ Please use the buttons to interact.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_ID):
        await update.message.reply_text("❌ You are not admin.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    target_id = args[0]
    if target_id in users:
        users[target_id]["balance"] += 10
        save_users()
        await context.bot.send_message(
            chat_id=int(target_id),
            text="✅ Your task is approved. ₹10 added to your account."
        )
        await update.message.reply_text(f"✅ Approved user {target_id}.")
    else:
        await update.message.reply_text("❌ User not found.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
