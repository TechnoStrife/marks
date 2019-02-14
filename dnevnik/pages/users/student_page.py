from dnevnik.pages.users.user_page import UserPage
from main.models import Student, Class

__all__ = ['StudentPage']


class StudentPage(UserPage):
    def __init__(self, user_id, klass):
        super().__init__(user_id)
        self.klass: Class = klass
        self.student: Student = None

    def __str__(self):
        if self.parsed:
            return f'<StudentPage name={self.student.name}>'
        else:
            return f'<StudentPage id={self.user_id}, klass={self.klass.name}>'

    __repr__ = __str__

    def parse(self):
        super().parse()
        self.student = Student(
            full_name=self.name,
            klass=self.klass,
            birthday=self.birthday,
            tel=self.tel,
            email=self.email,
            parents=self.extract_parents(),
            dnevnik_id=self.user_id,
            not_found_in_dnevnik=self.not_found_in_dnevnik
        )
        self.parsed = True
        return self

    def extract_parents(self):
        parents = self.profile_soup.find(text='Родственники:').next_sibling
        parents = parents.get_text()
        parents = '\n'.join(parents.split(', '))
        return parents
