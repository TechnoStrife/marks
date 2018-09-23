
import datetime

LOGIN = '***REMOVED***'
PASSWORD = '***REMOVED***'
SCHOOL_ID = ***REMOVED***

URLS = {
    'login': 'https://login.dnevnik.ru/',
    'year': 'https://schools.dnevnik.ru/journals/',
    'class': 'https://schools.dnevnik.ru/class.aspx',
    'user': 'https://dnevnik.ru/user/user.aspx',
    'get_subjects': 'https://schools.dnevnik.ru/ajax.ashx?xss={xss}&a=gsbgid',
    'journal': 'https://schools.dnevnik.ru/journals/journalclassical.aspx'
}


def current_year():
    now = datetime.datetime.now()
    days_between_1_jan_and_1_sep = datetime.timedelta(days=243)  # it's like new year is on 1 sep
    return (now - days_between_1_jan_and_1_sep).year

