import datetime


def current_date():
    return datetime.datetime.now().strftime("%d.%m.%Y")
