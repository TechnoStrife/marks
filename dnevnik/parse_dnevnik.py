from time import time

import django

from dnevnik.settings import current_year

django.setup()

from dnevnik.support import login
from dnevnik.pages import *
from dnevnik.fetch_queue import FetchQueueProcessor
from main.models import *


def main():
    print('Logging in...', end=' ')
    session = login()
    print('done')
    fetch_queue = FetchQueueProcessor(session)
    fetch_queue.start()

    print('subject types')
    SubjectTypesPage().fetch(session).parse(save=True)

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

    xss_token = ClassesListPage(year=current_year()).fetch(session).parse_xss()
    Subject.objects.all().delete()
    Lesson.objects.all().delete()
    print('subjects')
    SubjectsPage.scan_all_classes(fetch_queue, Class.objects.all(), xss_token, save=True)

    Mark.objects.all().delete()
    Period.objects.all().delete()
    print('marks')
    LessonPage.scan_all(fetch_queue, Lesson.objects.all(), save=True)

    fetch_queue.stop()


if __name__ == '__main__':
    t = time()
    main()
    print()
    print(f'Total time: {round(time() - t, 3)} s')
