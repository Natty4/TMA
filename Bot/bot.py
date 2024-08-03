import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests



load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = "http://localhost:8000/get_appointments"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Book Appointment", callback_data='book')],
        [InlineKeyboardButton("View Appointments", callback_data='view')],
        [InlineKeyboardButton("Submit Feedback", callback_data='feedback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the Dental Clinic Appointment Bot!', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'book':
        # keyboard to launch the mini app to book an appointment
        keyboard = [[{'text': 'Book an Appointment', 'url': URL}]]
        reply_markup = {'inline_keyboard': keyboard}
        await query.edit_message_text(text='Click the button below to book an appointment', reply_markup=reply_markup)
        
    elif query.data == 'view':
        user_email = 'Johnd@email.com'
        response = requests.get(f'{URL}/{user_email}/')
        if response.status_code == 200:
            appointments = response.json().get('appointments', [])
            message = "Your Appointments:\n\n"
            for appointment in appointments:
                message += f"Service: {appointment['service__name']}\nDoctor: {appointment['doctor__full_name']}\nDate: {appointment['date']}\nTime: {appointment['time']}\nStatus: {appointment['status']}\n\n"
            await query.edit_message_text(text=message)
        else:
            await query.edit_message_text(text="Error fetching appointments.")
    elif query.data == 'feedback':
        await query.edit_message_text(text="Please visit our web page to submit feedback: [URL]")

# Function to send reminder notifications
async def send_reminder_notification(user_id: int, message: str):
    context = ContextTypes.DEFAULT_TYPE
    await context.bot.send_message(chat_id=user_id, text=message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()










# import os
# import logging
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# load_dotenv()

# BOT_TOKEN = os.getenv('BOT_TOKEN')

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text('Welcome to the Dental Clinic Appointment Bot\n\n'
#                                     'You can book an appointment by typing /book')

# async def book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     URL = os.getenv('URL')
#     # open the web page to book an appointment inline keyboard button
#     keyboard = [[{'text': 'Book an Appointment', 'url': URL}]]
#     reply_markup = {'inline_keyboard': keyboard}
    
#     await update.message.reply_text('Click the button below to book an appointment', reply_markup=reply_markup)

# if __name__ == '__main__':
#     application = ApplicationBuilder().token(BOT_TOKEN).build()

#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CommandHandler('book', book))

#     application.run_polling()