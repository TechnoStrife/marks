
import datetime
from typing import List

LOGIN = 'some login'
PASSWORD = 'expired anyway'
SCHOOL_ID = 1000000000000

CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/69.0.3497.100 Safari/537.36 '
MONTHS: List[str] = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                     'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
VERY_FIRST_YEAR = 2017


def current_year():
    now = datetime.datetime.now()
    days_between_1_jan_and_1_sep = datetime.timedelta(days=243)  # it's like new year is on 1 sep
    return (now - days_between_1_jan_and_1_sep).year

