from time import time
import django


django.setup()

from dnevnik.support import login
from dnevnik.pages import *
from dnevnik.pages.subjects_page import SubjectsPage
from dnevnik.fetch_queue import FetchQueueProcessor
from dnevnik.settings import current_year
from main.models import *


def main():
    print('Logging in')
    session = login()
    fetch_queue = FetchQueueProcessor(session)
    fetch_queue.start()

    # Teacher.objects.all().delete()
    # TeacherListPage.scan_all_pages(fetch_queue, save=True)

    # Class.objects.all().delete()
    # ClassPage.scan_all_classes(fetch_queue, save=True)

    # Student.objects.all().delete()
    # StudentListPage.scan_all_pages(fetch_queue, save=True)

    xss_token = ClassesListPage(year=current_year()).fetch(session).parse_xss()
    Subject.objects.all().delete()
    _, lessons = SubjectsPage.scan_all_classes(fetch_queue, Class.objects.all(), xss_token, save=True)

    fetch_queue.stop()


if __name__ == '__main__':
    t = time()
    main()
    print(time() - t)
