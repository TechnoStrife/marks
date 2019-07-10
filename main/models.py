from typing import Union, Iterable

from django.db.models import *

from dnevnik.support import unique
from main.base_models import MyModel as Model, PersonModel

__all__ = [
    'Period',
    'Student',
    'Teacher',
    'Class',
    'SubjectType',
    'Subject',
    'Lesson',
    'BaseMark',
    'Mark',
    'SemesterMark',
    'TerminalMark'
]


class Period(Model):
    num = SmallIntegerField(verbose_name='Четверть')
    year = SmallIntegerField(verbose_name='Уч. год')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)

    def __str__(self):
        return '%s четверть %s года' % (self.num, str(self.year))

    class Meta:
        verbose_name = 'четверть'
        verbose_name_plural = 'четверти'


class Teacher(PersonModel):
    job = CharField(max_length=128, verbose_name='Должность', null=True)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f'<Teacher {str(self)}>'

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'


class Class(Model):
    name = CharField(max_length=3, verbose_name='Класс')
    info = CharField(max_length=4096, verbose_name='Примечания', null=True)
    head_teacher = ForeignKey(Teacher, on_delete=CASCADE, verbose_name='Классный руководитель',
                              null=True, related_name='head_in_classes')
    year = SmallIntegerField(verbose_name='Уч. год')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)
    periods_count = SmallIntegerField(verbose_name='Количество учебных периодов', null=True)  # TODO delete?
    final_class = ForeignKey('self', verbose_name='Конечный класс', on_delete=SET_NULL, null=True)
    periods = ManyToManyField(Period, db_table='class_periods', verbose_name='Семестры', related_name='+')

    def __str__(self):
        return self.name + ' класс'

    @property
    def number(self):
        return int(self.name[:-1])

    @property
    def letter(self):
        return self.name[-1]

    def get_students(self):
        return Student.objects.filter(Q(klass=self) | Q(previous_classes=self)).distinct()

    def __repr__(self):
        return '<Class %s>' % self.name

    class Meta:
        verbose_name = 'класс'
        verbose_name_plural = 'классы'


class SubjectType(Model):
    subject_name = CharField(max_length=100, verbose_name='Название предмета', unique=True)
    type = CharField(max_length=100, verbose_name='Образовательная область')

    class Meta:
        verbose_name = 'Образовательная область предметов'
        verbose_name_plural = 'Образовательные области предметов'


class Subject(Model):
    name = CharField(max_length=127, verbose_name='Имя')
    type = CharField(max_length=100, verbose_name='Образовательная область')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)

    def __str__(self):
        return self.name

    def update_type(self):
        try:
            self.type = SubjectType.objects.get(subject_name=self.name).type
        except SubjectType.DoesNotExist:
            self.type = 'Неизвестно'

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'


class Student(PersonModel):
    info = CharField(max_length=4096, verbose_name='Примечания', null=True)

    klass = ForeignKey(Class, verbose_name='Класс', on_delete=CASCADE, null=True, related_name='students')
    previous_classes = ManyToManyField(Class, db_table='students_previous_classes',
                                       verbose_name='Предыдущие классы', related_name='previous_students')

    entered = DateField(verbose_name='Дата начала обучения', null=True)
    leaved = DateField(verbose_name='Дата конца обучения', null=True)

    parents = CharField(max_length=1024, verbose_name='Родители', null=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.klass.name)

    def __repr__(self):
        return f'<Student {str(self)}>'

    def need_to_update_classes(self, new_klass: Class, period: Period) -> bool:
        return True
        last_mark = Mark.objects \
            .filter(lesson_info__klass=self.klass, student=self) \
            .order_by('-date').first()
        if last_mark:
            if last_mark.period.year <= period.year \
                    and last_mark.period.num <= period.num:
                # self.previous_classes.add(self.klass)
                # self.klass = new_klass
                return True
        else:
            # self.klass = new_klass
            return True
        return False

    def set_classes_by_marks(self, marks: Union[None, Iterable['Mark']] = None):
        if marks is None:
            marks = Mark.objects.only('date', 'id') \
                .prefetch_related('lesson_info__klass') \
                .filter(student=self)
        marks = sorted(marks, key=lambda mark: mark.date, reverse=True)
        if len(marks) == 0:
            self.previous_classes.clear()
            return
        classes = unique((mark.lesson_info.klass for mark in marks), key=lambda klass: klass.id)
        self.klass = classes[0]
        self.previous_classes.set(classes[1:])
        self.save()

    class Meta:
        verbose_name = 'ученик'
        verbose_name_plural = 'ученики'


