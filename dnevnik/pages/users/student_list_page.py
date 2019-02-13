
from dnevnik.pages.users.user_list_page import UserListPage
from dnevnik.parsers.support import exclude_navigable_strings
from main.models import Class, Student

__all__ = ['StudentListPage']


class StudentListPage(UserListPage):
    URL = 'https://schools.dnevnik.ru/reports/default.aspx?report=people-students'

    def __init__(self, page=1):
        super().__init__(page=page)
        self.students = []

    def parse(self):
        super().parse()
        for tr, tr2 in self.join_rows():
            self.scan_tr(tr, tr2)
        return self

    def join_rows(self):
        table = exclude_navigable_strings(self.table)[2:]
        while table:
            tr = table.pop(0)
            tr2 = None
            if 'rowspan' in tr.td.attrs:
                tr2 = table.pop(0)
            yield tr, tr2

    @staticmethod
    def extract_parents(tr, tr2):
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

    def scan_tr(self, tr, tr2):
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
    def scan_all_pages(session):
        print('students', 1)
        page1 = StudentListPage().fetch(session).parse()
        students = page1.students
        for page in range(2, page1.last_page + 1):
            print('students', page)
            students.extend(StudentListPage(page=page).fetch(session).parse().students)
        return students
