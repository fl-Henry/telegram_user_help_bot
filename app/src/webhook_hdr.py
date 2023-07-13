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

        # Main Postgres configuration
        self.pg_cfg = PostgresConnectionParameters(
            dbname=config["POSTGRES_DB"],
            user=config["POSTGRES_USER"],
            password=config["POSTGRES_PASSWORD"],
            host=config["HOST"],
            port=config["DB_PORT"]
        )

        # Setting chat language
        self.lang = self.get_user_lang()
        self.text_json_all = None
        self.text_json = None
        self.get_text_json(self.lang)

        # Telegram handler
        access_token = config['ACCESS_TOKEN']
        self.tg = TelegramBotHdr(access_token)

        self.chat_id = self.get_chat_id()
        self.redirect_response()

    # # ===== From DB =================================================================================== From DB =====
    ...
    # # ===== From DB =================================================================================== From DB =====

    def get_text_json(self, lang):
        self.text_json_all = fgm.json_read(f"{dh.db_data}lang/{lang}.json")
        self.text_json = self.text_json_all.get("aft_help")

    def get_user_info(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info_list = pg.select(
            "user_info",
            columns=["id", "is_bot", "first_name", "last_name", "username", "chosen_lang"],
            sql_conditions=f"WHERE id={user_id}"
        )
        pg.close()
        return user_info_list

    def get_user_lang(self):
        user_info = self.get_message_user_info()
        try:
            chosen_lang = self.get_user_info(user_info["id"])[0]["chosen_lang"]
        except:
            chosen_lang = "en"
        return chosen_lang

    # # ===== To DB ======================================================================================= To DB =====
    ...
    # # ===== To DB ======================================================================================= To DB =====

    def update_lang(self, chosen_lang: str):
        user_info = self.get_message_user_info()
        chosen_lang = self.text_json.get("eng")[int(chosen_lang)][1]
        self.lang = chosen_lang
        self.get_text_json(self.lang)
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("user_info", {"chosen_lang": chosen_lang}, f"WHERE id={user_info['id']}")
        pg.close()

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
            "answered": "false",
        }
        pg.insert_one("messages", messages_data)
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

        message = str(self.response.get("callback_query").get("data"))

        message += f"+{self.text_json.get('/start').get('first_questions').get(message.split('/')[-1])}"
        messages_data = {
            "user_id": user_info["id"],
            "message": message,
            "answered": "false",
        }
        pg.insert_one("messages", messages_data)
        pg.close()

    def mark_msgs_as_answered(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("messages", {"answered": True}, f"WHERE user_id={user_id}")
        pg.close()
        return True

    def mark_user_as_answered(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("user_info", {"answered": True}, f"WHERE id={user_id}")
        pg.close()

    def delete_user_data(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.delete_rows("messages", f"WHERE user_id={user_id}")
        pg.delete_rows("user_info", f"WHERE id={user_id}")
        pg.close()

    # # ===== Parse message ======================================================================= Parse message =====
    ...
    # # ===== Parse message ======================================================================= Parse message =====

    def get_message_user_info(self):
        """
        :return: {
          "id": 6221817501,                       \n
          "is_bot": false,                        \n
          "first_name": "Henry",                  \n
          "last_name": "Guildman",                \n
          "username": "Henry_guildman",           \n
          "language_code": "en"                   \n
        },
        """
        if self.response.get("message") is None:
            if self.response.get("callback_query") is None:
                return None
            else:
                return self.response.get("callback_query").get("from")
        else:
            return self.response.get("message").get("from")

    def get_chat_id(self):
        if self.response.get("message") is None:
            if self.response.get("callback_query") is None:
                return None
            else:
                return self.response.get("callback_query").get("message").get("chat").get("id")
        else:
            return self.response.get("message").get("chat").get("id")

    # # ===== Telegram responses to a user ========================================= Telegram responses to a user =====
    ...
    # # ===== Telegram responses to a user ========================================= Telegram responses to a user =====

    def send_first_questions(self, question_num, entrypoint):
        """

        :param question_num: str    | "01", "02" ...
        :param entrypoint:
        :return:
        """

        buttons = self.tg.build_inline_buttons(
            self.text_json.get("/start").get("first_questions_prompt").get(question_num),
            entrypoint
        )

        keys_markup = self.tg.build_buttons_markup(buttons, 2, "inline_keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/start").get("first_questions").get(question_num),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def after_first_questions(self):
        entrypoint = "/start"
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get(entrypoint).get("after_first_questions"),
        }
        self.tg.send_message(json_data)

        return True

    def restart(self):
        user_info = self.get_message_user_info()
        self.delete_user_data(user_info["id"])
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/restart"),
        }
        self.tg.send_message(json_data)

        self.start()

    def close(self):
        user_info = self.get_message_user_info()
        self.mark_msgs_as_answered(user_info["id"])
        self.mark_user_as_answered(user_info["id"])

        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/close"),
        }
        self.tg.send_message(json_data)

    def end(self):
        user_info = self.get_message_user_info()
        self.delete_user_data(user_info["id"])

        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/end"),
        }
        self.tg.send_message(json_data)

    def help(self):
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/help"),
        }
        self.tg.send_message(json_data)

        return True

    def greetings(self):
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/start").get("text"),
        }
        self.tg.send_message(json_data)
        self.send_first_questions("01", "/start/first_questions/01")

    def start(self):
        entrypoint = "/start/first_questions/00"
        self.send_first_questions("00", entrypoint)

    # # ===== Redirection =========================================================================== Redirection =====
    ...
    # # ===== Redirection =========================================================================== Redirection =====

    def check_for_commands(self, message):
        entrypoint_str: str = message[:gm.find_char_index(message, "?")]

        if entrypoint_str[0] == "/":
            entrypoint = entrypoint_str.split("/")[1:]
            match entrypoint[0]:

                case "start":

                    # If there is anything else after /start/...
                    if len(entrypoint) > 1:
                        match "/".join(entrypoint[1:]).split("?")[0]:

                            case "first_questions/00":
                                self.save_callback_data()
                                self.update_lang(message[gm.find_char_index(message, "?")+1:])
                                self.greetings()

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

                case "help":
                    self.help()

                case "restart":
                    self.restart()

                case "close":
                    self.close()

                case "end":
                    self.end()

                case "lang":
                    self.lang()

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



