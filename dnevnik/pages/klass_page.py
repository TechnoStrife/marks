import copy
import re
from typing import Union, List
from urllib.parse import parse_qs, urlparse

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages import TeacherPage
from main.models import Teacher, Class
from .base_page import BasePage

__all__ = ['ClassPage', 'transform_class_name', 'class_grade']


def transform_class_name(name: str) -> str:  # '10 "А"' -> '10А'
    if len(name) == 3:
        return name
    expr = re.match('^(\\d{1,2})\\s?\"([А-Я])\"', name)
    name = expr.group(1) + expr.group(2)
    return name


def class_grade(name: str) -> int:  # '10А' -> 10
    if name[1].isdigit():
        return int(name[:2])
    return int(name[0])


class ClassPage(BasePage):
    URL: str = 'https://schools.dnevnik.ru/class.aspx'

    def __init__(self, name: str, class_id: int, year: int):
        super().__init__(params={'class': str(class_id)})
        self.klass = Class(name=name, year=year, dnevnik_id=class_id)
        self.head_teacher_id: Union[int, None] = None
        self.head_teacher_parsed: bool = False

    def __str__(self):
        return f'<ClassPage name={self.klass.name}, year={self.klass.year}>'

    __repr__ = __str__

    def parse(self) -> 'ClassPage':
        self.extract_final_class()
        self.extract_head_teacher()
        self.parsed = True
        return self

    def extract_final_class(self) -> None:
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

    def extract_head_teacher(self) -> None:
        head_teacher = self.soup.find(class_='peopleS')
        if not head_teacher:
            self.head_teacher_parsed = True
            return
        head_teacher = head_teacher.find(class_='first').find_all('a')[1]
        if not head_teacher['href']:
            raise RuntimeError
        self.head_teacher_id = head_teacher['href'][len('https://dnevnik.ru/user/user.aspx?user='):].strip()
        self.head_teacher_id = int(self.head_teacher_id)

        head_teacher = Teacher.objects.filter(dnevnik_id=self.head_teacher_id)
        if head_teacher.exists():
            self.klass.head_teacher = head_teacher.first()
            self.head_teacher_parsed = True

    @staticmethod
    def scan_all_classes(classes: List[Class], fetch_queue: FetchQueueProcessor) -> List[Class]:
        pages = [ClassPage(name=klass.name, class_id=klass.dnevnik_id, year=klass.year)
                 for klass in classes]
        fetch_queue.process(pages)

        teachers_request = {page.head_teacher_id
                            for page in pages
                            if not page.head_teacher_parsed}
        if len(teachers_request) > 0:
            teachers_request = [TeacherPage(user_id=head_teacher_id)
                                for head_teacher_id in teachers_request]
            fetch_queue.process(teachers_request)
            head_teachers = [teacher_page.teacher for teacher_page in teachers_request]
            head_teachers = {teacher.id: teacher for teacher in head_teachers}
            for page in pages:
                if page.head_teacher_parsed:
                    continue
                page.klass.head_teacher = head_teachers[page.head_teacher_id]
        classes = [page.klass for page in pages]
        return classes
