from flask import Flask, request
import telebot
import os

API_TOKEN = ("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# In-memory database (for demo/testing)
users = {}  # Format: { user_id: {"ref": referrer_id, "team": [], "balance": 0} }

# Constants
REFERRAL_REWARD = 5  # ₹5 per refer

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if user_id not in users:
        referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        users[user_id] = {"ref": referrer_id, "team": [], "balance": 0}

        if referrer_id and referrer_id in users and user_id != referrer_id:
            users[referrer_id]["team"].append(user_id)
            users[referrer_id]["balance"] += REFERRAL_REWARD

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👤 Profile", "💰 My Balance")
    markup.row("🔗 My Referral Link", "👥 My Team")
    bot.send_message(user_id, "🎉 Welcome to the Referral Bot!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    user = users.get(user_id)

    if not user:
        bot.reply_to(message, "कृपया /start ने सुरुवात करा.")
        return

    if message.text == "👤 Profile":
        ref = user.get("ref", "None")
        team_count = len(user.get("team", []))
        msg = (
            f"👤 *Your Profile:*\n"
            f"🆔 ID: `{user_id}`\n"
            f"👑 Referred By: `{ref}`\n"
            f"👥 Team Members: `{team_count}`"
        )
        bot.send_message(user_id, msg, parse_mode="Markdown")

    elif message.text == "💰 My Balance":
        balance = user.get("balance", 0)
        bot.send_message(user_id, f"💰 Your Current Balance: ₹{balance}")

    elif message.text == "🔗 My Referral Link":
        bot.send_message(user_id, f"🔗 Share this link:\nhttps://t.me/YOUR_BOT_USERNAME?start={user_id}")

    elif message.text == "👥 My Team":
        team = user.get("team", [])
        if team:
            msg = f"👥 Your Team ({len(team)}):\n" + "\n".join([f"- `{uid}`" for uid in team])
        else:
            msg = "🙁 You don't have any team members yet."
        bot.send_message(user_id, msg, parse_mode="Markdown")

# Webhook setup
@app.route('/' + API_TOKEN, methods=['POST'])
def receive_update():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.environ.get('RENDER_URL')}/{API_TOKEN}")
    return "Webhook सेट झाला!", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
