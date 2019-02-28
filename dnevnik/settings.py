
import datetime

LOGIN = '***REMOVED***'
PASSWORD = '***REMOVED***'
SCHOOL_ID = ***REMOVED***

CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/69.0.3497.100 Safari/537.36 '

VERY_FIRST_YEAR = 2012


def current_year():
    now = datetime.datetime.now()
    days_between_1_jan_and_1_sep = datetime.timedelta(days=243)  # it's like new year is on 1 sep
    return (now - days_between_1_jan_and_1_sep).year

