# ./app/webhook_adm_bot_hdr.py
import json
from sys import exit as sx
from dotenv import dotenv_values

# Custom imports
from telegram_bot_hdr import TelegramBotHdr
from postgresql_hdr import PostgresqlHdr, PostgresConnectionParameters
from general_methods import files_gm as fgm
from general_methods import gm


dh = fgm.DirectoriesHandler()
config = dotenv_values(dh.dotenv)


class WebhookAdmHdr:

    def __init__(self, response):
        self.result = True
        self.response = response

        # TODO: add langs
        self.lang = "ru"
        self.answers = fgm.json_read(f"{dh.db_data}lang/{self.lang}.json")["aft_adm"]

        # Main Postgres configuration
        self.pg_cfg = PostgresConnectionParameters(
            dbname=config["POSTGRES_DB"],
            user=config["POSTGRES_USER"],
            password=config["POSTGRES_PASSWORD"],
            host=config["HOST"],
            port=config["DB_PORT"]
        )

        # Telegram handler
        access_token = config['ACCESS_ADM_TOKEN']
        self.tg = TelegramBotHdr(access_token)

        self.chat_id = self.get_chat_id()
        self.redirect_response()

    # # ===== Get from DB =========================================================================== Get from DB =====
    ...
    # # ===== Get from DB =========================================================================== Get from DB =====

    def check_staff_user(self):
        # Get staff_info from DB
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        staff_info_list = pg.select("staff_info")
        pg.close()

        # Check if there is user in staff_info
        user_name = self.get_message_user_info().get("username").lower()
        for staff_info in staff_info_list:
            if user_name == str(staff_info["staff_account"]).lower():
                return True

        return False

    def get_user_first_questions(self, user_id):
        """
        :return: ["message", ...]
        """
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_messages_list = pg.select(
            "messages",
            columns=["message"],
            sql_conditions=f"WHERE (user_id={user_id} "
                           f"AND POSITION('/start/first_questions' IN message)>0)"
        )
        pg.close()

        for x in user_messages_list:
            print(x)

        return user_messages_list

    def get_user_messages(self):
        """
        :return:
        """

        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info_list = pg.select(
            "user_info",
            columns=["id", "is_bot", "first_name", "last_name", "username"],
            sql_conditions=f"WHERE answered=false"
        )
        pg.close()

        return user_info_list

    def get_unsolved_user_info(self):
        """
            Get user_info for users who have unsolved questions
        :return: [{
                    "id": x[0],
                    "is_bot": x[1],
                    "first_name": x[2],
                    "last_name": x[3],
                    "username": x[4],
                }, ... ]
        """
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info_list = pg.select(
            "user_info",
            columns=["id", "is_bot", "first_name", "last_name", "username", "chosen_lang"],
            sql_conditions=f"WHERE answered=false"
        )
        pg.close()
            
        return user_info_list

    # # ===== Save to DB ============================================================================= Save to DB =====
    ...
    # # ===== Save to DB ============================================================================= Save to DB =====
    #
    # def save_message_data(self):
    #     pg = PostgresqlHdr(pcp=self.pg_cfg)
    #     user_info = {
    #         "id": self.response.get("message").get("from").get("id"),
    #         "is_bot": self.response.get("message").get("from").get("is_bot"),
    #         "first_name": self.response.get("message").get("from").get("first_name"),
    #         "last_name": self.response.get("message").get("from").get("last_name"),
    #         "username": self.response.get("message").get("from").get("username"),
    #         "language_code": self.response.get("message").get("from").get("language_code"),
    #     }
    #     pg.insert_one("user_info", user_info)
    #
    #     messages_data = {
    #         "user_id": user_info["id"],
    #         "message": self.response.get("message").get("text"),
    #         "answered": "false",
    #     }
    #     pg.insert_one("messages", messages_data)
    #
    #     pg.commit()
    #     pg.close()
    #
    # def save_callback_data(self):
    #     pg = PostgresqlHdr(pcp=self.pg_cfg)
    #     user_info = {
    #         "id": self.response.get("callback_query").get("from").get("id"),
    #         "is_bot": self.response.get("callback_query").get("from").get("is_bot"),
    #         "first_name": self.response.get("callback_query").get("from").get("first_name"),
    #         "last_name": self.response.get("callback_query").get("from").get("last_name"),
    #         "username": self.response.get("callback_query").get("from").get("username"),
    #         "language_code": self.response.get("callback_query").get("from").get("language_code"),
    #     }
    #     pg.insert_one("user_info", user_info)
    #
    #     messages_data = {
    #         "user_id": user_info["id"],
    #         "message": self.response.get("callback_query").get("data"),
    #         "answered": "false",
    #     }
    #     pg.insert_one("messages", messages_data)
    #
    #     pg.commit()
    #     pg.close()

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
        user_info = self.response.get("message").get("from")
        if user_info is not None:
            return user_info
        else:
            gm.PrintMode.error("get_message_user_info() returns None")
            return None

    def get_chat_id(self):
        if self.response.get("message") is None:
            if self.response.get("callback_query") is None:
                return None
            else:
                return self.response.get("callback_query").get("message").get("chat").get("id")
        else:
            return self.response.get("message").get("chat").get("id")

    # # ===== Bot responses ======================================================================= Bot responses =====
    ...
    # # ===== Bot responses ======================================================================= Bot responses =====

    def send_unknown(self):
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get("unknown_cmd").get("text"),
        }
        self.tg.send_message(json_data)

    def send_main_buttons(self):
        buttons = self.tg.build_keyboard_button(self.answers.get("/main_kb").get("buttons"))
        keys_markup = self.tg.build_buttons_markup(buttons, 1, "keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get("/main_kb").get("text"),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def start(self):
        json_data = {
            "chat_id": self.chat_id,
            "text": self.answers.get("unknown_cmd").get("text"),
        }
        self.tg.send_message(json_data)

    def adm_authenticate(self):
        # TODO Timer to log out
        self.send_main_buttons()

    def main_kb(self):
        self.adm_authenticate()

    def next_user(self):
        # TODO

        # Get user_info for users that have unsolved questions
        user_info_list = self.get_unsolved_user_info()
        for user_info in user_info_list:
            messages = []

            # Get answers on the first auto questions
            user_first_questions = self.get_user_first_questions(user_info["id"])

            # Get custom user questions/messages
            # user_messages = self.get_user_messages()

            # TODO:
            # if len(messages) == 0:
            #     self.mark_user_as_answered(user_info["id"])
            # else:
            #     break

    def get_lost_count(self):
        # Get user_info for users that have unsolved questions
        user_info_list = self.get_unsolved_user_info()

        # Build an answer to send to the chat
        placeholders = {
            "users_number": len(user_info_list),
        }
        text = str(self.answers.get("/get_lost_count")).format(**placeholders)
        json_data = {
            "chat_id": self.chat_id,
            "text": text,
        }
        self.tg.send_message(json_data)

    # # ===== Redirection =========================================================================== Redirection =====
    ...
    # # ===== Redirection =========================================================================== Redirection =====

    def check_buttons(self, message):
        main_kb_asw = self.answers.get("main_kb_asw")
        for row in main_kb_asw:
            if message == row[0]:
                exec(row[2])
                return True
        return False

    def check_for_commands(self, message):
        entrypoint_str: str = message[:gm.find_char_index(message, "?")]

        if entrypoint_str[0] == "/":

            entrypoint = entrypoint_str[1:]
            match entrypoint:

                case "start":
                    self.start()

                case "adm_authenticate":
                    self.adm_authenticate()

                case "main_kb":
                    self.main_kb()

                case "next_user":
                    self.next_user()

                case "get_lost_count":
                    self.get_lost_count()

                case _:
                    print("Unknown command:", message)

        else:
            if not self.check_buttons(message):
                self.send_unknown()

    def redirect_response(self):

        print(self.response)
        print()

        if self.check_staff_user():
            print("[OK] Authentication succeeded")
            if self.response.get("message") is not None:
                self.check_for_commands(self.response.get("message").get("text"))

            if self.response.get("callback_query") is not None:
                self.check_for_commands(self.response.get("callback_query").get("data"))
        else:
            print("\n\n\n[WARNING] Authentication failed ^^^^^^^^^^^")

