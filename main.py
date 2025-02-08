import telebot
from telebot import types
import json

# 🔹 Replace with your BotFather token
TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

# 🔹 Store user data (In a real app, use a database)
users = {}

# 🔹 Investment packages and VIP levels
investment_plans = {
    "Starter Plan": {"amount": 399, "days": 40, "daily_return": 133, "vip": "VIP 1"},
    "LT Smart Plan": {"amount": 599, "days": 60, "daily_return": 233, "vip": "VIP 2"},
    "Elite Plan": {"amount": 999, "days": 40, "daily_return": 424, "vip": "VIP 3"},
    "Premium Plan": {"amount": 1999, "days": 30, "daily_return": 999, "vip": "VIP 4"},
    "Great Package": {"amount": 9999, "days": 30, "daily_return": 2666, "vip": "VIP 5"},
}

# 🔹 Load user data from file (if exists)
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

# 🔹 Save user data function
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# 🔹 Start command (Register user)
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users[chat_id] = {"name": "", "bank_details": "", "investment": None, "vip": None, "balance": 0}
        bot.send_message(chat_id, "Welcome! Please enter your name to register:")
    else:
        bot.send_message(chat_id, "Welcome back! Use /menu to see options.")

# 🔹 Register name
@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id]["name"] == "")
def register_name(message):
    chat_id = message.chat.id
    users[chat_id]["name"] = message.text
    save_users()
    bot.send_message(chat_id, f"Thanks, {message.text}! Now, use /add_bank to enter your bank details.")

# 🔹 Register bank details before investing
@bot.message_handler(commands=['add_bank'])
def add_bank_details(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter your bank account details:")
    bot.register_next_step_handler(message, save_bank_details)

def save_bank_details(message):
    chat_id = message.chat.id
    users[chat_id]["bank_details"] = message.text
    save_users()
    bot.send_message(chat_id, "✅ Bank details saved! Now you can invest. Use /menu to proceed.")

# 🔹 Show menu
@bot.message_handler(commands=['menu'])
def menu(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📈 Invest", "📊 My Progress", "💸 Withdraw", "❓ FAQs"]
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)

# 🔹 Handle menu options
@bot.message_handler(func=lambda message: message.text in ["📈 Invest", "📊 My Progress", "💸 Withdraw", "❓ FAQs"])
def handle_menu(message):
    chat_id = message.chat.id
    if message.text == "📈 Invest":
        invest(chat_id)
    elif message.text == "📊 My Progress":
        show_progress(chat_id)
    elif message.text == "💸 Withdraw":
        withdraw(chat_id)
    elif message.text == "❓ FAQs":
        faqs(chat_id)

# 🔹 Investment options (Checks if bank details exist)
def invest(chat_id):
    if not users[chat_id]["bank_details"]:
        bot.send_message(chat_id, "⚠️ You must add your bank details before investing! Use /add_bank.")
        return
    
    markup = types.InlineKeyboardMarkup()
    for plan, details in investment_plans.items():
        markup.add(types.InlineKeyboardButton(f"{plan} - ₹{details['amount']}", callback_data=f"invest_{plan}"))
    bot.send_message(chat_id, "Choose an investment plan:", reply_markup=markup)

# 🔹 Handle investment selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("invest_"))
def confirm_investment(call):
    chat_id = call.message.chat.id
    plan_name = call.data.replace("invest_", "")
    
    if users[chat_id]["investment"]:
        bot.send_message(chat_id, "You already have an active investment!")
        return
    
    plan = investment_plans[plan_name]
    users[chat_id]["investment"] = {"plan": plan_name, "amount": plan["amount"], "days_left": plan["days"], "daily_return": plan["daily_return"]}
    users[chat_id]["vip"] = plan["vip"]
    save_users()
    
    bot.send_message(chat_id, f"Investment confirmed! You've chosen {plan_name}. Please send proof of payment.")

# 🔹 Show progress
def show_progress(chat_id):
    user = users.get(chat_id, {})
    if not user["investment"]:
        bot.send_message(chat_id, "You haven't invested yet. Use /menu to start.")
        return

    invest_details = user["investment"]
    msg = f"💰 **Investment Details:**\n📦 Plan: {invest_details['plan']}\n💵 Amount: ₹{invest_details['amount']}\n📅 Days Left: {invest_details['days_left']}\n💸 Daily Return: ₹{invest_details['daily_return']}"
    bot.send_message(chat_id, msg)

# 🔹 Withdraw function (auto-transfer after cycle ends)
def withdraw(chat_id):
    user = users.get(chat_id, {})
    if not user["investment"]:
        bot.send_message(chat_id, "No active investment. Use /menu to start.")
        return
    
    if user["investment"]["days_left"] > 0:
        bot.send_message(chat_id, "You can withdraw after the cycle ends.")
    else:
        earned = user["investment"]["amount"] * 2  # Example: Double the investment
        users[chat_id]["balance"] += earned
        users[chat_id]["investment"] = None
        save_users()
        bot.send_message(chat_id, f"₹{earned} has been sent to your bank account!")

# 🔹 FAQs section
def faqs(chat_id):
    faq_text = """
❓ **Frequently Asked Questions** ❓

🔹 **How do I receive my money?**  
After adding your bank account, payments are auto-transferred once the cycle ends.

🔹 **Can I upgrade my plan?**  
Yes, after completing one cycle, you can choose a higher plan.

🔹 **How long does payment verification take?**  
It is verified manually. Please be patient.

If you need help, contact **@a2elot**.
"""
    bot.send_message(chat_id, faq_text)

# 🔹 Run the bot
bot.polling(none_stop=True)
