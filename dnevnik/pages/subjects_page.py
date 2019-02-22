from typing import List
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage, ResponseType
from dnevnik.support import flat_2d, unique
from main.models import Subject, Class, Lesson


class SubjectsPage(BasePage):
    URL: str = 'https://schools.dnevnik.ru/ajax.ashx'
    response_type = ResponseType.JSON

    def __init__(self, klass: Class, xss_token: str):
        super().__init__(params={
            'xss': xss_token,
            'a': 'gsbgid'
        }, data={
            'grade': str(klass.dnevnik_id)
        })
        self.klass = klass
        self.subjects: List[Subject] = []

    def parse(self):
        self.soup = BeautifulSoup(self.json['html'], 'lxml')
        subjects = self.soup.find_all('a')
        'https://schools.dnevnik.ru/journals/journalclassical.aspx' \
            '?view=subject&school=***REMOVED***&group=1448121055668900357&subject=3293138171526831' \
            '&period=1448167329646543382&year=2018'
        for z, subject in enumerate(subjects):
            name = subject.text
            query = parse_qs(urlparse(subject['href']).query)
            subject_id = int(query['subject'][0])
            subject = Subject(name=name, dnevnik_id=subject_id, type=Subject.OTHERS)
            self.subjects.append(subject)
        return self

    @staticmethod
    def scan_all_classes(fetch_queue: FetchQueueProcessor, classes: List[Class], xss_token: str, save: bool = False):
        pages = [SubjectsPage(klass, xss_token) for klass in classes]
        # fetch_queue.process(pages)
        for page in pages:
            page.fetch(fetch_queue.session).parse()

        subjects = [subject for page in pages for subject in page.subjects]
        subjects = unique(subjects, lambda x: x.dnevnik_id)
        if save:
            Subject.objects.bulk_create(subjects)
        subjects_map = {subject.dnevnik_id: subject for subject in subjects}
        lessons = [Lesson(klass=page.klass, subject=subjects_map[subject.dnevnik_id])
                   for page in pages for subject in page.subjects]
        # if save:
        #     Lesson.objects.bulk_create(lessons)
        return subjects, lessons


