import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')