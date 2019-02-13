import copy
import re
from urllib.parse import parse_qs, urlparse

from dnevnik.pages import TeacherPage
from main.models import Teacher, Class
from .base_page import BasePage

__all__ = ['ClassPage', 'transform_class_name', 'class_grade']


def transform_class_name(name):  # '10 "А"' -> '10А'
    if len(name) == 3:
        return name
    expr = re.match('^(\\d{1,2})\\s?\"([А-Я])\"', name)
    if not expr:
        return None
    name = expr.group(1) + expr.group(2)
    return name


def class_grade(name: str):  # '10А' -> 10
    if name[1].isdigit():
        return int(name[:2])
    return int(name[0])


class ClassPage(BasePage):
    URL = 'https://schools.dnevnik.ru/class.aspx'

    def __init__(self, name, class_id, year):
        super().__init__(params={'class': str(class_id)})
        self.klass = Class(name=name, year=year, dnevnik_id=class_id)
        self.session = None

    def fetch(self, session):
        super().fetch(session)
        self.session = session
        return self

    def parse(self):
        self.extract_final_class()
        self.extract_head_teacher()
        return self

    def extract_final_class(self):
        class_soup = self.soup.find(class_='info').find('h2').text[len('Класс:'):].strip()
        if '(' in class_soup:
            final_class_name = class_soup[:class_soup.find('(')].strip()
            self.klass.info = class_soup[class_soup.find('(') + len('('):class_soup.find(')')].strip()
            if final_class_name == self.klass.info:
                self.klass.info = None
        else:
            final_class_name = class_soup
            self.klass.info = None
        final_class_name = transform_class_name(final_class_name)

        final_class_id = int(parse_qs(urlparse(self.response.url).query)['class'][0])
        if final_class_id != self.klass.dnevnik_id:
            final_class = copy.copy(self.klass)
            final_class.name = final_class_name
            final_class.dnevnik_id = final_class_id
            final_class.year += class_grade(final_class.name) - class_grade(self.klass.name)
            self.klass.final_class = final_class

    def extract_head_teacher(self):
        head_teacher = self.soup.find(class_='peopleS')
        if not head_teacher:
            return None
        head_teacher = head_teacher.find(class_='first').find_all('a')[1]
        if not head_teacher['href']:
            raise RuntimeError
        head_teacher_id = head_teacher['href'][len('https://dnevnik.ru/user/user.aspx?user='):].strip()

        head_teacher = Teacher.objects.filter(dnevnik_id=head_teacher_id)
        if head_teacher.exists():
            self.klass.head_teacher = head_teacher.first()
        else:
            page = TeacherPage(user_id=int(head_teacher_id))
            page.fetch(self.session).parse()
            self.klass.head_teacher = page.teacher
