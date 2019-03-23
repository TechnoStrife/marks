from typing import Union, Dict

from bs4.element import Tag

from dnevnik import settings
from dnevnik.dates import transform_date
from dnevnik.pages.base_page import BasePage
from dnevnik.support import skip_navigable_strings
from main.models import Teacher, Student


class PersonPage(BasePage):
    URL = 'https://schools.dnevnik.ru/admin/persons/person.aspx?view=review&group=all&listview=archive'

    def __init__(self, person: Union[Teacher, Student]):
        super().__init__(params={
            'person': person.dnevnik_person_id,
            'school': settings.SCHOOL_ID,
            'view': 'review'
        })
        self.person: Union[Teacher, Student] = person

    def parse(self):
        info = self.soup.find(class_='info')
        info = self.parse_info(info)
        for key, value in info.items():
            setattr(self.person, key, value)
        self.parsed = True

    @staticmethod
    def parse_info(dl: Tag) -> Dict[str, str]:
        info = {}
        key = None
        for tag in skip_navigable_strings(dl):
            if tag.name == 'dt':
                if tag.text == 'ФИО':
                    key = 'full_name'
                elif tag.text == 'Дата рождения':
                    key = 'birthday'
                elif tag.text == 'Email':
                    key = 'email'
                elif tag.text.endswith('телефон'):
                    key = 'tel'
                else:
                    key = None
            elif tag.name == 'dd':
                if key == 'tel':
                    if key in info and info[key] != '-':
                        info[key] = tag.text.strip()
                elif key == 'birthday':
                    info[key] = transform_date(tag.text.strip())
                elif key is not None:
                    info[key] = tag.text.strip()
        return info

