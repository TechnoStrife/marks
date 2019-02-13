import django
django.setup()

from dnevnik.parsers.support import login
from dnevnik.pages import *

from main.models import *


def delete_all():
    Class.objects.all().delete()
    Teacher.objects.all().delete()
    Student.objects.all().delete()


def main():
    delete_all()
    print('Logging in')
    session = login()

    teachers = TeacherListPage.scan_all_pages(session)
    Teacher.objects.bulk_create(teachers)

    classes = YearPage.scan_all_years(session)

    for z, klass in enumerate(classes):
        class_page = ClassPage(name=klass.name, class_id=klass.dnevnik_id, year=klass.year)
        class_page.fetch(session).parse()
        klass = class_page.klass
        classes[z] = klass
        if klass.final_class is not None:
            print('%s (%s) -> %s (%s)' % (klass.name, klass.year, klass.final_class.name, klass.final_class.year))
        else:
            print('%s (%s)' % (klass.name, klass.year))

    not_saved_teachers = [klass.head_teacher for klass in classes if klass.head_teacher]
    not_saved_teachers = [klass.head_teacher for klass in classes if klass.head_teacher.pk is None]
    Teacher.objects.bulk_create()
    Class.objects.bulk_create(classes)

    students = StudentListPage.scan_all_pages(session)
    Student.objects.bulk_create(students)
    quit()


if __name__ == '__main__':
    main()
