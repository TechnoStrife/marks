import re
from collections import OrderedDict
from datetime import date as Date
from time import time
from typing import List, Dict

from bs4.element import Tag

from dnevnik import settings
from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage
from dnevnik.support import get_query_params, exclude_navigable_strings, timer
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
        self.save_students: List[Student] = []
        self.year: int = year
        self.lesson: Lesson = lesson
        self.period: Period = period
        self.periods: List[Period] = []
        self.marks: OrderedDict[Student, List[Mark]] = OrderedDict()
        self.no_marks: bool = False
        self.no_teacher: bool = False
        self.unknown_teacher: bool = False
        self.unknown_students: List[Student] = []
        self.unknown_students_urls: List[str] = []

    def __str__(self):
        if self.parsed:
            marks_count = sum(len(marks) for marks in self.marks.values())
            return f'<LessonPage marks={marks_count}>'
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
        info = self.soup.find(class_='header_journal')

        assert info.find(class_='m10').h2.text.strip() == self.lesson.subject.name
        year = int(info.find(class_='m10').h3.text[:4])
        if self.year is None:
            self.year = year
        else:
            assert self.year == year

        self._extract_teacher(info)

        periods = info.find(class_='period_list')
        periods = periods.find_all(class_='journal-link-period')
        for z, period in enumerate(periods):
            dnevnik_id = int(period['data-period-id'])
            periods[z] = Period(num=z + 1, year=self.year, dnevnik_id=dnevnik_id)
            if 'active' in period.a['class'] and self.period is None:
                self.period = periods[z]

        self.periods = periods

    def _extract_teacher(self, info):
        teacher_soup = info.find(class_='leads')

        if 'На этот предмет учитель не назначен' in str(teacher_soup):
            self.no_teacher = True
            return

        teacher_soup = teacher_soup.find(class_='u')
        teacher_name = teacher_soup.text
        dnevnik_id = int(get_query_params(teacher_soup['href'], 'user'))

        if self.lesson.teacher is not None and self.lesson.teacher.check_name(teacher_name):
            return
        check_name = self.lesson.teacher is None
        if Teacher.objects.filter(dnevnik_id=dnevnik_id).exists():
            self.lesson.teacher = Teacher.objects.get(dnevnik_id=dnevnik_id)
        else:
            self.lesson.teacher = Teacher(full_name=teacher_name, dnevnik_id=dnevnik_id)
            self.unknown_teacher = True
            raise RuntimeError()

        if check_name:
            assert self.lesson.teacher.check_name(teacher_name)

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
            if student.exists():
                student = student.first()
            else:
                name = ' '.join(row[0].a.text.split())
                student = Student(full_name=name, dnevnik_person_id=dnevnik_person_id)
                self.unknown_students.append(student)
                self.unknown_students_urls.append(name + ' ' + self.response.url)

            if student.need_to_update_classes(self.lesson.klass, self.period):
                self.save_students.append(student)
            self.marks[student] = []
            for cell, date in zip(row[1:], dates):
                student_marks = self._parse_cell(cell, date, student)
                self.marks[student].extend(student_marks)

    def _parse_cell(self, cell, date, student):
        presence, marks = exclude_navigable_strings(cell.span)
        presence = Mark.PRESENT if presence.text.strip() == '' else Mark.ABSENT
        marks = marks.get_text().strip()
        marks = marks.split('/')  # like '5/4'
        if marks == [''] and presence == Mark.PRESENT:
            marks = []
        marks = map(transform_mark, marks)
        marks = [Mark(mark=mark, presence=presence, student=student,
                      lesson_info=self.lesson, period=self.period, date=date)
                 for mark in marks]
        return marks

    @staticmethod
    def scan_all(fetch_queue: FetchQueueProcessor, lessons: List[Lesson], save: bool = False):
        pages: List[LessonPage] = [LessonPage(lesson) for lesson in lessons]
        fetch_queue.process(pages)
        pages2 = []
        for page in pages:
            periods: List[Period] = page.periods.copy()
            if page.period in periods:
                periods.remove(page.period)
            for period in periods:
                pages2.append(LessonPage(page.lesson, period, page.year))
        fetch_queue.process(pages2)
        pages += pages2
        del pages2

        unknown_students = [student for page in pages for student in page.unknown_students]
        print('unknown_students:', unknown_students)

        marks: List[Mark] = []
        periods: Dict[int, Period] = {}
        for page in pages:
            for period in page.periods:
                periods[period.dnevnik_id] = period
            for student_marks in page.marks.values():
                marks.extend(student_marks)

        if unknown_students:
            LessonPage._replace_unknown_students(marks, unknown_students)

        if save:
            for unknown_student in unknown_students:
                unknown_student.save()

            with timer('periods'):
                for period in periods.values():
                    period.save()

            with timer('students'):
                LessonPage._save_students(pages, marks)

            LessonPage._save_lessons(pages, periods)

            with timer('marks'):
                for mark in marks:
                    mark.period = periods[mark.period.dnevnik_id]
                Mark.objects.bulk_create(marks)

        return marks, periods, unknown_students

    @staticmethod
    def _replace_unknown_students(marks, unknown_students):
        unknown_students_map = {student.dnevnik_person_id: student for student in unknown_students}
        for mark in marks:
            if mark.student.dnevnik_person_id in unknown_students_map:
                mark.student = unknown_students_map[mark.student.dnevnik_person_id]

    @staticmethod
    def _save_lessons(pages, periods):
        t1 = 0
        t2 = 0
        t3 = 0
        saved_classes = set()
        for index, page in enumerate(pages):
            print(f'\rpages {index + 1}/{len(pages)} {round(t1)}:{round(t2)}:{round(t3)}', end='')
            t = time()
            page.lesson.save()
            t1 += time() - t
            if page.lesson.klass.id in saved_classes:
                continue
            else:
                saved_classes.add(page.lesson.klass.id)
            t = time()
            page.periods = [periods[period.dnevnik_id] for period in page.periods]
            page.lesson.klass.periods.set(page.periods)
            t2 += time() - t
            t = time()
            page.lesson.klass.periods_count = len(page.periods)
            page.lesson.klass.save()
            t3 += time() - t
        print()

    @staticmethod
    def _save_students(pages, marks):
        students = (student for page in pages for student in page.save_students)
        students = {student.dnevnik_person_id: student for student in students}
        students_marks = {student_person_id: {} for student_person_id in students.keys()}
        for mark in marks:
            student_marks_by_class = students_marks[mark.student.dnevnik_person_id]
            # we need only 1 mark from every class
            # because we need to get classes in which student has got any marks
            student_marks_by_class[mark.lesson_info.klass] = mark

        i = 0
        for student_person_id, student_marks in students_marks.items():
            i += 1
            print(f'\rstudents {i}/{len(students)}', end='')
            if len(student_marks) == 0:
                continue
            student_marks = student_marks.values()
            student = students[student_person_id]
            student.set_classes_by_marks(student_marks)
        print('\rstudents ', end='')
