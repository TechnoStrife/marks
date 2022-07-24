from collections import OrderedDict
from typing import List

from bs4.element import Tag

from dnevnik import settings
from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.pages.base_page import BasePage
from dnevnik.support import get_query_params, exclude_navigable_strings, timer
from main.models import Period, Lesson, Teacher, Student, TerminalMark, SemesterMark

__all__ = ['SummaryPage']


class SummaryPage(BasePage):
    URL = 'https://schools.dnevnik.ru/journals/journalclassical.aspx'

    def __init__(self, lesson: Lesson, year=None):
        super().__init__({
            'view': 'subject',
            'school': settings.SCHOOL_ID,
            'group': lesson.klass.dnevnik_id,
            'subject': lesson.subject.dnevnik_id,
            'period': '0',
            'year': year
        })
        self.save_students: List[Student] = []
        self.year: int = year
        self.lesson: Lesson = lesson
        self.periods: List[Period] = []
        self.semester_marks: OrderedDict[Student, List[SemesterMark]] = OrderedDict()
        self.terminal_marks: OrderedDict[Student, List[TerminalMark]] = OrderedDict()
        self.no_marks: bool = False
        self.no_teacher: bool = False
        self.unknown_teacher: bool = False
        self.unknown_students: List[Student] = []

    def __str__(self):
        if self.parsed:
            marks_count = sum(len(marks) for marks in self.semester_marks.values())
            return f'<SummaryPage marks={marks_count}>'
        else:
            return '<SummaryPage>'

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
            periods[z] = Period.objects.get(num=z + 1, year=self.year, dnevnik_id=dnevnik_id)
        self.periods = periods

    def _extract_teacher(self, info):
        teacher_soup = info.find(class_='leads')

        if 'На этот предмет учитель не назначен' in str(teacher_soup):
            self.no_teacher = True
            return

        if teacher_soup.find(class_='u') is None:
            teacher_name = teacher_soup.contents[-1].strip()
            self.lesson.teacher = Teacher.objects.get_or_create(full_name=teacher_name)[0]
            self.unknown_teacher = True
            return

        teacher_soups = teacher_soup.find_all(class_='u')
        for teacher_soup in teacher_soups:
            success, teacher = self.try_find_teacher(teacher_soup)
            if success:
                self.lesson.teacher = teacher
                break
        else:
            self.unknown_teacher = True

    def try_find_teacher(self, teacher_soup: Tag):
        teacher_name = teacher_soup.text
        dnevnik_id = int(get_query_params(teacher_soup['href'], 'user'))
        if self.lesson.teacher is not None and self.lesson.teacher.check_name(teacher_name):
            return False, None
        check_name = self.lesson.teacher is None
        if Teacher.objects.filter(dnevnik_id=dnevnik_id).exists():
            teacher = Teacher.objects.get(dnevnik_id=dnevnik_id)
        elif Teacher.objects.filter(full_name=teacher_name).exists():
            teacher = Teacher.objects.get(full_name=teacher_name)
        else:
            teacher = Teacher(full_name=teacher_name, dnevnik_id=dnevnik_id)
            return False, teacher

        if check_name:
            if not teacher.check_name(teacher_name):
                return False, None
        return True, teacher

    def _parse_periods(self, table: Tag) -> List[Period]:
        row = exclude_navigable_strings(table.find('thead').find('tr'))
        periods = []
        prev_num = 0
        for cell in row:
            if 'total' not in cell.attrs.get('class', {}):
                continue
            if cell.text[0].isdigit():
                num = int(cell.text[:cell.text.find(' ')])
                assert num == prev_num + 1
                prev_num = num
                periods.append(self.periods[num - 1])
            if cell.text == 'Год':
                break
        return periods

    def _parse_table(self):
        table: Tag = self.soup.find('table')
        periods = self._parse_periods(table)
        rows = exclude_navigable_strings(table.find('tbody'))
        for row in rows:
            row = exclude_navigable_strings(row)[1:]  # First td contains useless column number
            person_cell, *row = row
            dnevnik_person_id = int(get_query_params(person_cell.a['href'], 'student'))
            name = ' '.join(person_cell.a.text.split())
            student = Student.objects.filter(dnevnik_person_id=dnevnik_person_id)
            if not student.exists():
                student = Student.objects.filter(full_name__contains=name)

            if student.exists():
                student = student.first()
            else:
                print('unknown student in SummaryPage', name, self.response.url)
                continue

            self.semester_marks[student] = []

            for cell, period in zip(row, periods):
                mark = self._parse_cell(cell)
                if mark is None:
                    continue
                mark = SemesterMark(mark=mark, student=student, lesson_info=self.lesson, period=period)
                self.semester_marks[student].append(mark)

            assert len(row) == len(periods) + len(TerminalMark.TYPES)
            for terminal_mark, mark_type in zip(row[-len(TerminalMark.TYPES):], TerminalMark.TYPES):
                terminal_mark = self._parse_cell(terminal_mark)
                if terminal_mark is None:
                    continue
                terminal_mark = TerminalMark(mark=terminal_mark, student=student,
                                             lesson_info=self.lesson, year=self.year, type=mark_type)
                self.terminal_marks.setdefault(student, []).append(terminal_mark)

    @staticmethod
    def _parse_cell(cell):
        presence, mark = exclude_navigable_strings(cell.span)
        assert presence.text.strip() == ''
        mark = mark.get_text().strip()
        assert '/' not in mark
        return int(mark) if mark != '' else None

    @staticmethod
    def scan_all(fetch_queue: FetchQueueProcessor, lessons: List[Lesson], save: bool = False):
        pages: List[SummaryPage] = [SummaryPage(lesson) for lesson in lessons]
        fetch_queue.process(pages)

        semester_marks: List[SemesterMark] = []
        terminal_marks: List[TerminalMark] = []
        for page in pages:
            for marks in page.semester_marks.values():
                semester_marks.extend(marks)
            for marks in page.terminal_marks.values():
                terminal_marks.extend(marks)

        if save:
            with timer('marks'):
                SemesterMark.objects.bulk_create(semester_marks)
                TerminalMark.objects.bulk_create(terminal_marks)

        return semester_marks, terminal_marks
