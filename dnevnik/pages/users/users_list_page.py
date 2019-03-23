from abc import ABCMeta, abstractmethod
from typing import List

from bs4.element import Tag

from dnevnik import settings
from dnevnik.dates import transform_date
from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage
from dnevnik.pages.users.person_page import PersonPage
from dnevnik.support import exclude_navigable_strings, get_query_params
from main.models import Class, Student, Teacher

__all__ = ['UserListPage', 'TeacherListPage', 'StudentListPage']


class UserListPage(BasePage, metaclass=ABCMeta):
    URL = 'https://schools.dnevnik.ru/admin/persons/default.aspx'

    def __init__(self, group: str, page: int, archive: bool = False):
        super().__init__(params={
            'school': settings.SCHOOL_ID,
            'page': page,
            'group': group,
            'view': 'archive' if archive else None
        })
        self.last_page: int = None
        self.archive = archive

    def extract_pages_count(self):
        pager = self.soup.find(class_='pager')
        last_page = exclude_navigable_strings(pager.ul.children)[-1]
        last_page = last_page.a.text if last_page.a else last_page.b.text
        self.last_page = int(last_page)
        return self.last_page

    def parse(self):
        self.extract_pages_count()
        table: List[Tag] = exclude_navigable_strings(self.soup.find(class_='grid'))
        table = table[1:]
        table: List[List[Tag]] = [exclude_navigable_strings(row) for row in table]

        for row in table:
            self._parse_row(row)
        self.parsed = True
        return self

    @abstractmethod
    def _parse_row(self, row: List[Tag]) -> None:
        pass


class StudentListPage(UserListPage):
    def __init__(self, page: int = 1, archive: bool = False):
        super().__init__('students', page, archive)
        self.students: List[Student] = []

    def _parse_row(self, row: List[Tag]):
        if self.archive:
            klass = None
            entered = transform_date(row[2].get_text().strip())
            leaved = transform_date(row[3].get_text().strip())
        else:
            klass = Class.objects.get(dnevnik_id=int(get_query_params(row[3].a['href'], 'class')))
            entered = None
            leaved = None
        student = Student(
            full_name=row[1].a.text,
            dnevnik_id=int(get_query_params(row[0].a['href'], 'user')) if row[0].a else None,
            dnevnik_person_id=int(get_query_params(row[1].a['href'], 'person')),
            klass=klass,
            entered=entered,
            leaved=leaved
        )
        self.students.append(student)

    @staticmethod
    def scan_all(fetch_queue: FetchQueueProcessor, save: bool = False, archive: bool = False) -> List[Student]:
        page1 = StudentListPage(archive=archive)
        page1.fetch(fetch_queue.session).parse()
        pages = [StudentListPage(page, archive=archive) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        pages.insert(0, page1)
        students = [student for page in pages for student in page.students]
        pages = [PersonPage(student) for student in students]
        fetch_queue.process(pages)  # modifies each student
        if save:
            Student.objects.bulk_create(students)
        return students


class TeacherListPage(UserListPage):
    def __init__(self, page: int = 1, archive: bool = False):
        super().__init__('staff', page, archive)
        self.teachers: List[Teacher] = []

    def _parse_row(self, row: List[Tag]):
        if self.archive:
            job = None
        else:
            job = row[2].span.text
        teacher = Teacher(
            full_name=row[1].a.text,
            dnevnik_id=int(get_query_params(row[0].a['href'], 'user')) if row[0].a else None,
            dnevnik_person_id=int(get_query_params(row[1].a['href'], 'person')),
            job=job,
        )
        self.teachers.append(teacher)

    @staticmethod
    def scan_all(fetch_queue: FetchQueueProcessor, save: bool = False, archive: bool = False) -> List[Teacher]:
        page1 = TeacherListPage(archive=archive)
        page1.fetch(fetch_queue.session).parse()
        pages = [TeacherListPage(page, archive=archive) for page in range(2, page1.last_page + 1)]
        fetch_queue.process(pages)
        pages.insert(0, page1)
        teachers = [teacher for page in pages for teacher in page.teachers]
        pages = [PersonPage(teacher) for teacher in teachers]
        fetch_queue.process(pages)  # modifies each teacher
        if save:
            Teacher.objects.bulk_create(teachers)
        return teachers
