import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, filters
)
ADMIN_ID = 5596196601

users = {}

# Load users if exists
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

def start(update: Update, context: CallbackContext):
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
    update.message.reply_text("🔥 Welcome to Teem मराठे 🔥", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    query.answer()

    if query.data == "daily_task":
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🔗 Send today's Instagram or YouTube video link to like or watch."
        )
        users[user_id]["awaiting_task"] = True
        save_users()

    elif query.data == "balance":
        bal = users.get(user_id, {}).get("balance", 0)
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"💰 Your balance: ₹{bal}"
        )

def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    message = update.message.text

    if users.get(user_id, {}).get("awaiting_task"):
        task_text = message
        users[user_id]["tasks"].append(task_text)
        users[user_id]["awaiting_task"] = False
        save_users()
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 Task from user {user_id}:\n\n{task_text}\n\nUse /approve {user_id} to give ₹10"
        )
        update.message.reply_text("✅ Task submitted! Wait for admin approval.")
    else:
        update.message.reply_text("❗ Please use the buttons to interact.")

def approve(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_ID):
        update.message.reply_text("❌ You are not admin.")
        return

    args = context.args
    if not args:
        update.message.reply_text("Usage: /approve <user_id>")
        return

    target_id = args[0]
    if target_id in users:
        users[target_id]["balance"] += 10
        save_users()
        context.bot.send_message(
            chat_id=int(target_id),
            text="✅ Your task is approved. ₹10 added to your account."
        )
        update.message.reply_text(f"✅ Approved user {target_id}.")
    else:
        update.message.reply_text("❌ User not found.")

def main():
    updater = Updater("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("approve", approve))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
