import app
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

from credentials import TELEGRAM_TOKEN, OPENAI_TOKEN
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)


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
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'random')
    await send_text(update, context, text)

    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt, '')

    await send_text_buttons(update, context, answer, {
        'random': 'Хочу ще факт 🧠',
        'start': 'Закінчити'
    })

chat_gpt = ChatGptService(OPENAI_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
text = load_message('random')
async def random_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await random(update, context)
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update, context)

app.add_handler(CallbackQueryHandler(random_callback, pattern='^random$'))
app.add_handler(CallbackQueryHandler(start_callback, pattern='^start$'))
app.add_handler(CallbackQueryHandler(default_callback_handler))

app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()


app.run_polling()

