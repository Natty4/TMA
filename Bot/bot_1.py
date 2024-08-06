import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Define your bot token here
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Define your Mini App URL here
MINI_APP_URL = os.getenv('MINI_APP_URL')
# Define your feedback URL here
FEEDBACK_URL = os.getenv('FEEDBACK_URL')
APPOINTMENTS_URL = os.getenv('APPOINTMENTS_URL')

# Start command handler
# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Launch Mini App", url=MINI_APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! Click the button below to launch the Mini App.', reply_markup=reply_markup)

# Support command handler
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    response = requests.get(APPOINTMENTS_URL)
    if response:
        data = response.json()
        if not data['appointments']:
            await update.message.reply_text('No completed appointments yet.')
            return

        keyboard = [
            [InlineKeyboardButton(f"{appt['service__name']} {[appt['id']]} with {appt['doctor__full_name']}", callback_data=f"rate_{appt['id']}")]
            for appt in data['appointments']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Please select an appointment to rate:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Error fetching appointments. Please try again later.')

# Callback query handler for rating
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('rate_'):
        appointment_id = query.data.split('_')[1]
        context.user_data['appointment_id'] = appointment_id

        keyboard = [
            [InlineKeyboardButton(i*'⭐️', callback_data=f"rating_{i}")]
            for i in range(1, 6)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Please select a rating:', reply_markup=reply_markup)
    
    elif query.data.startswith('rating_'):
        rating = query.data.split('_')[1]
        context.user_data['rating'] = rating

        await query.edit_message_text('Please provide any additional comments or type "skip" to finish:')

# Generic message handler for feedback comments
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if 'appointment_id' in context.user_data and 'rating' in context.user_data:
        appointment_id = context.user_data['appointment_id']
        rating = context.user_data['rating']

        if user_message.lower() == 'skip':
            comments = ''
        else:
            comments = user_message

        response = requests.post(FEEDBACK_URL, json={'appointment_id': appointment_id, 'rating': rating, 'comments': comments})
        if response.status_code == 200:
            await update.message.reply_text('Thank you for your feedback!')
        else:
            await update.message.reply_text('Error submitting feedback. Please try again later.')
            
            

        # Clear the context user data after submission
        context.user_data.clear()

# Main function to set up the bot
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('support', support))

    # Register callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Register message handler for all other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()