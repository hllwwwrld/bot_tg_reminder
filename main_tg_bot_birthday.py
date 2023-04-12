import telebot
import sql_db
import message_wrapper
import db_conn
import time


bot = telebot.TeleBot(db_conn.bot_birthday_token())


# регистрация пользователя по командам /reg и /start
@bot.message_handler(commands=['reg', 'start'])
def registration(message):
    # запоминаю айди пользователя и имя
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)

    # если пользователь новый, ранее его не регистрировали - создается
    if sql_db.is_user_new(user_id):
        sql_db.create_user(user_id, username)  # создаю пользователя

        # оповещаю пользователя и вывожу лог
        bot.send_message(user_id, f'Success registration\nuser_id: {user_id}\nand username: {username}')
        print(f'Зарегестрирован пользователь с ником "{username}" и ID "{user_id}" ')

    # если пользователь уже есть в базе, то обновляются данные
    else:
        sql_db.update_user(user_id, username)
        bot.send_message(user_id, f'Registration data updated\nuser_id: {user_id}\nusername: {username}')
        print(f'Данные обновлены по пользователю с ником "{username}" и ID "{user_id}" ')


# добавление новой даты
@bot.message_handler(commands=['add'])
def add_new_bday(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # добавляю словарь, который будет заполняться ключевыми полями для создания новой даты пользователя
    date_dict = dict()
    date_dict['user_id'] = user_id  # добавляю в словарь айди юзера
    print(f'Добавление новой даты для пользователя {username}, {user_id}')

    bot.send_message(user_id, 'Введите день рождения в формате YYYY-MM-DD')
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
            bot.register_next_step_handler(message, get_date_name, date_dict)  # перехожу к следущему шагу, где получаю название даты
        except Exception:
            date_dict.clear()
            bot.send_message(user_id, 'oops')
    else:  # если дата неверна - оповещаю пользователя и перехожу к следующему шагу - повторный вызов данной функции
        bot.reply_to(message, 'invalid date, try again')
        bot.register_next_step_handler(message, get_date, date_dict)


def get_date_name(message, date_dict):
    user_id = message.from_user.id

    try:
        date_dict['name'] = message.text   # добавляю новое значение в ключевые поля с датой

        sql_db.add_date(date_dict['name'], date_dict['date'], date_dict['user_id'])  # создаю новую дату для пользователя в БД

        # оповещения пользователя и вывод лога
        bot.send_message(user_id, 'Новая дата успешно добавлена')
        bot.send_message(user_id, f"{date_dict['date']} - {date_dict['name']}")
        print(f"Добавлена новая дата для пользователя {user_id}. {date_dict['date']} - {date_dict['name']}")

    except Exception:
        bot.reply_to(message, 'oops, something went wrong')


@bot.message_handler(commands=['check'])
def check_all_user_dates(message):
    user_id = message.from_user.id
    dates = sql_db.check_dates(user_id)
    if len(dates) > 0:
        bot.send_message(user_id, f'I know {len(dates)} your dates, here they are (ordered by closest):')
        for name in dates:
            bot.send_message(user_id, f'{name}: {dates[name]}')
    else:
        bot.send_message(user_id, 'Not found any dates for you')


@bot.message_handler(commands=['nearest'])
def check_nearest_user_date(message):
    user_id = message.from_user.id
    dates = sql_db.check_dates(user_id, nearest=True)
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
    dates = sql_db.check_dates(user_id, month=message.text)
    if len(dates) > 0:
        for name in dates:
            bot.send_message(user_id, f'{name}: {dates[name]}')
    else:
        bot.send_message(user_id, f'Not found any dates in month "{message.text}" for you')


def remind_dates():
    pass


bot.infinity_polling()
