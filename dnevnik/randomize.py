import mimesis
import django
from mimesis.builtins import RussiaSpecProvider
from mimesis.enums import Gender

import dnevnik

django.setup()

from main.base_models import PersonModel
from main.models import Teacher, Student, Period, Class, Subject

random_person = mimesis.Person('ru')
random_date = mimesis.Datetime()
russian_random = RussiaSpecProvider()


def autoinc(num):
    def inc():
        nonlocal num
        num += 1
        return num
    return inc


dnevnik_id_num = autoinc(1000000000000)
dnevnik_person_id_num = autoinc(1000000000000)
period_num = autoinc(1000000000000000000)
class_num = autoinc(1000000000000000000)
subject_num = autoinc(3000000000000000)


def gender(person: PersonModel) -> Gender:
    first_name = person.full_name.split()[1]
    if first_name in ['Любовь']:
        return Gender.FEMALE
    if first_name[-1] in ['а', 'я']:
        return Gender.FEMALE
    return Gender.MALE


def random_full_name(gender: Gender = None, surname: str = None) -> str:
    name, new_surname = random_person.full_name(gender).split()
    if surname is None:
        surname = new_surname
    patronymic = russian_random.patronymic(gender)
    return ' '.join([surname, name, patronymic])


def randomize_person(person: PersonModel):
    person.full_name = random_full_name(gender(person))
    if person.birthday is not None:
        person.birthday = random_date.date(person.birthday.year, person.birthday.year)
    if person.tel is not None:
        person.tel = random_person.telephone()
    if person.email is not None:
        person.email = random_person.email()
    if person.dnevnik_id is not None:
        person.dnevnik_id = dnevnik_id_num()
    if person.dnevnik_person_id is not None:
        person.dnevnik_person_id = dnevnik_person_id_num()


def randomize_teachers():
    count = Teacher.objects.count()
    for z, teacher in enumerate(Teacher.objects.all()):
        randomize_person(teacher)
        teacher.save()
        print(f'\rteachers {z + 1}/{count}', end='')
    print()


def randomize_students():
    count = Student.objects.count()
    for z, student in enumerate(Student.objects.all()):
        randomize_person(student)
        student.info = None
        if student.parents is not None:
            father = random_full_name(gender=Gender.MALE, surname=student.surname)
            mother = random_full_name(gender=Gender.FEMALE, surname=student.surname)
            student.parents = f'{father}, {mother}'
        student.save()
        print(f'\rstudents {z + 1}/{count}', end='')
    print()


def drop_dnevnik_ids():
    print('dropping dnevnik_ids... ', end='')
    for z, period in enumerate(Period.objects.all()):
        period.dnevnik_id = period_num()
        period.save()
    for z, klass in enumerate(Class.objects.all()):
        klass.dnevnik_id = class_num()
        klass.save()
    for z, subject in enumerate(Subject.objects.all()):
        subject.dnevnik_id = subject_num()
        subject.save()
    # Period.objects.update(dnevnik_id=1000000000000000000)
    # Class.objects.update(dnevnik_id=1000000000000000000)
    # Subject.objects.update(dnevnik_id=3000000000000000)
    print('done')


def main():
    randomize_teachers()
    randomize_students()
    drop_dnevnik_ids()


if __name__ == '__main__':
    main()
