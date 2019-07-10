from itertools import zip_longest
from typing import Dict, List

import django

from dnevnik.settings import current_year

django.setup()

from dnevnik.support import timer, remove_equal_items, login
from dnevnik.pages import *
from dnevnik.fetch_queue import FetchQueueProcessor
from main.models import *


def get_active_periods(fetch_queue: FetchQueueProcessor, classes: List[Class]) -> Dict[Class, Period]:
    xss_token = fetch_xss_token(fetch_queue.session)
    pages = [SubjectsPage(klass, xss_token) for klass in classes]
    fetch_queue.process(pages)
    res = {}
    for page in pages:
        if page.period != 0:
            res[page.klass] = Period.objects.get(dnevnik_id=page.period)
    return res


def initial_scan(fetch_queue: FetchQueueProcessor):
    print('subject types')
    SubjectTypesPage().fetch(fetch_queue.session).parse(save=True)

    Teacher.objects.all().delete()
    print('teachers')
    TeacherListPage.scan_all(fetch_queue, save=True)
    print('teachers archive')
    TeacherListPage.scan_all(fetch_queue, save=True, archive=True)

    Class.objects.all().delete()
    print('classes')
    ClassPage.scan_all_classes(fetch_queue, save=True)

    Student.objects.all().delete()
    print('students')
    StudentListPage.scan_all(fetch_queue, save=True)
    print('students archive')
    StudentListPage.scan_all(fetch_queue, save=True, archive=True)

    xss_token = fetch_xss_token(fetch_queue.session)
    Subject.objects.all().delete()
    Lesson.objects.all().delete()
    print('subjects')
    SubjectsPage.scan_all_classes(fetch_queue, Class.objects.all(), xss_token, save=True)

    Mark.objects.all().delete()
    Period.objects.all().delete()
    print('marks')
    LessonPage.scan_all(fetch_queue, Lesson.objects.all(), save=True)
    print('summary marks')
    SummaryPage.scan_all(fetch_queue, Lesson.objects.all(), save=True)


def everyday_scan(fetch_queue: FetchQueueProcessor):
    cur_year = current_year()
    classes = Class.objects.filter(year=cur_year)
    active_periods = get_active_periods(fetch_queue, classes)
    pages = []
    summary_pages = []
    for lesson in Lesson.objects.filter(klass__year=cur_year):
        if lesson.klass in active_periods:
            page = LessonPage(lesson, period=active_periods[lesson.klass], year=cur_year)
            pages.append(page)
        summary_page = SummaryPage(lesson, year=cur_year)
        summary_pages.append(summary_page)
    fetch_queue.process(pages + summary_pages)

    print('save marks')
    insert_marks = extract_and_save_marks(
        pages,
        Mark,
        page_marks=lambda page: page.marks,
        custom_filter=lambda marks, page: marks.filter(
            period=page.period,
            is_semester=False,
            is_terminal=False
        )
    )
    print()
    print(len(insert_marks), 'new marks')

    print('save semester marks')
    insert_marks = extract_and_save_marks(
        summary_pages,
        SemesterMark,
        page_marks=lambda page: page.semester_marks,
        custom_filter=lambda marks, _: marks.filter(period__year=cur_year)
    )
    print()
    print(len(insert_marks), 'new marks')
    print('save terminal marks')
    insert_marks = extract_and_save_marks(
        summary_pages,
        TerminalMark,
        page_marks=lambda page: page.terminal_marks,
        custom_filter=lambda marks, _: marks.filter(year=cur_year)
    )
    print()
    print(len(insert_marks), 'new marks')


def extract_and_save_marks(pages, mark_type, page_marks, custom_filter):
    mark_groups = [(page, student, marks)
                   for page in pages
                   for student, marks in page_marks(page).items()
                   if student not in page.unknown_students]
    insert_marks = []
    for z, group in enumerate(mark_groups):
        page, student, new_marks = group
        print(f'\r{z + 1}/{len(mark_groups)}', end='')

        marks = mark_type.objects.filter(student=student, lesson_info=page.lesson)
        marks = custom_filter(marks, page)
        to_insert = sync_marks(list(marks), new_marks)
        insert_marks.extend(to_insert)
    if insert_marks:
        mark_type.objects.bulk_create(insert_marks)
    return insert_marks


def sync_marks(current: List[BaseMark], new: List[BaseMark]):
    update_fields = {
        Mark: ['mark', 'presence', 'date'],
        SemesterMark: ['mark', 'period'],
        TerminalMark: ['mark', 'type'],
    }
    if len(current) == len(new) == 0:
        return []

    remove_equal_items(current, new, lambda mark1, mark2: mark1.equals(mark2))
    to_insert = []
    for mark, new_mark in zip_longest(current, new):
        if mark is None:
            to_insert.append(new_mark)
        elif new_mark is None:
            mark.delete()
        else:
            assert type(mark) is type(new_mark)
            new_mark.id = mark.id
            new_mark.pk = mark.pk
            new_mark.save(update_fields=update_fields[type(new_mark)])
    return to_insert


def scan_teachers(fetch_queue: FetchQueueProcessor):
    print('teachers')
    teachers = TeacherListPage.scan_all(fetch_queue)
    for teacher in teachers:
        teacher.update_or_create('dnevnik_person_id')


def scan_students(fetch_queue: FetchQueueProcessor):
    print('students')
    students = StudentListPage.scan_all(fetch_queue)
    # students += StudentListPage.scan_all(fetch_queue, archive=True)

    with timer('saving students'):
        for student in students:
            student.update_or_create('dnevnik_person_id')


def main():
    with timer('Total time', after=True):
        session = login()
        with FetchQueueProcessor(session) as fetch_queue:
            # scan_teachers(fetch_queue)
            # scan_students(fetch_queue)
            everyday_scan(fetch_queue)


if __name__ == '__main__':
    main()
