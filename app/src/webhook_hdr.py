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

    def tg_build_response(self):
        pass

    # # ===== Get from DB =========================================================================== Get from DB =====
    ...
    # # ===== Get from DB =========================================================================== Get from DB =====

    def check_staff_user(self):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        staff_info_list = pg.select("staff_info")
        pg.close()

        # TODO lowercase
        for staff_info in staff_info_list:
            if self.response.get("message").get("from").get("username") in staff_info:
                return True

        return False

    # # ===== Save to DB ============================================================================= Save to DB =====
    ...
    # # ===== Save to DB ============================================================================= Save to DB =====

    def save_message_data(self):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info = {
            "id": self.response.get("message").get("from").get("id"),
            "is_bot": self.response.get("message").get("from").get("is_bot"),
            "first_name": self.response.get("message").get("from").get("first_name"),
            "last_name": self.response.get("message").get("from").get("last_name"),
            "username": self.response.get("message").get("from").get("username"),
            "language_code": self.response.get("message").get("from").get("language_code"),
        }
        pg.insert_one("user_info", user_info)

        messages_data = {
            "user_id": user_info["id"],
            "message": self.response.get("message").get("text"),
            "responded": "false",
        }
        pg.insert_one("messages", messages_data)

        pg.commit()
        pg.close()

    def save_callback_data(self):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info = {
            "id": self.response.get("callback_query").get("from").get("id"),
            "is_bot": self.response.get("callback_query").get("from").get("is_bot"),
            "first_name": self.response.get("callback_query").get("from").get("first_name"),
            "last_name": self.response.get("callback_query").get("from").get("last_name"),
            "username": self.response.get("callback_query").get("from").get("username"),
            "language_code": self.response.get("callback_query").get("from").get("language_code"),
        }
        pg.insert_one("user_info", user_info)

        messages_data = {
            "user_id": user_info["id"],
            "message": self.response.get("callback_query").get("data"),
            "responded": "false",
        }
        pg.insert_one("messages", messages_data)

        pg.commit()
        pg.close()

    # # ===== Telegram responses to a user ========================================= Telegram responses to a user =====
    ...
    # # ===== Telegram responses to a user ========================================= Telegram responses to a user =====

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

        keys_markup = self.tg.build_buttons_markup(buttons, 2, "inline_keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get("/start").get("first_questions").get(question_num),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def after_first_questions(self):
        entrypoint = "/start"
        self.save_callback_data()
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

    def next_user(self):
        if self.check_staff_user():
            print("Success")
        else:
            print("Fail")

    # # ===== Redirection =========================================================================== Redirection =====
    ...
    # # ===== Redirection =========================================================================== Redirection =====

    def get_chat_id(self):
        if self.response.get("message") is None:
            if self.response.get("callback_query") is None:
                return None
            else:
                return self.response.get("callback_query").get("message").get("chat").get("id")
        else:
            return self.response.get("message").get("chat").get("id")

    def check_for_commands(self, message):
        entrypoint_str: str = message[:gm.find_char_index(message, "?")]

        if entrypoint_str[0] == "/":
            entrypoint = entrypoint_str.split("/")[1:]
            match entrypoint[0]:

                case "start":

                    # If there is anything else after /start/...
                    if len(entrypoint) > 1:
                        match "/".join(entrypoint[1:]).split("?")[0]:

                            case "first_questions/01":
                                self.save_callback_data()
                                self.send_first_questions("02", gm.url_parent(entrypoint_str)+"02")

                            case "first_questions/02":
                                self.save_callback_data()
                                self.send_first_questions("03", gm.url_parent(entrypoint_str)+"03")

                            case "first_questions/03":
                                self.save_callback_data()
                                self.after_first_questions()

                            case _:
                                print("Unknown command:", message)

                    # If command is /start
                    else:
                        self.start()

                case "next_user":
                    self.next_user()

                case _:
                    print("Unknown command:", message)

        else:
            self.save_message_data()

    def redirect_response(self):

        print(self.response)
        print()
        if self.response.get("message") is not None:
            self.check_for_commands(self.response.get("message").get("text"))

        if self.response.get("callback_query") is not None:
            self.check_for_commands(self.response.get("callback_query").get("data"))



