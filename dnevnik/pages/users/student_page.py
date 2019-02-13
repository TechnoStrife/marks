from dnevnik.pages.users.user_page import UserPage
from main.models import Student

__all__ = ['StudentPage']


class StudentPage(UserPage):
    def __init__(self, user_id, klass):
        super().__init__(user_id)
        self.klass = klass
        self.student = None
        self.parents = None

    def parse(self):
        super().parse()
        self.extract_parents()
        self.student = Student(
            full_name=self.name,
            klass=self.klass,
            birthday=self.birthday,
            tel=self.tel,
            email=self.email,
            parents=self.parents,
            dnevnik_id=self.user_id,
            not_found_in_dnevnik=self.not_found_in_dnevnik
        )
        return self

    def extract_parents(self):
        parents = self.profile_soup.find(text='Родственники:').next_sibling
        parents = parents.get_text()
        self.parents = '\n'.join(parents.split(', '))
