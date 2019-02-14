from dnevnik.pages.users.user_page import UserPage
from main.models import Teacher

__all__ = ['TeacherPage']


class TeacherPage(UserPage):
    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.teacher: Teacher = None

    def __str__(self):
        if self.parsed:
            return f'<TeacherPage name={self.teacher.name}>'
        else:
            return f'<TeacherPage id={self.user_id}>'

    __repr__ = __str__

    def parse(self):
        super().parse()
        self.teacher = Teacher(
            full_name=self.name,
            birthday=self.birthday,
            tel=self.tel,
            email=self.email,
            dnevnik_id=self.user_id,
        )
        self.parsed = True
        return self
