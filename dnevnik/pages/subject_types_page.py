from dnevnik.pages.base_page import BasePage
from dnevnik.support import exclude_navigable_strings, unique
from main.models import SubjectType


class SubjectTypesPage(BasePage):
    URL = 'https://schools.dnevnik.ru/admin/subjects/default.aspx?school=1000000000000'

    def __init__(self):
        super().__init__()

    def parse(self, save: bool = True):
        table = self.soup.find(class_='grid')
        table = exclude_navigable_strings(table)
        table = table[1:]
        table = [exclude_navigable_strings(row) for row in table]
        types = [SubjectType(subject_name=row[0].text, type=row[1].text) for row in table]
        types = unique(types, key=lambda subject_type: subject_type.subject_name)
        if save:
            for subject_type in types:
                saved_type = SubjectType.objects.filter(subject_name=subject_type.subject_name)
                if saved_type.exists():
                    saved_type.update(type=subject_type.type)
                else:
                    subject_type.save()
        self.parsed = True
        return self
