from typing import List

from bs4 import BeautifulSoup
from dnevnik.support import exclude_navigable_strings, get_query_params

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.users.users_report_page import UsersReportPage
from dnevnik.support import flat_2d
from main.models import Teacher

__all__ = ['TeachersReportPage']


class TeachersReportPage(UsersReportPage):
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
            dnevnik_id = int(get_query_params(children[1].a['href'], 'user'))

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
    def scan_all_pages(fetch_queue: FetchQueueProcessor, save: bool = False) -> List[Teacher]:
        print('teachers', 1)
        page1 = TeachersReportPage().fetch(fetch_queue.session).parse()
        pages = [TeachersReportPage(page=page) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        teachers = flat_2d([page1.teachers] + [page.teachers for page in pages])
        if save:
            Teacher.objects.bulk_create(teachers)
        return teachers
