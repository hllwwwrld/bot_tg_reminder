from sql_db import SqlRequests
from db_conn import Connections
import message_wrapper
import configparser
from date_remaind import start_process

config = configparser.ConfigParser()
config.read('connection_config')

connections = Connections(config)
database = SqlRequests(config)

bot = connections.bot


# регистрация пользователя по командам /reg и /start
@bot.message_handler(commands=['reg', 'start'])
def registration(message):
    # запоминаю айди пользователя и имя
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)

    # если пользователь новый, ранее его не регистрировали - создается
    if database.is_user_new(user_id):
        database.create_user(user_id, username)  # создаю пользователя

        # оповещаю пользователя и вывожу лог
        bot.send_message(user_id, f'''Success registration\nuser_id: {user_id}\nand username: {username}.
You will get reminds about chosen dates 3 days before a date, everyday
You can set personal days value (instead of default 3) to get messages
use command (/<command>)''')
        print(f'Зарегестрирован пользователь с ником "{username}" и ID "{user_id}" ')

    # если пользователь уже есть в базе, то обновляются данные
    else:
        database.update_user(user_id, username)
        bot.send_message(user_id, f'''Registration data updated\nuser_id:{user_id}\nusername: {username}
You are now taking remind 3 days before a date, everyday
You can set personal days value (instead of your value) to get messages,
use command (/<command>)''')
        print(f'Данные обновлены по пользователю с ником "{username}" и ID "{user_id}"')


# добавление новой даты
@bot.message_handler(commands=['add'])
def add_new_bday(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # добавляю словарь, который будет заполняться ключевыми полями для создания новой даты пользователя
    date_dict = dict()
    date_dict['user_id'] = user_id  # добавляю в словарь айди юзера
    print(f'Добавление новой даты для пользователя {username}, {user_id}')

    bot.send_message(user_id, 'Send your date, in format: YYYY-MM-DD')
    # перехожу к следующему шагу, как параметр перадаю:
    # сообщение, чтобы знать к какому чату обращаться
    # функцию, в которой будет выполняться следующий шаг
    # и словарь с ключевыми полями для создания даты
    bot.register_next_step_handler(message, get_date, date_dict)


def get_date(message, date_dict):
    user_id = message.from_user.id

    # проверяю полученную дату на соответствие формату
    if message_wrapper.message_is_date(message):
        try:
            date_dict['date'] = message.text  # добавляю в ключевые поля саму дату
            bot.send_message(user_id, 'Send name of date')   # запрашиваю имя даты

            # перехожу к следущему шагу, где получаю название даты
            bot.register_next_step_handler(message, get_date_name, date_dict)
        except:
            date_dict.clear()
            bot.send_message(user_id, 'oops')
    else:  # если дата неверна - оповещаю пользователя и перехожу к следующему шагу - повторный вызов данной функции
        bot.reply_to(message, 'invalid date, try again')
        bot.register_next_step_handler(message, get_date, date_dict)


def get_date_name(message, date_dict):
    user_id = message.from_user.id

    try:
        date_dict['name'] = message.text   # добавляю новое значение в ключевые поля с датой

        # создаю новую дату для пользователя в БД
        database.add_date(date_dict['name'], date_dict['date'], date_dict['user_id'])

        # оповещения пользователя и вывод лога
        bot.send_message(user_id, 'New date successfully added')
        bot.send_message(user_id, f"{date_dict['date']} - {date_dict['name']}")
        print(f"Добавлена новая дата для пользователя {user_id}. {date_dict['date']} - {date_dict['name']}")

    except:
        bot.reply_to(message, 'oops, something went wrong')


@bot.message_handler(commands=['check'])
def check_all_user_dates(message):
    user_id = message.from_user.id
    dates = database.check_dates(user_id)
    if len(dates) > 0:
        bot.send_message(user_id, f'I know {len(dates)} your dates, here they are (ordered by closest):')
        for name in dates:
            bot.send_message(user_id, f'{name}: {dates[name]}')
    else:
        bot.send_message(user_id, 'Not found any dates for you')


@bot.message_handler(commands=['nearest'])
def check_nearest_user_date(message):
    user_id = message.from_user.id
    dates = database.check_dates(user_id, nearest=True)
    if len(dates) > 0:
        for name in dates:
            bot.send_message(user_id, f'Your nearest date is:\n{name}: {dates[name]}')
    else:
        print('Not found any dates for you')


@bot.message_handler(commands=['in_month'])
def check_dates_in_month_step_1(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Choose month to check dates for (from 1 to 12)')
    bot.register_next_step_handler(message, check_dates_in_month_step_2)


def check_dates_in_month_step_2(message):
    user_id = message.from_user.id
    dates = database.check_dates(user_id, month=message.text)
    if len(dates) > 0:
        for name in dates:
            bot.send_message(user_id, f'{name}: {dates[name]}')
    else:
        bot.send_message(user_id, f'Not found any dates in month "{message.text}" for you')


def remind_dates():
    users = database.get_all_users()  # получаю список всех user_id <и кол-во дней, за которое юзер получает уведомления>
    for user_id in users:
        dates_to_remind = database.get_remind_date(user_id)  # для каждого пользователя получаю список
        if len(dates_to_remind) > 0:
            bot.send_message(user_id, 'Reminding about your upcoming dates')
            for date in dates_to_remind:
                bot.send_message(user_id, f'In {date[3]} days comes "{date[0]}" date, which starts on {date[1]}')
        # else:
        #     bot.send_message(user, "Don't have any new dates comes in {user[1]}")


if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
