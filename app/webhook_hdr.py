# ./app/webhook_hdr.py
import sys

from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr


config = dotenv_values(".env")
ACCESS_TOKEN = config['ACCESS_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']

tg = TelegramBotHdr(ACCESS_TOKEN)


class WebhookHdr:

    def __init__(self, response):
        self.result = True
        self.response = response
        self.redirect_response(self.response)

    def redirect_response(self, response):
        print(response)
