import datetime

from bs4 import BeautifulSoup

from dnevnik import settings
from dnevnik.pages.base_page import BasePage
from dnevnik.support import exclude_navigable_strings

__all__ = ['UserListPage']


class UserListPage(BasePage):
    def __init__(self, page):
        super().__init__(params={
            'school': settings.SCHOOL_ID,
            'page': page
        })
        self.last_page: int = None
        self.table: BeautifulSoup = None

    def extract_pages_count(self):
        pager = self.soup.find(class_='pager')
        last_page = exclude_navigable_strings(pager.ul.children)[-1]
        last_page = last_page.a.text if last_page.a else last_page.b.text
        self.last_page = int(last_page)

    @staticmethod
    def transform_birthday(birthday):
        birthday = [int(x) for x in birthday.split('.')][::-1]
        return datetime.date(*birthday)

    def parse(self):
        self.extract_pages_count()
        self.table = exclude_navigable_strings(self.soup.find(class_='grid'))
        return self
