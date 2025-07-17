import telebot
from flask import Flask, request
import json
import os

API_TOKEN = '8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE'
ADMIN_ID = 5259348480  # Replace with your Telegram ID

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

DATA_FILE = "db.json"

# Utils
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    data = load_data()
    user_id = str(message.chat.id)

    if user_id not in data['users']:
        data['users'][user_id] = {
            "name": message.from_user.first_name,
            "ref_by": None,
            "balance": 0,
            "tasks_done": []
        }
        save_data(data)
    
    bot.send_message(message.chat.id, f"🙏 Welcome {message.from_user.first_name}!\n\nUse /profile, /tasks, /balance")

# Profile update
@bot.message_handler(commands=['profile'])
def profile(message):
    data = load_data()
    user = data['users'][str(message.chat.id)]
    msg = f"👤 Name: {user['name']}\n💰 Balance: ₹{user['balance']}"
    bot.send_message(message.chat.id, msg)

# Balance command
@bot.message_handler(commands=['balance'])
def balance(message):
    data = load_data()
    balance = data['users'][str(message.chat.id)]["balance"]
    bot.send_message(message.chat.id, f"💸 Your Balance: ₹{balance}")

# Tasks list
@bot.message_handler(commands=['tasks'])
def tasks(message):
    data = load_data()
    tasks = data['tasks']
    if not tasks:
        bot.send_message(message.chat.id, "📭 No tasks for today.")
    else:
        text = "📝 Today's Tasks:\n"
        for idx, task in enumerate(tasks, 1):
            text += f"{idx}. {task['text']} (₹{task['reward']})\n"
        text += "\nReply with /done <task_number> to mark it done"
        bot.send_message(message.chat.id, text)

# Mark task done
@bot.message_handler(commands=['done'])
def mark_done(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "❗Usage: /done <task_number>")
    
    try:
        task_num = int(args[1]) - 1
        data = load_data()
        user = data['users'][str(message.chat.id)]

        if task_num < 0 or task_num >= len(data['tasks']):
            return bot.reply_to(message, "❌ Invalid task number.")

        if task_num in user['tasks_done']:
            return bot.reply_to(message, "✅ Already marked as done.")

        reward = data['tasks'][task_num]['reward']
        user['balance'] += reward
        user['tasks_done'].append(task_num)
        save_data(data)

        bot.reply_to(message, f"✅ Task completed! ₹{reward} added to your balance.")

    except Exception as e:
        bot.reply_to(message, "❌ Error occurred. Try again.")

# Admin: Add Task
@bot.message_handler(commands=['addtask'])
def add_task(message):
    if message.chat.id != ADMIN_ID:
        return

    text = message.text.replace('/addtask', '').strip()
    if '|' not in text:
        return bot.reply_to(message, "❗Usage: /addtask Task Text | 10")

    task_text, reward = text.split('|')
    data = load_data()
    data['tasks'].append({"text": task_text.strip(), "reward": int(reward.strip())})
    save_data(data)

    bot.send_message(message.chat.id, "✅ Task added.")

# Flask Webhook
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is live"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://YOUR-RENDER-URL.onrender.com/" + API_TOKEN)
    app.run(host="0.0.0.0", port=10000)
