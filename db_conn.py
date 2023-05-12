import psycopg2
import telebot
import configparser


config = configparser.ConfigParser()
config.read('connection_config')


class BotConnection:
    def __init__(self):
        self.bot = telebot.TeleBot(config.get('telebot', 'remainder_bot'))


class DbConnection:
    def __init__(self):
        self.db_connection = psycopg2.connect(database=config.get('db_conn', 'database'),
                                         user=config.get('db_conn', 'user'),
                                         password=config.get('db_conn', 'password'),
                                         host=config.get('db_conn', 'host'),
                                         port=config.get('db_conn', 'port'))
        self.database = self.db_connection.cursor()
