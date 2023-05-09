import datetime


def message_is_date(message):
    message_date = message.text
    try:
        date_tuple = tuple(map(int, message_date.split('-')))
        assert len(date_tuple) == 3
        datetime.date(*date_tuple)
        return True
    except:
        return False


def message_is_date_time(message):
    message_date_time = message.text
    try:
        space_between_date_time = message_date_time.rfind(' ')
        date_tuple = tuple(map(int, message_date_time[:space_between_date_time].split('-')))
        assert len(date_tuple) == 3
        time_tuple = tuple(map(int, message_date_time[space_between_date_time + 1:].split(':')))
        assert len(time_tuple) >= 1
        datetime.datetime(*date_tuple, *time_tuple)
        return True
    except:
        return False
