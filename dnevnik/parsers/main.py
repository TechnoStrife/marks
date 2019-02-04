import django

from dnevnik import dnevnik_settings
from dnevnik.parsers.basic import login
from dnevnik.parsers.klasses import scan_classes_by_year, scan_class
from dnevnik.parsers.users import scan_all_students

django.setup()


def main():
    print('Logging')
    session = login()

    # scan_all_teachers(session)
    scan_all_students(session)
    quit()

    for year in range(dnevnik_settings.current_year(), dnevnik_settings.VERY_FIRST_YEAR - 1, -1):
        classes = scan_classes_by_year(session, year)
        for klass in classes:
            klass = scan_class(session, klass['name'], klass['id'], year)
            if klass.final_class is not None:
                print('%s (%s) -> %s (%s)' % (klass.name, klass.year, klass.final_class.name, klass.final_class.year))
            else:
                print('%s (%s)' % (klass.name, klass.year))


if __name__ == '__main__':
    main()
