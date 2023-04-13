import configparser
from db_conn import Connections
from sql_db import SqlRequests

config = configparser.ConfigParser()
config.read('connection_config')

connections = Connections(config)
database = SqlRequests(config)

bot = connections.bot


def remind_dates():
    users = database.get_all_users()  # получаю список всех user_id <и кол-во дней, за которое юзер получает уведомления>
    for user_id in users:
        dates_to_remind = database.get_remind_date(user_id)  # для каждого пользователя получаю список
        if len(dates_to_remind) > 0:
            bot.send_message(user_id, 'Reminding about your upcoming dates')
            for date in dates_to_remind:
                bot.send_message(user_id, f'In {int(date[3])} days comes "{date[0]}" date, which starts on {date[1]}')
        # else:
        #     bot.send_message(user, "Don't have any new dates comes in {user[1]}")