import os
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marks.settings')
django.setup()

# import from any project file must go after django.setup()
from marks.settings import DNEVNIK

LOGIN = DNEVNIK['login']
PASSWORD = DNEVNIK['pass']
SCHOOL_ID = DNEVNIK['school_id']

URLS = {
    'login': 'https://login.dnevnik.ru/',
    'journals': 'https://schools.dnevnik.ru/journals/?school={school_id}&tab=groups&year={year}',
    'get_subjects': 'https://schools.dnevnik.ru/ajax.ashx?xss={xss}&a=gsbgid',
    'journal': 'https://schools.dnevnik.ru/journals/journalclassical.aspx'
}


def login() -> requests.Session:
    url = URLS['login']
    login_data = {
        'login': LOGIN,
        'password': PASSWORD
    }
    s = requests.Session()
    r = s.post(url, data=login_data)

    if 'Ошибка в логине или пароле' in r.text:
        raise ValueError('Ошибка в логине или пароле')
    if r.status_code != 200:
        raise RuntimeError('Неизвестная ошибка при попытке авторизации')
    return s
