import datetime

from dnevnik.pages.users.user_list_page import UserListPage
from dnevnik.parsers.support import exclude_navigable_strings
from main.models import Teacher

__all__ = ['TeacherListPage']


class TeacherListPage(UserListPage):
    URL = 'https://schools.dnevnik.ru/reports/default.aspx?report=people-staff'

    def __init__(self, page=1):
        super().__init__(page)
        self.teachers = []

    def parse(self):
        super().parse()
        for tr in self.table[1:]:
            self.scan_tr(tr)
        return self

    def scan_tr(self, tr):
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
    def scan_all_pages(session):
        print('teachers', 1)
        page1 = TeacherListPage().fetch(session).parse()
        teachers = page1.teachers
        for page in range(2, page1.last_page + 1):
            print('teachers', page)
            teachers.extend(TeacherListPage(page=page).fetch(session).parse().teachers)
        return teachers
