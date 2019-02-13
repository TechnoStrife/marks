from dnevnik.pages.users.user_page import UserPage
from main.models import Teacher

__all__ = ['TeacherPage']


class TeacherPage(UserPage):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.teacher = None

    def parse(self):
        super().parse()
        self.teacher = Teacher(
            full_name=self.name,
            birthday=self.birthday,
            tel=self.tel,
            email=self.email,
            dnevnik_id=self.user_id,
        )
        return self
