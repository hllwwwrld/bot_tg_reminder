import psycopg2
import telebot


class Connections:
    def __init__(self, config):
        api_token = config.get('telebot', 'remainder_bot')
        self.bot = telebot.TeleBot(api_token)
        self.database = psycopg2.connect(database=config.get('db_conn', 'database'),
                                        user=config.get('db_conn', 'user'),
                                        password=config.get('db_conn', 'password'),
                                        host=config.get('db_conn', 'host'),
                                        port=config.get('db_conn', 'port'))
        self.cursor = self.database.cursor()

    # def conn_db(self):
    #     return psycopg2.connect(database=config.get('db_conn', 'database'),
    #                             user=config.get('db_conn', 'user'),
    #                             password=config.get('db_conn', 'password'),
    #                             host=config.get('db_conn', 'host'),
    #                             port=config.get('db_conn', 'port'))
    #
    # def create_bot_conn(self):
    #     api_token = config.get('telebot', 'remainder_bot')
    #     self.bot = telebot.TeleBot(api_token)
