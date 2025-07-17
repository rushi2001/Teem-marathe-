from flask import Flask, request
import telebot
import os

API_TOKEN = ("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Temporary In-Memory Database (Use actual DB like MongoDB for production)
users = {}  # Format: user_id: {"ref": referrer_id, "team": []}

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if user_id not in users:
        referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        users[user_id] = {"ref": referrer_id, "team": []}
        if referrer_id and referrer_id in users:
            users[referrer_id]["team"].append(user_id)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👤 My ID", "🔗 My Referral Link")
    markup.row("👥 My Team")
    bot.send_message(user_id, "Welcome to the bot!", reply_markup=markup)

# Button handler
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id

    if message.text == "👤 My ID":
        bot.reply_to(message, f"Your ID: {user_id}")

    elif message.text == "🔗 My Referral Link":
        bot.reply_to(message, f"Your link:\nhttps://t.me/YOUR_BOT_USERNAME?start={user_id}")

    elif message.text == "👥 My Team":
        team = users.get(user_id, {}).get("team", [])
        if team:
            msg = f"👥 Your Team ({len(team)} members):\n" + "\n".join([f"- {uid}" for uid in team])
        else:
            msg = "😕 You don’t have any team members yet."
        bot.reply_to(message, msg)

# Webhook receiver
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.environ.get('RENDER_URL')}/{API_TOKEN}")
    return "Webhook Set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
