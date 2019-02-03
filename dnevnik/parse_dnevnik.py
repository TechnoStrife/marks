import re
import django
import requests
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from dnevnik import dnevnik_settings

django.setup()
from main.models import *
from dnevnik.support import *


def login() -> requests.Session:
    session = requests.Session()
    login_data = {
        'login': dnevnik_settings.LOGIN,
        'password': dnevnik_settings.PASSWORD
    }
    r = request_page(session, 'login', data=login_data)

    if r.url == 'https://dnevnik.ru/teacher' or r.url == 'https://dnevnik.ru:443/teacher':  # after redirect
        return session
    elif 'Ошибка в логине или пароле' in r.text:
        raise ValueError('Ошибка в логине или пароле')
    elif r.status_code != 200:
        raise RuntimeError('Неизвестная ошибка при попытке авторизации')
    else:
        raise RuntimeError('WTF how did it get here?')


def scan_classes_by_year(session: requests.Session, year):
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


def scan_class(session: requests.Session, name, class_id, year) -> Class:
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

    r = request_page(session, 'class', params={'class': str(class_id)})

    klass = {
        'name': name,
        'year': year,
        'dnevnik_id': class_id,
    }

    soup = BeautifulSoup(r.text, "lxml")
    class_info = soup.find(class_='info').find('h2').text[len('Класс:'):].strip()
    if '(' in class_info:
        final_class_name = class_info[:class_info.find('(')].strip()
        klass['info'] = class_info[class_info.find('(') + len('('):class_info.find(')')].strip()
        if final_class_name == klass['info']:
            klass['info'] = None
    else:
        final_class_name = class_info
        klass['info'] = None
    final_class_name = transform_class_name(final_class_name)
    del class_info

    klass['head_teacher'] = extract_head_teacher(soup.find(class_='peopleS'), session)

    final_class_id = int(parse_qs(urlparse(r.url).query)['class'][0])
    if final_class_id != class_id:
        final_class = klass.copy()
        final_class['name'] = final_class_name
        final_class['dnevnik_id'] = final_class_id
        del final_class_id, final_class_name
        final_class['year'] += class_grade(final_class['name']) - class_grade(klass['name'])
        final_class = get_or_create(Class, 'dnevnik_id', **final_class)
        klass['final_class'] = final_class

    return get_or_create(Class, 'dnevnik_id', **klass)


def scan_user(session: requests.Session, user_id: int, user=STUDENT, klass=None):
    def extract_contacts(contacts_soup):
        if not contacts_soup:
            return {}
        # Samples: https://dnevnik.ru/user/user.aspx?user=1000005849457  1000007512420  1000007381547
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
        return contacts

    if type(user_id) is not int:
        raise ValueError('user_id must be type int')
    if user not in USER_TYPES:
        raise RuntimeError("user must be '{}' or '{}'".format(STUDENT, TEACHER))

    r = request_page(session, 'user', params={'user': str(user_id)})
    soup = BeautifulSoup(r.text, "lxml")

    profile = soup.find(class_='profile')

    res = {
        'dnevnik_id': user_id,
        'name': profile.h2.a.text.strip()
    }

    if not profile.p or profile.p.text == 'Страница скрыта пользователем':
        res['not_found_in_dnevnik'] = True
    else:
        birthday = profile.find(class_='birthdayTable').dd.text.replace('\xa0', ' ').strip()
        if '(' in birthday:  # cut age like '19 октября 1992 (25 лет)' -> '19 октября 1992'
            birthday = birthday[:birthday.find('(')].strip()
        res['birthday'] = birthday
        del birthday

        res.update(extract_contacts(soup.find(class_='contacts')))
    del profile

    if user == STUDENT:
        res['klass'] = klass
        res['full_name'] = res.pop('name')
        return update_or_create(Student, 'dnevnik_id', **res)
    else:
        return update_or_create(Teacher, 'dnevnik_id', **res)


