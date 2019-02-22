from typing import Tuple, Union, List

from bs4 import BeautifulSoup

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.users.user_list_page import UserListPage
from dnevnik.support import exclude_navigable_strings, flat_2d
from main.models import Class, Student

__all__ = ['StudentListPage']


class StudentListPage(UserListPage):
    URL: str = 'https://schools.dnevnik.ru/reports/default.aspx?report=people-students'

    def __init__(self, page=1):
        super().__init__(page=page)
        self.students: List[Student] = []

    def __str__(self):
        if self.parsed:
            return f"<StudentListPage page={self.params['page']}>"
        else:
            return f"<StudentListPage page={self.params['page']}, parsed={len(self.students)}>"

    __repr__ = __str__

    def parse(self):
        super().parse()
        for tr, tr2 in self.join_rows():
            self.scan_tr(tr, tr2)
        self.parsed = True
        return self

    def join_rows(self) -> Tuple[BeautifulSoup, Union[BeautifulSoup, None]]:
        table = exclude_navigable_strings(self.table)[2:]
        while table:
            tr = table.pop(0)
            tr2 = None
            if 'rowspan' in tr.td.attrs:
                tr2 = table.pop(0)
            yield tr, tr2

    @staticmethod
    def extract_parents(tr: BeautifulSoup, tr2: BeautifulSoup) -> str:
        parents = ''
        if tr[5].text.strip() != '':
            parents = tr[5]['title']
            if tr[6].text.strip() != '':
                parents += ': ' + tr[6].text.strip()
            if tr2 is not None:
                tr2 = exclude_navigable_strings(tr2)
                parents += '\n' + tr2[0]['title']
                if tr2[1].text.strip() != '':
                    parents += ': ' + tr2[1].text.strip()
        return parents

    def scan_tr(self, tr: BeautifulSoup, tr2: BeautifulSoup):
        tr = exclude_navigable_strings(tr)
        offset = len('https://schools.dnevnik.ru/class.aspx?class=')
        klass_id = int(tr[4].a['href'][offset:])

        dnevnik_id = None
        if tr[1].a:
            offset = len('https://dnevnik.ru/user/user.aspx?user=')
            dnevnik_id = int(tr[1].a['href'][offset:])

        student = Student(
            full_name=tr[1]['title'],
            klass=Class.objects.get(dnevnik_id=klass_id),
            birthday=self.transform_birthday(tr[3].text),
            email=tr[7].text if tr[7].text else None,
            tel=str(tr[6].contents[0]) if tr[6].text else None,
            parents=self.extract_parents(tr, tr2),
            dnevnik_id=dnevnik_id,
        )
        self.students.append(student)

    @staticmethod
    def scan_all_pages(fetch_queue: FetchQueueProcessor, save: bool = False) -> List[Student]:
        print('students', 1)
        page1 = StudentListPage().fetch(fetch_queue.session).parse()
        pages = [StudentListPage(page=page) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        students = flat_2d([page1.students] + [page.students for page in pages])
        if save:
            Student.objects.bulk_create(students)
        return students
