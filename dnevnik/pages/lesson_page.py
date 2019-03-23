import re
from collections import OrderedDict
from datetime import date as Date
from typing import List, Dict

from bs4.element import Tag

from dnevnik import settings
from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage
from dnevnik.support import get_query_params, exclude_navigable_strings
from main.models import Period, Lesson, Teacher, Mark, Student

__all__ = ['LessonPage']


def transform_mark(mark: str):
    if mark == '':
        return None
    if mark[-1] in ('+', '-'):
        mark = mark[:-1]
    return int(mark)


class LessonPage(BasePage):
    URL = 'https://schools.dnevnik.ru/journals/journalclassical.aspx'

    def __init__(self, lesson: Lesson, period: Period = None, year=None):
        super().__init__({
            'view': 'subject',
            'school': settings.SCHOOL_ID,
            'group': lesson.klass.dnevnik_id,
            'subject': lesson.subject.dnevnik_id,
            'period': str(period.dnevnik_id) if period is not None else None,
            'year': year
        })
        self.year: int = year
        self.lesson: Lesson = lesson
        self.period: Period = period
        self.periods: List[Period] = None
        self.marks: OrderedDict[Student, List[Mark]] = OrderedDict()
        self.no_marks: bool = False
        self.no_teacher: bool = False
        self.unknown_teacher: bool = False
        self.unknown_students: List[str] = []

    def __str__(self):
        if self.parsed:
            return f'<LessonPage marks={len(self.marks)}>'
        else:
            return '<LessonPage>'

    def parse(self):
        if 'Страница не найдена (404)' in self.response.text:
            raise RuntimeError('404 ' + self.response.url)
        try:
            self._extract_info()
        except Teacher.DoesNotExist:
            self.parsed = True
            self.unknown_teacher = True
            self.no_marks = True
            return self

        if self.period is None:
            self.parsed = True
            return self  # TODO if journal shows summary marks

        if 'За выбранный период уроков нет' in self.response.text:
            self.no_marks = True
        else:
            self._parse_table()
        self.parsed = True
        return self

    def _extract_info(self):
        info = self.soup.find(class_='l')

        assert info.find(class_='m10').h2.text.strip() == self.lesson.subject.name
        year = int(info.find(class_='m10').h3.text[:4])
        if self.year is None:
            self.year = year
        else:
            assert self.year == year

        teacher_soup = info.find(class_='leads')
        if 'На этот предмет учитель не назначен' in str(teacher_soup):
            self.no_teacher = True
        else:
            teacher_soup = teacher_soup.find(class_='u')
            dnevnik_id = int(get_query_params(teacher_soup['href'], 'user'))
            if not Teacher.objects.filter(dnevnik_id=dnevnik_id).exists():
                print()
            self.lesson.teacher = Teacher.objects.get(dnevnik_id=dnevnik_id)
            assert self.lesson.teacher.check_name(teacher_soup.text)

        periods = info.find(class_='period_list')
        periods = periods.find_all(class_='journal-link-period')
        for z, period in enumerate(periods):
            dnevnik_id = int(period['data-period-id'])
            periods[z] = Period(num=z + 1, year=self.year, dnevnik_id=dnevnik_id)
            if 'active' in period.a['class'] and self.period is None:
                self.period = periods[z]
        self.periods = periods

    def _parse_dates(self, table: Tag) -> List[Date]:
        day_regex = re.compile(r'^day_(?P<period>\d)_(?P<month>\d{1,2})_(?P<day>\d{1,2})$')
        dates = table.find_all(id=day_regex)
        for z, date in enumerate(dates):
            date = day_regex.match(date['id'])
            month = int(date.group('month'))
            day = int(date.group('day'))
            year = self.year if month > 6 else self.year + 1
            dates[z] = Date(year=year, month=month, day=day)
        return dates

    def _parse_table(self):
        table: Tag = self.soup.find('table')
        dates = self._parse_dates(table)
        rows = exclude_navigable_strings(table.find('tbody'))
        for row in rows:
            row = exclude_navigable_strings(row)[1:]  # First td contains useless column number
            dnevnik_person_id = int(get_query_params(row[0].a['href'], 'student'))
            student = Student.objects.filter(dnevnik_person_id=dnevnik_person_id)
            if not student.exists():
                name = row[0].a.text.split()
                self.unknown_students.append(' '.join(name) + ' ' + self.response.url)
                continue
            student = student[0]
            student.dnevnik_student_id = int(row.pop(0)['id'])
            student_marks: List[Mark] = []
            for cell, date in zip(row, dates):
                presence, marks = exclude_navigable_strings(cell.span)
                presence = Mark.PRESENT if presence.text.strip() == '' else Mark.ABSENT
                marks = marks.get_text().strip()
                marks = marks.split('/')
                if marks == [''] and presence == Mark.PRESENT:
                    marks = []
                marks = map(transform_mark, marks)
                marks = [Mark(mark=mark, presence=presence, student=student,
                              lesson_info=self.lesson, period=self.period, date=date)
                         for mark in marks]
                student_marks.extend(marks)
            self.marks[student] = student_marks

    @staticmethod
    def scan_all(fetch_queue: FetchQueueProcessor, lessons: List[Lesson], save: bool = False):
        pages = [LessonPage(lesson) for lesson in lessons]
        fetch_queue.process(pages)
        pages2 = []
        for page in pages:
            periods: List[Period] = page.periods.copy()
            periods.remove(page.period)
            for period in periods:
                pages2.append(LessonPage(page.lesson, period, page.year))
        fetch_queue.process(pages2)
        pages += pages2
        del pages2
        print('unknown_students:', sum(len(page.unknown_students) for page in pages))

        marks: List[Mark] = []
        periods: Dict[int, Period] = {}
        for page in pages:
            for period in page.periods:
                periods[period.dnevnik_id] = period
            for student_marks in page.marks.values():
                marks.extend(student_marks)
        del pages
        if save:
            for period in periods.values():
                period.save()
            for mark in marks:
                mark.period = periods[mark.period.dnevnik_id]
            Mark.objects.bulk_create(marks)
        return marks, periods
