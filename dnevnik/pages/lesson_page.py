import re
from collections import OrderedDict
from datetime import date as Date
from typing import List

from bs4.element import Tag
from django.db.models import Q

from dnevnik import settings
from dnevnik.pages.base_page import BasePage
from dnevnik.support import get_query_params, exclude_navigable_strings
from main.models import Class, Subject, Period, Lesson, Teacher, Mark, Student

__all__ = ['LessonPage']


class LessonPage(BasePage):
    URL = 'https://schools.dnevnik.ru/journals/journalclassical.aspx'

    def __init__(self, lesson: Lesson, period: Period = None, year=None):
        super().__init__({
            'view': 'subject',
            'school': settings.SCHOOL_ID,
            'group': lesson.klass.dnevnik_id,
            'subject': lesson.subject.dnevnik_id,
            'period': str(period.dnevnik_id),
            'year': year
        })
        self.year: int = year
        self.lesson: Lesson = lesson
        self.period: Period = period
        self.periods: List[Period] = None
        self.marks: OrderedDict[Student, List[Mark]] = OrderedDict()

    def parse(self):
        if 'Страница не найдена (404)' in self.response.text:
            raise RuntimeError('404 ' + self.response.url)
        self._extract_info()

        if self.period is None:
            return  # TODO if journal shows summary marks

        self._parse_table()

    def _extract_info(self):
        info = self.soup.find(class_='l')

        assert info.find(class_='m10').h2.text.strip() == self.lesson.subject.name
        year = int(info.find(class_='m10').h3.text[:4])
        if self.year is None:
            self.year = year
        else:
            assert self.year == year

        teacher_soup = info.find(class_='leads').find(class_='u')
        dnevnik_id = int(get_query_params(teacher_soup['href'], 'user'))
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
            dates[z] = Date(year=self.year, month=month, day=day)
        return dates

    def _parse_table(self):
        table: Tag = self.soup.find('table')
        dates = self._parse_dates(table)
        rows = exclude_navigable_strings(table.find('tbody'))
        for row in rows:
            row = exclude_navigable_strings(row)[1:]  # First td contains useless column number
            name = row[0].a.text.split()
            student = Student.objects.filter(Q(full_name__contains=name[0])
                                             & Q(full_name__contains=name[1]))
            assert student.exists()
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
                marks = [int(mark) if mark != '' else None for mark in marks]
                marks = [Mark(mark=mark, presence=presence, student=student,
                              lesson_info=self.lesson, period=self.period, date=date)
                         for mark in marks]
                student_marks.extend(marks)
            self.marks[student] = student_marks
