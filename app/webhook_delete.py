# ./app/webhook_delete.py
from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr


config = dotenv_values(".env")
ACCESS_TOKEN = config['ACCESS_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']

tg = TelegramBotHdr(ACCESS_TOKEN)
tg.delete_webhook()

