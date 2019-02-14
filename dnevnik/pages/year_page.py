from typing import List

from dnevnik import dnevnik_settings
from dnevnik.pages.klass_page import transform_class_name
from main.models import Class
from .base_page import BasePage

__all__ = ['YearPage']


class YearPage(BasePage):
    URL: str = 'https://schools.dnevnik.ru/journals/'

    def __init__(self, year: int):
        super().__init__(params={
            'school': dnevnik_settings.SCHOOL_ID,
            'tab': 'groups',
            'year': str(year)
        })
        self.year: int = year
        self.classes: List[Class] = []
        self.previous_year: bool = False

    def __str__(self):
        return f'<YearPage year={self.year}>'

    __repr__ = __str__

    def parse(self) -> 'YearPage':
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
        return self

    @staticmethod
    def scan_all_years(session) -> List[Class]:
        year = dnevnik_settings.current_year()
        classes = []
        while True:
            print('years', year)
            page = YearPage(year=year).fetch(session).parse()
            classes.extend(page.classes)
            if page.previous_year:
                year -= 1
            else:
                break
        return classes