def scan_all_teachers(session: requests.Session):
    def scan_tr(tr):
        children = exclude_navigable_strings(tr)

        res = {
            'full_name': children[1]['title'],
            'birthday': children[3].text,
            'email': children[7].text if children[7].text else None,
        }
        res['birthday'] = [int(x) for x in res['birthday'].split('.')]
        res['birthday'] = datetime.date(*res['birthday'][::-1])
        if children[6].text:
            res['tel'] = str(children[6].contents[0])
        else:
            res['tel'] = None

        if children[1].a:
            res['dnevnik_id'] = int(children[1].a['href'][len('https://dnevnik.ru/user/user.aspx?user='):])
        else:
            res['hidden_in_dnevnik'] = True

        return update_or_create(Teacher, 'dnevnik_id', **res)

    r = request_page(session, 'all_teachers', params={'school': dnevnik_settings.SCHOOL_ID})
    soup = BeautifulSoup(r.text, "lxml")

    pager = soup.find(class_='pager')
    last_page = exclude_navigable_strings(pager.ul.children)[-1]
    last_page = last_page.a.text if last_page.a else last_page.b.text
    last_page = int(last_page)
    del pager

    teachers = []

    table = soup.find(class_='grid')
    for tr in exclude_navigable_strings(table)[1:]:
        teachers.append(scan_tr(tr))

    for page in range(2, last_page + 1):
        r = request_page(session, 'all_teachers', params={
            'school': dnevnik_settings.SCHOOL_ID,
            'page': page
        })
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find(class_='grid')
        for tr in exclude_navigable_strings(table)[1:]:
            teachers.append(scan_tr(tr))
    return teachers


def scan_all_students(session: requests.Session):
    def scan_tr(tr, tr2):
        children = exclude_navigable_strings(tr)

        res = {
            'full_name': children[1]['title'],
            'birthday': children[3].text,
            'klass': int(children[4].a['href'][len('https://schools.dnevnik.ru/class.aspx?class='):]),
        }
        res['klass'] = Class.objects.get(dnevnik_id=res['klass'])
        res['birthday'] = [int(x) for x in res['birthday'].split('.')]
        res['birthday'] = datetime.date(*res['birthday'][::-1])

        if children[1].a:
            res['dnevnik_id'] = int(children[1].a['href'][len('https://dnevnik.ru/user/user.aspx?user='):])
        else:
            res['not_found_in_dnevnik'] = True

        if children[5].text.strip() != '':
            parents = children[5]['title']
            if children[6].text.strip() != '':
                parents += ': ' + children[6].text.strip()
            if tr2 is not None:
                tr2 = exclude_navigable_strings(tr2)
                parents += '\n' + tr2[0]['title']
                if tr2[1].text.strip() != '':
                    parents += ': ' + tr2[1].text.strip()
            res['parents'] = parents

        return update_or_create(Student, 'full_name', **res)

    def join_rows(table):
        table = exclude_navigable_strings(table)[2:]
        while table:
            tr = table.pop(0)
            tr2 = None
            if 'rowspan' in tr.td.attrs:
                tr2 = table.pop(0)
            yield tr, tr2

    r = request_page(session, 'all_students', params={'school': dnevnik_settings.SCHOOL_ID})
    soup = BeautifulSoup(r.text, "lxml")

    last_page = get_pages_count(soup)

    students = []

    table = soup.find(class_='grid')

    for tr, tr2 in join_rows(table):
        students.append(scan_tr(tr, tr2))

    for page in range(2, last_page + 1):
        r = request_page(session, 'all_students', params={
            'school': dnevnik_settings.SCHOOL_ID,
            'page': page
        })
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find(class_='grid')
        for tr, tr2 in join_rows(table):
            students.append(scan_tr(tr, tr2))
    return students


def main():
    print('Logging')
    session = login()

    # scan_all_teachers(session)
    scan_all_students(session)
    return

    for year in range(dnevnik_settings.current_year(), dnevnik_settings.VERY_FIRST_YEAR - 1, -1):
        classes = scan_classes_by_year(session, year)
        for klass in classes:
            klass = scan_class(session, klass['name'], klass['id'], year)
            if klass.final_class is not None:
                print('%s (%s) -> %s (%s)' % (klass.name, klass.year, klass.final_class.name, klass.final_class.year))
            else:
                print('%s (%s)' % (klass.name, klass.year))


if __name__ == '__main__':
    main()
