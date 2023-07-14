# ./app/webhook_adm_bot_hdr.py
import json

from random import randint
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
        access_token = config['ACCESS_ADM_TOKEN']
        self.tg = TelegramBotHdr(access_token)

        self.chat_id = self.get_chat_id()
        self.redirect_response()

    # # ===== Get from DB =========================================================================== Get from DB =====
    ...
    # # ===== Get from DB =========================================================================== Get from DB =====

    def get_user_lang(self):
        user_info = self.get_message_user_info()
        try:
            chosen_lang = self.get_user_info(user_info["id"])[0]["chosen_lang"]
        except:
            chosen_lang = "en"
        return chosen_lang

    def get_text_json(self, lang):
        self.text_json_all = fgm.json_read(f"{dh.db_data}lang/{lang}.json")
        self.text_json = self.text_json_all.get("aft_adm")

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

    def get_user_info(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info_list = pg.select(
            "user_info",
            columns=[
                "id",
                "is_bot",
                "first_name",
                "last_name",
                "username",
                "chosen_lang",
                "language_code",
                "is_bot",
                "in_process",
            ],
            sql_conditions=f"WHERE id={user_id}"
        )
        pg.close()
        if len(user_info_list) > 0:
            return user_info_list[0]
        else:
            return None

    def get_user_first_questions(self, user_id):
        """
        :return: str
        """
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_messages_list = pg.select(
            "messages",
            columns=["message"],
            sql_conditions=f"WHERE (user_id={user_id} "
                           f"AND POSITION('/start/first_questions' IN message)>0)"
        )
        pg.close()

        fqp = self.text_json_all.get("aft_help").get("/start").get("first_questions_prompt")

        placeholders = {x: "---" for x in fqp.keys()}
        for x in user_messages_list:
            callback = str(str(x.get('message')).split('/')[-1]).split("?")
            placeholders.update({callback[0]: fqp.get(callback[0])[int(callback[1])]})
        first_questions_text = str(self.text_json.get("get_user_first_questions")).format(**placeholders)

        return first_questions_text

    def get_user_messages(self, user_id):
        """
        :return:
        """

        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_messages_list = pg.select(
            "messages",
            columns=["message", "staff_account"],
            sql_conditions=f"WHERE (user_id={user_id} "
                           f"AND POSITION('/start' IN message)=0)"
        )
        pg.close()

        messages = ""
        for message in user_messages_list:
            if message.get("staff_account") is None:
                messages += f"<u><b>User:</b></u>\n{message['message']}\n\n"
            else:
                messages += f"<u><b>{message.get('staff_account')}:</b></u>\n{message['message']}\n\n"
        return messages

    def get_unsolved_user_info(self):
        """
            Get user_info for users who have unsolved questions
        :return: [{
                "id",
                "is_bot",
                "first_name",
                "last_name",
                "username",
                "chosen_lang",
                "language_code",
                "is_bot",
                }, ... ]
        """
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        user_info_list = pg.select(
            "user_info",
            columns=[
                "id",
                "is_bot",
                "first_name",
                "last_name",
                "username",
                "chosen_lang",
                "language_code",
                "is_bot",
                "in_process",
            ],
            sql_conditions=f"WHERE answered=false"
        )
        pg.close()

        not_in_process = [x for x in user_info_list if x["in_process"] is False]
        if len(not_in_process) > 0:
            return not_in_process
        else:
            return user_info_list

    # # ===== Save to DB ============================================================================= Save to DB =====
    ...
    # # ===== Save to DB ============================================================================= Save to DB =====

    def update_lang(self, chosen_lang: str):
        user_info = self.get_message_user_info()
        chosen_lang = self.text_json_all.get("aft_help").get("eng")[int(chosen_lang)][1]

        self.lang = chosen_lang
        self.get_text_json(self.lang)

        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("staff_info", {"chosen_lang": chosen_lang}, f"WHERE staff_account='{user_info['username']}'")
        pg.close()
        self.send_main_buttons()

    def mark_user_as_answered(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("user_info", {"answered": True}, f"WHERE id={user_id}")
        pg.update("messages", {"answered": True}, f"WHERE user_id={user_id}")
        pg.close()

    def mark_user_in_process(self, user_id):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        pg.update("user_info", {"in_process": True}, f"WHERE id={user_id}")
        pg.close()

    def save_reply_message(self, user_id, reply_message):
        pg = PostgresqlHdr(pcp=self.pg_cfg)
        staff_info = self.get_message_user_info()
        messages_data = {
            "user_id": user_id,
            "message": reply_message,
            "answered": True,
            "staff_account": staff_info.get("username"),
        }
        pg.insert_one("messages", messages_data)

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

    # # ===== Bot responses ======================================================================= Bot responses =====
    ...
    # # ===== Bot responses ======================================================================= Bot responses =====

    def send_unknown(self):
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("unknown_cmd").get("text"),
        }
        self.tg.send_message(json_data)

    def send_main_buttons(self):
        buttons = self.tg.build_keyboard_button(self.text_json.get("/main_kb").get("buttons"))
        keys_markup = self.tg.build_buttons_markup(buttons, 1, "keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": self.text_json.get("/main_kb").get("text"),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def start(self):
        # TODO
        # json_data = {
        #     "chat_id": self.chat_id,
        #     "text": self.text_json.get("unknown_cmd").get("text"),
        # }
        # self.tg.send_message(json_data)
        pass

    def adm_authenticate(self):
        # TODO Timer to log out
        self.langs()
        self.send_main_buttons()

    def main_kb(self):
        self.send_main_buttons()

    def next_user(self):
        # Get user_info for users that have unsolved questions
        user_info_list = self.get_unsolved_user_info()

        for user_info in user_info_list:

            if user_info["in_process"]:
                user_info = user_info_list[randint(0, len(user_info_list) - 1)]
                text = self.text_json.get("/next_user").get("in_process") + "\n\n"

            else:
                text = ""

            # Get answers on the first auto questions
            user_first_questions = self.get_user_first_questions(user_info["id"])

            # Get custom user questions/messages
            user_messages = self.get_user_messages(user_info["id"])

            if user_messages in ["", " ", None]:
                self.mark_user_as_answered(user_info["id"])

            else:
                user_info_str = str(self.text_json.get("/next_user").get("text")).format(**user_info)
                text += f"{user_info_str}\n\n{user_first_questions}\n\n{user_messages}"
                json_data = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                }
                self.tg.send_message(json_data)
                self.mark_user_in_process(user_info["id"])
                break

    def get_lost_count(self):
        # Get user_info for users that have unsolved questions
        user_info_list = self.get_unsolved_user_info()

        # Build an answer to send to the chat
        placeholders = {
            "users_number": len(user_info_list),
        }

        text = ""
        if placeholders["users_number"] > 0:
            if user_info_list[0]["in_process"]:
                text = self.text_json.get("/get_lost_count").get("in_process") + "\n\n"
        text += str(self.text_json.get("/get_lost_count").get("text")).format(**placeholders)

        json_data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        self.tg.send_message(json_data)

    def reply_user(self):
        text = self.text_json.get("/reply_user").get("text")
        json_data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        self.tg.send_message(json_data)

    def send_answer_message(self, message, user_id):
        if self.get_user_info(user_id):

            # To user
            access_token = config['ACCESS_TOKEN']
            tg = TelegramBotHdr(access_token)
            json_data = {
                "chat_id": user_id,
                "text": message,
            }
            tg.send_message(json_data)
            self.save_reply_message(user_id, message)
            self.mark_user_as_answered(user_id)

            # To staff (callback)
            placeholders = self.get_user_info(user_id)
            if len(message) > 70:
                placeholders.update({"message_part": message[:64] + "..."})
            else:
                placeholders.update({"message_part": message})
            text = str(self.text_json.get("send_answer_message").get("text")).format(**placeholders)

            json_data = {
                "chat_id": self.chat_id,
                "text": text,
            }
            self.tg.send_message(json_data)

        else:
            placeholders = {
                "id": user_id,
            }
            text = str(self.text_json.get("send_answer_message").get("wrong_id")).format(**placeholders)
            json_data = {
                "chat_id": self.chat_id,
                "text": text,
            }
            self.tg.send_message(json_data)

    def send_first_questions(self, question_num, entrypoint):
        start_json = self.text_json_all.get("aft_help").get("/start")
        buttons = self.tg.build_inline_buttons(
            start_json.get("first_questions_prompt").get(question_num),
            entrypoint
        )

        keys_markup = self.tg.build_buttons_markup(buttons, 2, "inline_keyboard")
        json_data = {
            "chat_id": self.chat_id,
            "text": start_json.get("first_questions").get(question_num),
            "reply_markup": keys_markup,
        }
        self.tg.send_message(json_data)

    def langs(self):
        self.send_first_questions("_00", "/start/first_questions/_00")

    # # ===== Redirection =========================================================================== Redirection =====
    ...
    # # ===== Redirection =========================================================================== Redirection =====

    def check_buttons(self, message):
        main_kb_asw = self.text_json.get("main_kb_asw")
        for row in main_kb_asw:
            if message == row[0]:
                exec(row[2])
                return True

        return False

    def check_reply_user(self, message):
        try:
            user_id = int(message.split()[0])
            self.send_answer_message(message[len(str(user_id)):], user_id)
            return True
        except ValueError:
            return False

    def check_for_commands(self, message):
        entrypoint_str: str = message[:gm.find_char_index(message, "?")]

        if entrypoint_str[0] == "/":
            entrypoint = entrypoint_str.split("/")[1:]
            match entrypoint[0]:

                case "start":

                    # If there is anything else after /start/...
                    if len(entrypoint) > 1:
                        match "/".join(entrypoint[1:]).split("?")[0]:

                            case "first_questions/_00":
                                self.update_lang(message[gm.find_char_index(message, "?")+1:])

                    # If command is /start
                    else:
                        self.start()

                case "adm_authenticate":
                    self.adm_authenticate()

                case "main_kb":
                    self.main_kb()

                case "next_user":
                    self.next_user()

                case "get_lost_count":
                    self.get_lost_count()

                case "reply_user":
                    self.reply_user()

                case "langs":
                    self.langs()

                case _:

                    print("Unknown command:", message)

        else:
            if not self.check_buttons(message):
                if not self.check_reply_user(message):
                    self.send_unknown()

    def redirect_response(self):

        print(self.response)
        print()

        if self.response.get("edited_message") is None:
            if self.check_staff_user():
                print("[OK] Authentication succeeded")
                if self.response.get("message") is not None:
                    self.check_for_commands(self.response.get("message").get("text"))

                if self.response.get("callback_query") is not None:
                    self.check_for_commands(self.response.get("callback_query").get("data"))
            else:
                print("\n\n\n[WARNING] Authentication failed ^^^^^^^^^^^")

        else:
            print("edited_message is not supported")
