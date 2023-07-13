# ./app/webhook_delete.py
from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr


config = dotenv_values(".env")

# Webhook deleting
ACCESS_TOKEN = config['ACCESS_TOKEN']

tg = TelegramBotHdr(ACCESS_TOKEN)
tg.delete_webhook()

# Webhook adm deleting
ACCESS_ADM_TOKEN = config['ACCESS_ADM_TOKEN']

tg = TelegramBotHdr(ACCESS_ADM_TOKEN)
tg.delete_webhook()
