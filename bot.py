from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

from credentials import TELEGRAM_TOKEN, OPENAI_TOKEN
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
        # Додати команду в меню можна так:
        # 'command': 'button text'

    })




chat_gpt = ChatGptService(OPENAI_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()

# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))

# Зареєструвати обробник колбеку можна так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