class Lesson(Model):
    klass = ForeignKey(Class, verbose_name='Класс', on_delete=CASCADE)
    subject = ForeignKey(Subject, verbose_name='Предмет', on_delete=CASCADE)
    teacher = ForeignKey(Teacher, verbose_name='Учитель', on_delete=CASCADE, null=True)

    @property
    def name(self):
        return str(self)

    def __str__(self):
        return '%s в %s' % (
            self.subject.name,
            self.klass.name
        )

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'


class BaseMark(Model):
    mark = SmallIntegerField(verbose_name='Оценка', null=True)
    student = ForeignKey(Student, verbose_name='Ученик', on_delete=CASCADE)
    lesson_info = ForeignKey(Lesson, verbose_name='Урок', on_delete=CASCADE)

    class Meta:
        abstract = True


class Mark(BaseMark):
    PRESENT = 0
    ABSENT = 1

    PRESENCE_CHOICES = (
        (PRESENT, 'Присутствовал'),
        (ABSENT, 'Отсутствовал'),
        # (2, 'Опоздал')
    )

    presence = SmallIntegerField(verbose_name='Присутствие', choices=PRESENCE_CHOICES, default=PRESENT)
    period = ForeignKey(Period, verbose_name='Четверть', on_delete=CASCADE, null=True)
    date = DateField(verbose_name='Дата')

    def __str__(self):
        subject_name = self.lesson_info.subject.name.lower()
        if self.presence == self.ABSENT:
            # TODO изменение по роду "не было"
            return f'{self.student} не было на {subject_name} в {self.date}'

        return f'{self.mark} по {subject_name} за {self.date} - {self.student}'

    def equals(self, other: 'Mark'):
        return self.mark == other.mark \
               and self.presence == other.presence \
               and self.date == other.date \
               and self.student_id == other.student_id \
               and self.lesson_info_id == other.lesson_info_id \
               and self.period_id == other.period_id

    class Meta:
        verbose_name = 'оценка'
        verbose_name_plural = 'оценки'


class SemesterMark(BaseMark):
    period = ForeignKey(Period, verbose_name='Четверть', on_delete=CASCADE, null=True)

    def __str__(self):
        subject_name = self.lesson_info.subject.name.lower()
        return f'Четвертная оценка {self.mark} по {subject_name} - {self.student}'

    def equals(self, other: 'SemesterMark'):
        return self.mark == other.mark \
               and self.student_id == other.student_id \
               and self.lesson_info_id == other.lesson_info_id \
               and self.period_id == other.period_id

    class Meta:
        verbose_name = 'четвертная оценка'
        verbose_name_plural = 'четвертные оценки'


class TerminalMark(BaseMark):
    YEAR = 1
    EXAM = 2
    FINAL = 3
    TYPES = (YEAR, EXAM, FINAL)
    TYPE_CHOICES = (
        (YEAR, 'Годовая'),
        (EXAM, 'Экзамен'),
        (FINAL, 'Итоговая'),
    )

    year = SmallIntegerField(verbose_name='Год')
    type = SmallIntegerField(verbose_name='Тип', choices=TYPE_CHOICES)

    def __str__(self):
        subject_name = self.lesson_info.subject.name.lower()
        return f'{self.type} оценка {self.mark} по {subject_name} - {self.student}'

    def equals(self, other: 'TerminalMark'):
        return self.mark == other.mark \
               and self.student_id == other.student_id \
               and self.lesson_info_id == other.lesson_info_id \
               and self.type == other.type \
               and self.year == other.year

    class Meta:
        verbose_name = 'итоговая оценка'
        verbose_name_plural = 'итоговые оценки'
