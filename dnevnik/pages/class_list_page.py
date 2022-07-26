import re
from typing import List, Union

import requests

from dnevnik import settings
from dnevnik.settings import VERY_FIRST_YEAR, current_year
from dnevnik.support import transform_class_name
from main.models import Class
from .base_page import BasePage

__all__ = ['ClassesListPage', 'fetch_xss_token']


class ClassesListPage(BasePage):
    URL: str = 'https://schools.dnevnik.ru/journals/'

    def __init__(self, year: int):
        super().__init__(params={
            'school': settings.SCHOOL_ID,
            'tab': 'groups',
            'year': str(year)
        })
        self.year: int = year
        self.classes: List[Class] = []
        self.previous_year: bool = False
        self.xss_token: Union[str, None] = None

    def __str__(self):
        return f'<YearPage year={self.year}>'

    __repr__ = __str__

    def parse(self) -> 'ClassesListPage':
        classes_soup = self.soup.find_all(title="Открыть журналы этого класса")
        if self.soup.find(class_='pB').a:
            self.previous_year = True
        for klass in classes_soup:
            self.classes.append(Class(
                name=transform_class_name(klass.text.strip()),
                year=self.year,
                dnevnik_id=int(klass['href'][1:]),
            ))
        self.parsed = True
        # self.xss_token = self.parse_xss()
        return self

    def parse_xss(self) -> str:
        xss_re = re.compile(r'\?xss=([\da-f]{64})')
        xss_token = xss_re.search(self.response.text)
        return xss_token.group(1)

    @staticmethod
    def scan_all_years(session) -> List[Class]:
        year = settings.current_year()
        classes = []
        while True:
            print('years', year)
            page = ClassesListPage(year=year).fetch(session).parse()
            classes.extend(page.classes)
            if year <= VERY_FIRST_YEAR:
                break
            if page.previous_year:
                year -= 1
            else:
                break
        return classes


def fetch_xss_token(session: requests.Session):
    return ClassesListPage(year=current_year()).fetch(session).parse_xss()
