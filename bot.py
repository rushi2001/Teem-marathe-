from telebot import TeleBot
import json
import os

bot = TeleBot("8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE")

# User data फाईल
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    args = message.text.split()
    referred_by = args[1] if len(args) > 1 else None

    users = load_users()
    if user_id not in users:
        users[user_id] = {
            "username": username,
            "points": 0,
            "referred_by": referred_by,
            "referrals": []
        }
        if referred_by and referred_by in users:
            users[referred_by]["points"] += 10
            users[referred_by]["referrals"].append(user_id)

        save_users(users)

    bot.send_message(message.chat.id, f"नमस्कार {username or 'मित्रा'}! Motivational Akhada मध्ये स्वागत आहे.")

# Profile Command
@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        user = users[user_id]
        profile_text = f"""🧾 *तुझं प्रोफाइल*
👤 Username: @{user['username']}
💰 Points: {user['points']}
👥 Referrals: {len(user['referrals'])}
"""
        bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "कृपया /start कमांड वापरा आधी.")

# Refer Command
@bot.message_handler(commands=['refer'])
def refer(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(message.chat.id, f"🫂 आपला referral link:\n{referral_link}")
    else:
        bot.send_message(message.chat.id, "कृपया /start कमांड वापरा आधी.")

# Polling सुरू करा
bot.polling()
