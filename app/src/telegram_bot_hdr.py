# ./app/telegram_bot_hdr
# TODO: admin login

# TODO: create db
#   table: users
#       rows: <all user data>
#   table: messages
#       rows: user_id/chat_id, response_json
#   table: admin_data
#       rows: username, password
#

import requests
from dotenv import dotenv_values

# Custom imports
from general_methods import gm


class TelegramBotHdr:

    def __init__(self, access_token):
        self._access_token = access_token
        self._base_url = f"https://api.telegram.org/bot{self._access_token}/"

    def endpoint_url(self, endpoint):
        return f"{self._base_url}{endpoint}"

    @staticmethod
    def _response_result(response):
        if response["ok"] is True:
            print(f"{gm.Tags.LightGreen}{gm.Tags.Bold}[OK]{gm.Tags.ResetAll} {response}")
        else:
            print(f"{gm.Tags.LightYellow}{gm.Tags.Bold}[WARNING]{gm.Tags.ResetAll} {response}")

    def set_webhook(self, webhook_url):
        endpoint = "setWebhook"
        url = self.endpoint_url(endpoint)
        params = {
            "url": webhook_url,
        }
        response = requests.post(url, params=params)
        response = response.json()
        self._response_result(response)

    def get_webhook_info(self):
        endpoint = "getWebhookInfo"
        url = self.endpoint_url(endpoint)
        response = requests.post(url).json()
        self._response_result(response)

    def delete_webhook(self):
        endpoint = "deleteWebhook"
        url = self.endpoint_url(endpoint)
        response = requests.post(url).json()
        self._response_result(response)

    def send_message(self, json_data):
        """
            https://core.telegram.org/bots/api#sendmessage
            {
                "chat_id": Integer or String,
                "text": String,
            }
        :param json_data:
        :return:
        """
        endpoint = "sendMessage"
        url = self.endpoint_url(endpoint)
        response = requests.post(url, json=json_data).json()
        self._response_result(response)
        return True

    @staticmethod
    def build_inline_buttons(options_list, entrypoint: str):
        """
            https://core.telegram.org/bots/api#inlinekeyboardmarkup
            {
                "text": String,
                "callback_data": String,
            }
        :options_list: list(str)
        :return:
        """
        return [
            {
                "text": x,
                "callback_data": f"{entrypoint}?{counter}",
            }
            for x, counter in zip(options_list, range(len(options_list)))
        ]

    @staticmethod
    def build_keyboard_button(button_text_list):
        """
        :param button_text_list:
        :return:
        """
        return [{"text": x} for x in button_text_list]

    @staticmethod
    def build_buttons_markup(buttons_list, columns_number, markup_name):
        return {
            markup_name: [x for x in gm.UrlIterator(buttons_list, columns_number)],
            "is_persistent": True,
            "resize_keyboard": True,
        }

    def inline_button(self):
        """
            https://core.telegram.org/bots/api#inlinekeyboardmarkup
            {
                "text": String,
                "callback_data": String,
            }
        :return:
        """
        pass


def main():
    config = dotenv_values(".env")
    ACCESS_TOKEN = config['ACCESS_TOKEN']
    WEBHOOK_URL = config['WEBHOOK_URL']

    tg = TelegramBot(ACCESS_TOKEN)
    tg.set_webhook(WEBHOOK_URL)
    tg.get_webhook_info()
    tg.delete_webhook()
    tg.get_webhook_info()


if __name__ == '__main__':
    main()