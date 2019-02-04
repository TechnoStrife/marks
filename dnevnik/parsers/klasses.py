import re
from bs4 import BeautifulSoup
from requests import Session
from urllib.parse import parse_qs, urlparse

from main.models import *
from dnevnik import dnevnik_settings
from dnevnik.parsers.support import TEACHER, get_or_create
from dnevnik.parsers.users import scan_user
from dnevnik.parsers.basic import request_page


def transform_class_name(name):
    if len(name) == 3:
        return name
    expr = re.match('^(\\d{1,2})\\s?\"([А-Я])\"', name)
    if not expr:
        return None
    name = expr.group(1) + expr.group(2)
    return name


def class_grade(name: str):
    if name[1].isdigit():
        return int(name[:2])
    return int(name[0])


def scan_classes_by_year(session: Session, year):
    r = request_page(session, 'year', params={
        'school': dnevnik_settings.SCHOOL_ID,
        'tab': 'groups',
        'year': str(year)
    })
    soup = BeautifulSoup(r.text, "lxml")
    classes = soup.find_all(title="Открыть журналы этого класса")
    res = []
    for klass in classes:
        res.append({
            'id': klass['href'][1:],
            'name': transform_class_name(klass.text.strip()),
        })
    return res


def extract_final_class(soup, klass, url):
    class_soup = soup.find(class_='info').find('h2').text[len('Класс:'):].strip()
    if '(' in class_soup:
        final_class_name = class_soup[:class_soup.find('(')].strip()
        class_info = class_soup[class_soup.find('(') + len('('):class_soup.find(')')].strip()
        if final_class_name == class_info:
            class_info = None
    else:
        final_class_name = class_soup
        class_info = None
    final_class_name = transform_class_name(final_class_name)

    final_class_id = int(parse_qs(urlparse(url).query)['class'][0])
    final_class = None
    if final_class_id != klass['dnevnik_id']:
        final_class = klass.copy()
        final_class['name'] = final_class_name
        final_class['dnevnik_id'] = final_class_id
        del final_class_id, final_class_name
        final_class['year'] += class_grade(final_class['name']) - class_grade(klass['name'])
        final_class = get_or_create(Class, 'dnevnik_id', **final_class)

    return class_info, final_class


def extract_head_teacher(head_teacher, session):
    if not head_teacher:
        return None
    head_teacher = head_teacher.find(class_='first').find_all('a')[1]
    if not head_teacher['href']:
        raise RuntimeError
    head_teacher_id = head_teacher['href'][len('https://dnevnik.ru/user/user.aspx?user='):].strip()

    head_teacher = Teacher.objects.filter(dnevnik_id=head_teacher_id)
    if head_teacher.exists():
        head_teacher = head_teacher.first()
    else:
        head_teacher = scan_user(session, int(head_teacher_id), TEACHER)
    return head_teacher


def scan_class(session: Session, name, class_id, year) -> Class:
    r = request_page(session, 'class', params={'class': str(class_id)})

    klass = {
        'name': name,
        'year': year,
        'dnevnik_id': class_id,
    }

    soup = BeautifulSoup(r.text, "lxml")
    klass['info'], final_class = extract_final_class(soup, klass, r.url)
    if final_class is not None:
        klass['final_class'] = final_class

    klass['head_teacher'] = extract_head_teacher(soup.find(class_='peopleS'), session)

    return get_or_create(Class, 'dnevnik_id', **klass)

