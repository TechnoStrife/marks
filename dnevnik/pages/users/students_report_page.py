from typing import Tuple, Union, List

from bs4 import BeautifulSoup
from bs4.element import Tag

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.users.users_report_page import UsersReportPage
from dnevnik.support import exclude_navigable_strings, flat_2d, get_query_params, unique
from main.models import Class, Student

__all__ = ['StudentsReportPage']


class StudentsReportPage(UsersReportPage):
    URL: str = 'https://schools.dnevnik.ru/reports/default.aspx?report=people-students'

    def __init__(self, page: int = 1, year: int = None, date: str = None):
        super().__init__(page, year, date)
        self.students: List[Student] = []

    def __str__(self):
        if self.parsed:
            return f"<StudentListPage page={self.params['page']}, parsed={len(self.students)}>"
        else:
            return f"<StudentListPage page={self.params['page']}>"

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

    def extract_years(self):
        switch = self.soup.find(class_='switch')
        years = switch.find_all('a')
        dates = [get_query_params(year['href'], 'date') for year in years]
        years = [year.text for year in years]
        years = [int(year[:year.index('/')]) for year in years]
        return list(zip(years, dates))

    @staticmethod
    def extract_parents(tr: List[Tag], tr2: BeautifulSoup) -> str:
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
        name: List[str] = tr[1]['title'].split()
        name = name[-1:] + name[:-1]
        name = ' '.join(name)

        dnevnik_id = None
        if tr[1].a:
            dnevnik_id = int(get_query_params(tr[1].a['href'], 'user'))

        student = Student(
            full_name=name,
            klass=Class.objects.get(dnevnik_id=klass_id),
            birthday=self.transform_birthday(tr[3].text),
            # email=tr[7].text.strip() if tr[7].text.strip() else None,
            # tel=str(tr[6].contents[0]) if tr[6].text else None,
            parents=self.extract_parents(tr, tr2),
            dnevnik_id=dnevnik_id,
        )
        self.students.append(student)

    @staticmethod
    def scan_all_pages(fetch_queue: FetchQueueProcessor,
                       year: int = None, date: str = None, save: bool = False) -> List[Student]:
        page1 = StudentsReportPage(1, year, date).fetch(fetch_queue.session).parse()
        pages = [StudentsReportPage(page, year, date) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        students = flat_2d([page1.students] + [page.students for page in pages])
        if save:
            Student.objects.bulk_create(students)
        return students

    @staticmethod
    def scan_all_years(fetch_queue: FetchQueueProcessor, save: bool = False) -> List[Student]:
        years = StudentsReportPage().fetch(fetch_queue.session).extract_years()
        first_pages = [StudentsReportPage(1, year, date) for year, date in years]  # if year >= VERY_FIRST_YEAR
        fetch_queue.process(first_pages)
        pages = []
        for page1 in first_pages:
            for page_n in range(2, page1.last_page + 1):
                pages.append(StudentsReportPage(page_n, page1.year, page1.date))
        fetch_queue.process(pages)
        pages.extend(first_pages)
        students = (student for page in pages for student in page.students)
        students = unique(students, lambda x: x.full_name)
        if save:
            Student.objects.bulk_create(students)
        return students
