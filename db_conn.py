import psycopg2
import configparser


config = configparser.ConfigParser()
config.read('connection_config')


def conn():
    return psycopg2.connect(database=config.get('db_conn', 'database'),
                            user=config.get('db_conn', 'user'),
                            password=config.get('db_conn', 'password'),
                            host=config.get('db_conn', 'host'),
                            port=config.get('db_conn', 'port'))
