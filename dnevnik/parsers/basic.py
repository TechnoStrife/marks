import re

from requests import Session

from dnevnik import dnevnik_settings
from dnevnik.dnevnik_settings import CHROME_USER_AGENT


def login() -> Session:
    session = Session()
    login_data = {
        'login': dnevnik_settings.LOGIN,
        'password': dnevnik_settings.PASSWORD
    }
    r = request_page(session, 'login', data=login_data)

    if re.match(r'https://dnevnik\.ru(:443)?/teacher', r.url):  # after redirect
        return session
    elif 'Ошибка в логине или пароле' in r.text:
        raise ValueError('Ошибка в логине или пароле')
    elif r.status_code != 200:
        raise RuntimeError('Неизвестная ошибка при попытке авторизации')
    else:
        raise RuntimeError('WTF how did it get here?')


def request_page(session: Session, page_name, params=None, data=None):
    import time
    method = session.get if data is None else session.post
    url = dnevnik_settings.URLS[page_name]
    tries = 0
    while True:
        r = method(
            url,
            params=params,
            data=data,
            headers={'Referer': url, 'User-Agent': CHROME_USER_AGENT}
        )
        if r.status_code == 200 and len(r.text) > 0:
            break
        if tries >= 10:
            raise RuntimeError
        time.sleep(tries)
        tries += 1
    return r

