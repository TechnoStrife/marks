from typing import List

from bs4 import BeautifulSoup

from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage, ResponseType
from dnevnik.support import unique, get_query_params
from main.models import Subject, Class, Lesson

__all__ = ['SubjectsPage']


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
        for z, subject in enumerate(subjects):
            name = subject.text
            subject_id = int(get_query_params(subject['href'], 'subject'))
            subject = Subject(name=name, dnevnik_id=subject_id)
            subject.update_type()
            self.subjects.append(subject)
        self.parsed = True
        return self

    @staticmethod
    def scan_all_classes(fetch_queue: FetchQueueProcessor, classes: List[Class], xss_token: str, save: bool = False):
        pages = [SubjectsPage(klass, xss_token) for klass in classes]
        fetch_queue.process(pages)

        subjects = [subject for page in pages for subject in page.subjects]
        subjects = unique(subjects, lambda x: x.dnevnik_id)
        if save:
            for subject in subjects:
                subject.save()
        subjects_map = {subject.dnevnik_id: subject for subject in subjects}
        lessons = [Lesson(klass=page.klass, subject=subjects_map[subject.dnevnik_id])
                   for page in pages for subject in page.subjects]
        if save:
            Lesson.objects.bulk_create(lessons)
        return subjects, lessons


