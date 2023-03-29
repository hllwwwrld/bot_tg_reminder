def message_is_date(message):
    date = message.text
    # bool_list = [True if i in '0123456789' else i == '-' for i in date]
    bool_list = list(map(lambda symb: symb in '0123456789' or symb == '-', date))
    return all([all(bool_list), date.count('-') == 2, len(date) == 10])
