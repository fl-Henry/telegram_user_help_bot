# ./app/webhook_set.py
from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr


config = dotenv_values(".env")

# Webhook setting
ACCESS_TOKEN = config['ACCESS_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']

tg = TelegramBotHdr(ACCESS_TOKEN)
tg.set_webhook(WEBHOOK_URL)
tg.get_webhook_info()

# Webhook adm setting
ACCESS_ADM_TOKEN = config['ACCESS_ADM_TOKEN']
WEBHOOK_ADM_URL = config['WEBHOOK_ADM_URL']

tg = TelegramBotHdr(ACCESS_ADM_TOKEN)
tg.set_webhook(WEBHOOK_ADM_URL)
tg.get_webhook_info()

