from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters

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
    text = load_message('random')
    await send_text(update, context, text)

    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt, '')

    await send_text_buttons(update, context, answer, {
        'random': 'Хочу ще факт 🧠',
        'start': 'Закінчити'
    })
async def gpts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    text = load_message('gpt')
    await send_text(update, context, text)
    context.user_data['mode'] = 'gpt'


async def gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')

    if mode == 'gpt':
        prompt = load_prompt('gpt')
        answer = await chat_gpt.send_question(prompt, update.message.text)
    elif mode == 'talk':
        answer = await chat_gpt.add_message(update.message.text)
    else:
        answer = 'Виберіть режим з меню'

    await send_text(update, context, answer)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'talk')
    text = load_message('talk')
    await send_text_buttons(update, context, text, {
        'talk_cobain': 'Курт Кобейн 🎸',
        'talk_hawking': 'Стівен Хокінг 🔭',
        'talk_nietzsche': 'Фрідріх Ніцше 📖',
        'talk_queen': 'Королева Єлизавета 👑',
        'talk_tolkien': 'Джон Толкін 🧙',
    })
    context.user_data['mode'] = 'talk'

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'quiz')
    text = load_message('quiz')
    await send_text_buttons(update, context, text, {
        'quiz_prog': 'Програмування 🐍',
        'quiz_math': 'Математика ⨊',
        'quiz_biology': 'Біологія 🧬',
        'quiz_universe': 'Всесвіт 🌌',
    })

chat_gpt = ChatGptService(OPENAI_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpts))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_message))

async def random_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await random(update, context)
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update, context)

async def talk_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    personality = update.callback_query.data
    prompt = load_prompt(personality)
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, personality)
    await send_text(update, context, 'Вітаю! Задавай питання 👇')
    context.user_data['mode'] = 'talk'

async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    topic = update.callback_query.data
    context.user_data['mode'] = 'quiz'
    context.user_data['quiz_topic'] = topic
    context.user_data['quiz_score'] = 0

    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(prompt)

    question = await chat_gpt.add_message(f'Тема: {topic}. Задай питання.')
    await send_text(update, context, question)

app.add_handler(CallbackQueryHandler(random_callback, pattern='^random$'))
app.add_handler(CallbackQueryHandler(start_callback, pattern='^start$'))
app.add_handler(CallbackQueryHandler(talk_callback, pattern='^talk_'))
app.add_handler(CallbackQueryHandler(quiz_callback, pattern='^quiz_'))
app.add_handler(CallbackQueryHandler(default_callback_handler))

app.run_polling()


