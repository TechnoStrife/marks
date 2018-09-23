import re
import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marks.settings')
    django.setup()

# import from any project file must go after django.setup()
from dnevnik import dnevnik_settings
from main.models import *


LOGIN = dnevnik_settings.LOGIN
PASSWORD = dnevnik_settings.PASSWORD
SCHOOL_ID = dnevnik_settings.SCHOOL_ID
URLS = dnevnik_settings.URLS


def transform_class_name(name):
    if len(name) == 3:
        return name
    expr = re.match('^(\d{1,2})\s?\"([А-Я])\"', name)
    if not expr:
        return False
    name = expr.group(1) + expr.group(2)
    return name


def skip_navigable_strings(soup):
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    for z in soup:
        if type(z) is NavigableString:
            continue
        yield z


def exclude_navigable_strings(soup):
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    return [x for x in soup if type(x) is not NavigableString]


def login() -> requests.Session:
    session = requests.Session()
    url = URLS['login']
    login_data = {
        'login': LOGIN,
        'password': PASSWORD
    }
    r = session.post(url, data=login_data)

    if 'Ошибка в логине или пароле' in r.text:
        raise ValueError('Ошибка в логине или пароле')
    if r.status_code != 200:
        raise RuntimeError('Неизвестная ошибка при попытке авторизации')
    return session


def scan_year(session: requests.Session, year):
    url = URLS['year']
    r = session.post(
        url=url,
        params={
            'school': SCHOOL_ID,
            'tab': 'groups',
            'year': str(year)
        },
        headers={
            'Referer': url
        }
    )
    soup = BeautifulSoup(r.text, "lxml")
    classes = soup.find_all(title="Открыть журналы этого класса")
    res = []
    for klass in classes:
        res.append({
            'name': klass.text.strip(),
            'id': klass['href'][1:]
        })
    return res


def scan_class(session: requests.Session, class_id):
    url = URLS['class']
    r = session.post(
        url=url,
        params={
            'class': str(class_id)
        },
        headers={
            'Referer': url
        }
    )
    if r.status_code != 200:
        raise RuntimeError('Ошибка при попытке получить информацию о классе')
    soup = BeautifulSoup(r.text, "lxml")
    class_info = soup.find(class_='info').find('h2').text[len('Класс:'):].strip()
    if '(' in class_info:
        name = class_info[:class_info.find('(')].strip()
        info = class_info[class_info.find('(') + len('('):class_info.find(')')].strip()
    else:
        name = class_info
        info = None

    head_teacher = soup.find(class_='peopleS').find(class_='first').find_all('a')[1]
    if not head_teacher['href'].startswith('https://dnevnik.ru/user/user.aspx?user='):
        raise RuntimeError

    return {
        'name': name,
        'info': info,
        'head_teacher': {
            'id': head_teacher['href'][len('https://dnevnik.ru/user/user.aspx?user='):].strip(),
            'name': head_teacher.text.strip()
        }
    }


def scan_user(session: requests.Session, user_id: int):
    if type(user_id) is not int:
        raise ValueError('user_id must be type int')

    url = URLS['user']
    r = session.post(
        url=url,
        params={
            'user': str(user_id)
        },
        headers={
            'Referer': url
        }
    )
    if r.status_code == 404:
        return False
    if r.status_code != 200:
        raise RuntimeError(r.status_code)
    soup = BeautifulSoup(r.text, "lxml")
    profile = soup.find(class_='profile')
    if profile is None:
        raise RuntimeError("dnevnik sucks. it's not showing user profile")

    res = {}

    name = profile.h2.a.text.strip()
    res['name'] = name
    del name

    if profile.p and profile.p.text == 'Страница скрыта пользователем':
        res['hidden_in_dnevnik'] = True
        return res

    birthday = profile.find(class_='birthdayTable').dd.text.replace('\xa0', ' ').strip()
    if '(' in birthday:  # cut age like '19 октября 1992 (25 лет)' -> '19 октября 1992'
        birthday = birthday[:birthday.find('(')].strip()
    res['birthday'] = birthday
    del birthday
    del profile

    contacts_soup = soup.find(class_='contacts')
    if contacts_soup:
        # Samples: https://dnevnik.ru/user/user.aspx?user=1000005849457
        #          https://dnevnik.ru/user/user.aspx?user=1000007512420
        #          https://dnevnik.ru/user/user.aspx?user=1000007381547
        contacts = {}
        key = None
        for contact in skip_navigable_strings(contacts_soup):
            if contact.name == 'dt':
                if contact.text == 'Эл. почта':
                    key = 'email'
                elif contact.text == 'Мобильный телефон':
                    key = 'tel'
                else:
                    key = None
            elif contact.name == 'dd':
                if contact.text == 'Скрыт':
                    continue
                if key == 'email':
                    if contact.a and not contact.a.text.endswith('dnevnik.ru'):
                        contacts[key] = contact.a.text
                elif key is not None:
                    contacts[key] = contact.text
            else:
                raise RuntimeError('error in user contacts. dnevnik sucks')
        res.update(contacts)
        del contacts
    del contacts_soup

    return res


def scan_all_teachers(session: requests.Session):
    pass


def main():
    print('Logging')
    session = login()
    print('Scanning classes')

    scan_all_teachers(session)
    # classes = scan_year(session, dnevnik_settings.current_year())
    # for klass in classes:
    #     class_info = scan_class(session, klass['id'])
    #     klass.update(class_info)
    #     teacher_info = scan_user(session, klass['head_teacher']['id'])
    #     if teacher_info:
    #         klass['head_teacher'].update(teacher_info)


if __name__ == '__main__':
    main()
