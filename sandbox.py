# ./sandbox.py
import requests

from dotenv import dotenv_values

# Custom imports
from app.telegram_bot_hdr import TelegramBotHdr


config = dotenv_values("./app/.env")
ACCESS_TOKEN = config['ACCESS_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']

tg = TelegramBotHdr(ACCESS_TOKEN)


def main():
    tg.set_webhook(WEBHOOK_URL)
    tg.get_webhook_info()
    tg.delete_webhook()
    tg.get_webhook_info()


if __name__ == '__main__':
    main()
