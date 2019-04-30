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


def everyday_scan(fetch_queue: FetchQueueProcessor):
    classes = Class.objects.filter(year=current_year())
    active_periods = get_active_periods(fetch_queue, classes)
    pages = []
    for lesson in Lesson.objects.filter(klass__year=current_year()):
        page = LessonPage(lesson, period=active_periods[lesson.klass], year=current_year())
        pages.append(page)
    fetch_queue.process(pages)

    z = 0
    loops_num = sum(len(page.marks) for page in pages)
    insert = []
    for page in pages:
        for student, new_marks in page.marks.items():
            z += 1
            print(f'\r{z}/{loops_num}', end='')

            if student in page.unknown_students:
                continue

            marks = Mark.objects.filter(student=student, lesson_info=page.lesson, period=page.period,
                                        is_semester=False, is_terminal=False)
            marks = list(marks)
            to_insert = sync_marks(marks, new_marks)
            insert.extend(to_insert)
    print()
    print(len(insert), 'new marks')
    Mark.objects.bulk_create(insert)


def sync_marks(current: List[Mark], new: List[Mark]):
    if len(current) == 0 and len(new) == 0:
        return []

    remove_equal_items(current, new, lambda mark1, mark2: mark1.equals(mark2))
    to_insert = []
    for mark, new_mark in zip_longest(current, new):
        if mark is None:
            to_insert.append(new_mark)
        elif new_mark is None:
            mark.delete()
        else:
            mark.mark = new_mark.mark
            mark.presence = new_mark.presence
            mark.date = new_mark.date
            mark.save(update_fields=['mark', 'presence', 'date'])
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

    for student in students:
        student.update_or_create('dnevnik_person_id')


if __name__ == '__main__':
    with timer('Total time', after=True):
        session = login()
        with FetchQueueProcessor(session) as fetch_queue:
            scan_teachers(fetch_queue)
            scan_students(fetch_queue)
            everyday_scan(fetch_queue)
