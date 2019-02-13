from dnevnik import dnevnik_settings
from dnevnik.pages.klass_page import transform_class_name
from main.models import Class
from .base_page import BasePage

__all__ = ['YearPage']


class YearPage(BasePage):
    URL = 'https://schools.dnevnik.ru/journals/'

    def __init__(self, year):
        super().__init__(params={
            'school': dnevnik_settings.SCHOOL_ID,
            'tab': 'groups',
            'year': str(year)
        })
        self.year = year
        self.classes = []
        self.previous_year = False

    def parse(self):
        classes_soup = self.soup.find_all(title="Открыть журналы этого класса")
        if self.soup.find(class_='pB').a:
            self.previous_year = True
        for klass in classes_soup:
            self.classes.append(Class(
                name=transform_class_name(klass.text.strip()),
                year=self.year,
                dnevnik_id=klass['href'][1:],
            ))
        return self

    @staticmethod
    def scan_all_years(session):
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

