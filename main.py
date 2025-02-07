from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# User data storage (Replace this with a database in real use)
user_data = {}

# Define VIP levels based on investment amounts
VIP_STATUS = {
    '399': 'VIP 1', '599': 'VIP 2', '999': 'VIP 3', '1999': 'VIP 4', '9999': 'VIP 5'
}

SMART_PACKAGES = {
    'Package 1': {'price': 99, 'return': 299},
    'Package 2': {'price': 299, 'return': 599},
    'Package 3': {'price': 499, 'return': 999},
    'Package 4': {'price': 999, 'return': 1999},
    'Package 5': {'price': 1999, 'return': 3999},
    'Package 6': {'price': 4999, 'return': 9999},
    'Package 7': {'price': 9999, 'return': 29999}
}

LONG_TERM_PACKAGES = {
    'Starter Plan': {'price': 399, 'duration': 40, 'daily_return': 133},
    'LT Smart Plan': {'price': 599, 'duration': 60, 'daily_return': 233},
    'Elite Plan': {'price': 999, 'duration': 40, 'daily_return': 424},
    'Premium Plan': {'price': 1999, 'duration': 30, 'daily_return': 999},
    'Great Package': {'price': 9999, 'duration': 30, 'daily_return': 2666}
}

# Start command
async def start(update, context):
    user = update.message.from_user
    user_data[user.id] = {'name': user.first_name, 'investments': [], 'vip_status': None}
    
    keyboard = [
        [InlineKeyboardButton("📈 Smart Packages", callback_data='smart_packages')],
        [InlineKeyboardButton("⏳ Long Term Packages", callback_data='long_term_packages')],
        [InlineKeyboardButton("📊 Track Progress", callback_data='track_progress')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='contact_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Welcome {user.first_name}! Start your investment journey with us.", reply_markup=reply_markup)

# Handle button clicks
async def button(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == 'smart_packages':
        show_smart_packages(query)
    elif query.data == 'long_term_packages':
        show_long_term_packages(query)
    elif query.data == 'track_progress':
        show_progress(query, user)
    elif query.data == 'contact_support':
        await query.edit_message_text(text="📞 Contact Support:\nEmail: elivexinvest@gmail.com\nTelegram: @a2elot")

# Show smart packages
async def show_smart_packages(query):
    keyboard = []
    for package, details in SMART_PACKAGES.items():
        price = details['price']
        keyboard.append([InlineKeyboardButton(f"{package} - ₹{price}", callback_data=f"pay_smart_{price}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="💰 Choose a Smart Package to invest in:", reply_markup=reply_markup)

# Show long-term packages
async def show_long_term_packages(query):
    keyboard = []
    for package, details in LONG_TERM_PACKAGES.items():
        price = details['price']
        duration = details['duration']
        keyboard.append([InlineKeyboardButton(f"{package} - ₹{price} for {duration} days", callback_data=f"pay_long_{price}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="💰 Choose a Long-Term Package to invest in:", reply_markup=reply_markup)

# Show payment gateway with your correct UPI ID
async def payment_gateway(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    package_type = data[1]
    price = int(data[2])

    payment_message = (
        f"📢 To invest in this package, please make a payment of ₹{price}.\n\n"
        "✅ Payment Methods:\n"
        f"1️⃣ UPI: aielotshyam-1@oksbi\n"
        "📤 After payment, send a screenshot as proof."
    )

    user_data[query.from_user.id]['pending_payment'] = price  # Store payment amount
    await query.edit_message_text(payment_message)

# Handle payment proof submission
async def receive_payment_proof(update, context):
    user = update.message.from_user
    if user.id in user_data and 'pending_payment' in user_data[user.id]:
        price = user_data[user.id]['pending_payment']
        user_data[user.id]['vip_status'] = VIP_STATUS.get(str(price), 'VIP 1')
        del user_data[user.id]['pending_payment']  # Clear pending payment

        await update.message.reply_text(
            "✅ Payment received! Your investment has been processed.\n"
            f"🎖 VIP Status: {user_data[user.id]['vip_status']}"
        )
    else:
        await update.message.reply_text("⚠️ No pending payments found.")

# Show investment progress
async def show_progress(query, user):
    investments = user_data.get(user.id, {}).get('investments', [])
    if not investments:
        await query.edit_message_text(text="📉 You haven't made any investments yet.")
        return

    progress_message = "📊 Your Investment Progress:\n"
    for investment in investments:
        progress_message += f"\n📌 Package: {investment['package']}\n💸 Invested: ₹{investment['amount']}\n💰 Return: ₹{investment['return_value']}"

    await query.edit_message_text(progress_message)

# Back to Menu
async def back_to_menu(update, context):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Main function to start the bot
def main():
    application = Application.builder().token('7517200911:AAGUoLfnAQHiwK3u6y8prNXFCD8sIFLVb6U').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(payment_gateway, pattern='^pay_.*'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu'))
    application.add_handler(MessageHandler(filters.PHOTO, receive_payment_proof))  # Payment proof handling

    application.run_polling()  # Automatically handles the event loop for you

if __name__ == '__main__':
    main(); import something
