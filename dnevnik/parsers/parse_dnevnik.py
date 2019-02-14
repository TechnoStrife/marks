from time import time
import django

django.setup()

from dnevnik.parsers.support import login
from dnevnik.pages import *
from dnevnik.fetch_queue import FetchQueueProcessor

from main.models import *


def main():
    Class.objects.all().delete()
    Teacher.objects.all().delete()
    Student.objects.all().delete()

    t = time()
    print('Logging in')
    session = login()
    fetch_queue = FetchQueueProcessor(session)
    fetch_queue.start()

    teachers = TeacherListPage.scan_all_pages(fetch_queue)
    Teacher.objects.bulk_create(teachers)
    del teachers

    classes = YearPage.scan_all_years(session)

    classes = ClassPage.scan_all_classes(classes, fetch_queue)
    Teacher.objects.bulk_create(
        [klass.head_teacher for klass in classes
            if klass.head_teacher and klass.head_teacher.pk is None]
    )
    Class.objects.bulk_create(classes)
    del classes

    students = StudentListPage.scan_all_pages(fetch_queue)
    Student.objects.bulk_create(students)
    del students
    fetch_queue.stop()
    print(time() - t)


if __name__ == '__main__':
    main()
