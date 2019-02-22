import datetime

from bs4 import BeautifulSoup

from dnevnik.pages.base_page import BasePage
from dnevnik.support import skip_navigable_strings

__all__ = ['UserPage']


class UserPage(BasePage):
    URL: int = 'https://dnevnik.ru/user/user.aspx'

    def __init__(self, user_id: int):
        super().__init__(params={'user': user_id})
        if type(user_id) is not int:
            raise ValueError('user_id must be type int')
        self.user_id: int = user_id
        self.name: str = None
        self.birthday: datetime.date = None
        self.not_found_in_dnevnik: bool = False
        self.contacts: dict = {}
        self.email: str = None
        self.tel: str = None
        self.profile_soup: BeautifulSoup = None

    def parse(self):
        self.extract_profile()
        return self

    def extract_contacts(self):
        contacts_soup = self.soup.find(class_='contacts')
        if not contacts_soup:
            return {}
        # Samples: https://dnevnik.ru/user/user.aspx?user=1000005849457  1000007512420  1000007381547
        key = None
        for contact in skip_navigable_strings(contacts_soup):
            if contact.name == 'dt':
                if contact.text == 'Эл. почта':
                    key = 'email'
                elif contact.text == 'Мобильный телефон':
                    key = 'tel'
                else:
                    key = None
            elif contact.name == 'dd':
                if contact.text == 'Скрыт':
                    continue
                if key == 'email':
                    if contact.a and not contact.a.text.endswith('dnevnik.ru'):
                        self.email = contact.a.text
                elif key == 'tel':
                    self.tel = contact.text
            else:
                raise RuntimeError('error in user contacts. dnevnik sucks')
        return self.contacts

    def extract_profile(self):
        self.profile_soup = self.soup.find(class_='profile')
        self.name = self.profile_soup.h2.get_text().strip()

        if self.profile_soup.p and 'Страница скрыта пользователем' in self.profile_soup.p.text:
            self.not_found_in_dnevnik = True
            return

        self.birthday = self.profile_soup.find(class_='birthdayTable').dd.text.replace('\xa0', ' ').strip()
        if '(' in self.birthday:  # cut age like '19 октября 1992 (25 лет)' -> '19 октября 1992'
            self.birthday = self.birthday[:self.birthday.find('(')].strip()
        self.extract_contacts()
