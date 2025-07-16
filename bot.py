import telebot
from telebot.types import ReplyKeyboardMarkup
import json

TOKEN = '8049094194:AAH_quTdGh7Yv33oy32KNYhuHYmCNvV8DIE'
bot = telebot.TeleBot(TOKEN)

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📜 My Profile", "👥 My Team")
    markup.row("💸 My Earnings", "📤 Invite Friends")
    markup.row("🎯 Daily Task", "🛍 Buy Course")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    name = message.from_user.first_name
    ref = message.text.split(" ")[1] if len(message.text.split()) > 1 else None

    if uid not in users:
        users[uid] = {"name": name, "ref_by": ref, "refs": [], "earnings": 0}
        if ref and ref in users:
            users[ref]["refs"].append(uid)
            users[ref]["earnings"] += 20
        save_users()

    bot.send_message(message.chat.id, f"🏹 जय शिवराय, {name}! तू 'Teem मराठे' मध्ये सहभागी झाला आहेस!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = str(message.from_user.id)
    if message.text == "📜 My Profile":
        bot.send_message(message.chat.id, f"👤 Name: {users[uid]['name']}\n💸 Earnings: ₹{users[uid]['earnings']}\n👥 Team: {len(users[uid]['refs'])}")
    elif message.text == "👥 My Team":
        team = users[uid]['refs']
        if team:
            team_list = "\n".join([users[i]['name'] for i in team if i in users])
            bot.send_message(message.chat.id, f"👥 Team Members:\n{team_list}")
        else:
            bot.send_message(message.chat.id, "कोणताही सदस्य अजूनपर्यंत जोडलेला नाही.")
    elif message.text == "💸 My Earnings":
        bot.send_message(message.chat.id, f"💰 एकूण उत्पन्न: ₹{users[uid]['earnings']}")
    elif message.text == "📤 Invite Friends":
        ref_link = f"https://t.me/YOUR_BOT_USERNAME?start={uid}"
        bot.send_message(message.chat.id, f"📣 तुमचा Referral Link:\n{ref_link}")
    elif message.text == "🎯 Daily Task":
        bot.send_message(message.chat.id, "📌 आजचा टास्क: \n\n📝 'Discipline is the bridge between goals and achievement.' हा quote शेअर करा.")
    elif message.text == "🛍 Buy Course":
        bot.send_message(message.chat.id, "💡 PixleLab Course ₹299 ला उपलब्ध!\n🪙 Pay: 7448029679@ybl\n🖼️ Screenshot admin ला पाठवा.")
    else:
        bot.send_message(message.chat.id, "कृपया योग्य पर्याय निवडा.", reply_markup=main_menu())

bot.polling()
