# ./app/webhook_hdr.py
import sys

from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr
from postgresql_hdr import PostgresqlHdr, PostgresConnectionParameters
from general_methods import files_gm as fgm
from general_methods import gm


dh = fgm.DirectoriesHandler()
config = dotenv_values(dh.dotenv)


class WebhookHdr:

    def __init__(self, response):
        self.result = True
        self.response = response

        # TODO: add langs
        self.lang = "ru"
        self.answers = fgm.json_read(f"{dh.db_data}lang/{self.lang}.json")

        # Main Postgres configuration
        self.pg_cfg = PostgresConnectionParameters(
            dbname=config["POSTGRES_DB"],
            user=config["POSTGRES_USER"],
            password=config["POSTGRES_PASSWORD"],
            host=config["HOST"],
            port=config["DB_PORT"]
        )

        # Telegram handler
        access_token = config['ACCESS_TOKEN']
        self.tg = TelegramBotHdr(access_token)

        self.chat_id = self.get_chat_id()
        self.redirect_response()

    def save_to_db(self):

        def save_user_info(user_info):
            pg_hdr = PostgresqlHdr(self.pg_cfg)

            command = """
            """

            pg_hdr.commit()
            pg_hdr.close()

        if self.response.get("message") is not None:
            if self.response.get("from") is not None:
                save_user_info(self.response.get("from"))

    def tg_build_response(self):
        pass

    def send_first_questions(self, question_num, entrypoint):
        """

        :param question_num: str    | "01", "02" ...
        :param entrypoint:
        :return:
        """
        buttons = self.tg.build_buttons(
            self.answers.get("/start").get("first_questions_prompt").get(question_num),
            entrypoint
        )
        print("Buttons:", buttons)
        keys_markup = self.tg.build_buttons_markup(buttons, 2, "inline_keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get("/start").get("first_questions").get(question_num),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def after_first_questions(self):
        entrypoint = "/start"
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get(entrypoint).get("after_first_questions"),
        }
        self.tg.send_message(json_data)

        return True

    def start(self):
        entrypoint = "/start"
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get(entrypoint).get("text"),
        }
        self.tg.send_message(json_data)

        entrypoint = "/start/first_questions/01"
        self.send_first_questions("01", entrypoint)

        return True

    def check_for_commands(self, message):
        entrypoint = message[:gm.find_char_index(message, "?")]

        print("\n", entrypoint)
        match entrypoint:
            case "/start":
                return self.start()

            case "/start/first_questions/01":
                return self.send_first_questions("02", gm.url_parent(entrypoint)+"02")

            case "/start/first_questions/02":
                return self.send_first_questions("03", gm.url_parent(entrypoint)+"03")

            case "/start/first_questions/02":
                return self.send_first_questions("03", gm.url_parent(entrypoint)+"03")

            case "/start/first_questions/03":
                return self.after_first_questions()

            case _:
                print("Not command:", message)

    def get_chat_id(self):
        if self.response.get("message") is None:
            if self.response.get("callback_query") is None:
                return None
            else:
                return self.response.get("callback_query").get("message").get("chat").get("id")
        else:
            return self.response.get("message").get("chat").get("id")

    def redirect_response(self):
        if self.response.get("message") is not None:
            func = self.check_for_commands(self.response.get("message").get("text"))

        if self.response.get("callback_query") is not None:
            self.check_for_commands(self.response.get("callback_query").get("data"))



