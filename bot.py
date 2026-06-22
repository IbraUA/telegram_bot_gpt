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
        'quiz': 'Взяти участь у квізі ❓',
        'translator': 'Перекласти на бажану мову',
        'vocab': 'Мовний тренажер',
    })

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('random')
    await send_text(update, context, text)

    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt, 'Розкажи цікавий факт')

    await send_text_buttons(update, context, answer, {
        'random': 'Хочу ще факт 🧠',
        'start': 'Закінчити'
    })

async def gpts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    text = load_message('gpt')
    await send_text(update, context, text)
    context.user_data['mode'] = 'gpt'

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

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'translator')
    text = load_message('translator')
    await send_text_buttons(update, context, text, {
        'eng': "Вибрати переклад на англійську",
        'ger': "Вибрати переклад на німецьку",
        'esp': "Вибрати переклад на Іспанську",
    })

async def vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'vocab')
    prompt = load_prompt('vocab')
    answer = await chat_gpt.send_question(prompt, 'дай будь ласка нове слово для вивчення')
    if 'words' not in context.user_data:
        context.user_data['words'] = []
    context.user_data['words'].append(answer)
    await send_text_buttons(update, context, answer, {
        'next_word': "Хочу ще слово",
        'train_words': "Давай перевіримо, що ми вивчили!",
        'start': "Закінчити",
    })

chat_gpt = ChatGptService(OPENAI_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

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

async def gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    if mode == 'gpt':
        prompt = load_prompt('gpt')
        answer = await chat_gpt.send_question(prompt, update.message.text)
        await send_text(update, context, answer)

    elif mode == 'talk':
        answer = await chat_gpt.add_message(update.message.text)
        await send_text(update, context, answer)


    elif mode == 'quiz':
        score = context.user_data.get('quiz_score', 0)
        answer = await chat_gpt.add_message(update.message.text)
        if "Правильно" in answer:
            score += 1
        context.user_data['quiz_score'] = score

        await send_text_buttons(update, context, answer + f"\n\nРахунок: {score}", {
            'quiz_next': '➡️ Ще питання',
            'quiz_change': '🔄 Змінити тему',
            'start': '❌ Закінчити',
        })

    elif mode == 'vocab':
        index = context.user_data.get('train_index', 0)
        words = context.user_data.get('words', [])
        current_word = words[index]
        answer = await chat_gpt.add_message(
            f'Слово для перекладу: "{current_word}". Моя відповідь: "{update.message.text}". Перевір правильність.'
        )
        await send_text(update, context, answer)
        context.user_data['train_index'] = index + 1
        if index + 1 < len(words):
            next_question = await chat_gpt.add_message(
                'Задай наступне питання по іншому слову зі списку, але не показуй переклад — я маю вгадати'
            )
            await send_text(update, context, next_question)
        else:
            await send_text_buttons(update, context, 'Тренування завершено!', {
                'train_words': ' Тренуватись знову',
                'start': ' Закінчити',
            })

    elif mode == 'translator':
        answer = await chat_gpt.add_message(update.message.text)
        await send_text_buttons(update, context, answer, {
            'lang_change': 'Змінити мову',
            'start': '❌ Закінчити',
        })

    else:
        await send_text(update, context, 'Виберіть режим з меню')



async def translator_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    language = update.callback_query.data
    prompt = load_prompt(f"{language}")
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, language)
    await send_text(update, context, 'Вітаю!  Пиши тут, що ти хочеш перекласти 👇')
    context.user_data['mode'] = 'translator'

async def quiz_next_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    topic = context.user_data.get('quiz_topic')
    question = await chat_gpt.add_message('Задай наступне питання з тієї ж теми.')
    await send_text(update, context, question)

async def quiz_change_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await quiz(update, context)

async def lang_change_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text = load_message('translator')
    await send_text_buttons(update, context, text, {
        'eng': "Вибрати переклад на англійську",
        'ger': "Вибрати переклад на німецьку",
        'esp': "Вибрати переклад на Іспанську",
    })

async def next_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    question = await chat_gpt.add_message('Давай наступне слово для вивчення')
    context.user_data['words'].append(question)
    await send_text_buttons(update, context, question, {
        'next_word': "Хочу ще слово",
        'train_words': "Давай нових слів, потренуємось",
        'start': "Закінчити",
    })

async def train_words_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    chat_gpt.set_prompt(load_prompt('vocab'))
    if not context.user_data.get('words'):
        await send_text(update, context, 'Спочатку вивчи хоча б одне слово!')
        return
    context.user_data['train_index'] = 0
    context.user_data['mode'] = 'vocab'
    words = context.user_data.get('words', [])
    words_text = '\n'.join(words)
    question = await chat_gpt.add_message(
        f'Ось слова які ми вчили:\n{words_text}\n\nЗадай мені питання по одному з цих слів, але не показуй переклад — я маю сам його вгадати'
    )
    await send_text(update, context, question)
    await update.callback_query.answer()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpts))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('translator', translator))
app.add_handler(CommandHandler('vocab', vocab))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_message))
app.add_handler(CallbackQueryHandler(quiz_next_callback, pattern='^quiz_next$'))
app.add_handler(CallbackQueryHandler(random_callback, pattern='^random$'))
app.add_handler(CallbackQueryHandler(start_callback, pattern='^start$'))
app.add_handler(CallbackQueryHandler(talk_callback, pattern='^talk_'))
app.add_handler(CallbackQueryHandler(quiz_change_callback, pattern='^quiz_change$'))
app.add_handler(CallbackQueryHandler(quiz_callback, pattern='^quiz_'))
app.add_handler(CallbackQueryHandler(translator_callback, pattern='^eng$'))
app.add_handler(CallbackQueryHandler(translator_callback, pattern='^ger$'))
app.add_handler(CallbackQueryHandler(translator_callback, pattern='^esp$'))
app.add_handler(CallbackQueryHandler(lang_change_callback, pattern='^lang_change$'))
app.add_handler(CallbackQueryHandler(train_words_callback, pattern='^train_words$'))
app.add_handler(CallbackQueryHandler(next_word_callback, pattern='^next_word$'))
app.add_handler(CallbackQueryHandler(default_callback_handler))

app.run_polling()


