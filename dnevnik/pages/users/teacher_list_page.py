import itertools
from typing import List

from bs4 import BeautifulSoup

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.users.user_list_page import UserListPage
from dnevnik.parsers.support import exclude_navigable_strings
from main.models import Teacher

__all__ = ['TeacherListPage']


class TeacherListPage(UserListPage):
    URL: str = 'https://schools.dnevnik.ru/reports/default.aspx?report=people-staff'

    def __init__(self, page: int = 1):
        super().__init__(page)
        self.teachers: List[Teacher] = []

    def __str__(self):
        if self.parsed:
            return f"<StudentListPage page={self.params['page']}, parsed={len(self.teachers)}>"
        else:
            return f"<StudentListPage page={self.params['page']}>"

    __repr__ = __str__

    def parse(self):
        super().parse()
        for tr in self.table[1:]:
            self.scan_tr(tr)
        self.parsed = True
        return self

    def scan_tr(self, tr: BeautifulSoup):
        children = exclude_navigable_strings(tr)

        dnevnik_id = None
        if children[1].a:
            offset = len('https://dnevnik.ru/user/user.aspx?user=')
            dnevnik_id = int(children[1].a['href'][offset:])

        teacher = Teacher(
            full_name=children[1]['title'],
            birthday=self.transform_birthday(children[3].text),
            job=children[4].text or None,
            tel=str(children[6].contents[0]) if children[6].text else None,
            email=children[7].text if children[7].text else None,
            dnevnik_id=dnevnik_id,
        )
        self.teachers.append(teacher)

    @staticmethod
    def scan_all_pages(fetch_queue: FetchQueueProcessor) -> List[Teacher]:
        print('teachers', 1)
        page1 = TeacherListPage().fetch(fetch_queue.session).parse()
        pages = [TeacherListPage(page=page) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        teachers = [page1.teachers] + [page.teachers for page in pages]
        teachers = list(itertools.chain.from_iterable(teachers))
        return teachers
