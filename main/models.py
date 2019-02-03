from django.db.models import *
from dnevnik import dnevnik_settings


__all__ = [
    'Quarter',
    'Student',
    'Teacher',
    'Class',
    'Subject',
    'Lesson',
    'Mark'
]


class Quarter(Model):
    num = CharField(max_length=1, verbose_name='Четверть')
    year = SmallIntegerField(verbose_name='Уч. год')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)

    def __str__(self):
        return '%s четверть %s года' % (self.num, str(self.year))

    class Meta:
        verbose_name = 'четверть'
        verbose_name_plural = 'четверти'


class Teacher(Model):
    full_name = CharField(max_length=127, verbose_name='ФИО')
    birthday = DateField(verbose_name='День рождения', null=True)
    tel = CharField(max_length=15, verbose_name='Телефон', null=True)
    email = EmailField(verbose_name='Email', null=True)
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True, null=True)
    not_found_in_dnevnik = BooleanField(verbose_name='Профиль скрыт в dnevnik.ru', default=False)

    @property
    def name(self):
        surname, name, patronymic = self.full_name.split()
        name = f'{surname} {name[0]}. {patronymic[0]}.'
        return name

    @name.setter
    def name(self, value):
        self.full_name = value

    @property
    def first_name(self):
        surname, name, patronymic = self.full_name.split()
        return name

    @property
    def patronymic(self):
        surname, name, patronymic = self.full_name.split()
        return patronymic

    @property
    def middle_name(self):
        return self.patronymic

    @property
    def surname(self):
        surname, name, patronymic = self.full_name.split()
        return surname

    def dnevnik_link(self):
        if self.dnevnik_id:
            return 'https://dnevnik.ru/user/user.aspx?user=' + str(self.dnevnik_id)
        else:
            return None

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'


class Class(Model):
    name = CharField(max_length=3, verbose_name='Класс')
    info = CharField(max_length=4096, verbose_name='Примечания', null=True)
    head_teacher = ForeignKey(Teacher, on_delete=CASCADE, verbose_name='Классный руководитель', null=True)
    year = SmallIntegerField(verbose_name='Уч. год')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)
    # is_final = BooleanField(verbose_name='dnevnik.ru мразь', default=False)
    final_class = ForeignKey('self', verbose_name='Конечный класс', on_delete=SET_NULL, null=True)

    def __str__(self):
        return self.name + ' класс'

    @property
    def number(self):
        return self.name[:-1]

    @property
    def letter(self):
        return self.name[-1]

    def __repr__(self):
        return '<Class %s>' % self.name

    class Meta:
        verbose_name = 'класс'
        verbose_name_plural = 'классы'


class Subject(Model):
    PHILOLOGICAL = 'fil'
    PHYSICS = 'phy'
    INF_MATH = 'mth'
    SOCIAL = 'soc'
    ELECTIVES = 'ele'
    OTHERS = 'oth'

    TYPES = (
        (PHILOLOGICAL, 'Филологические'),
        (PHYSICS, 'Естественно-научные'),
        (INF_MATH, 'Информационно-математические'),
        (SOCIAL, 'Социальные'),
        (ELECTIVES, 'Элективные'),
        (OTHERS, 'Другие')
    )

    name = CharField(max_length=127, verbose_name='Имя')
    type = CharField(max_length=5, choices=TYPES)
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'


class Student(Model):
    full_name = CharField(max_length=255, verbose_name='Имя')
    info = CharField(max_length=4096, verbose_name='Примечания', default='')

    klass = ForeignKey(Class, verbose_name='Класс', on_delete=CASCADE)
    previous_classes = ManyToManyField(Class, db_table='students_previous_classes', verbose_name='Предыдущие классы', related_name='+')

    first_mark = ForeignKey('Mark', on_delete=PROTECT, verbose_name='Первая оценка', null=True, related_name='+')
    last_mark = ForeignKey('Mark', on_delete=PROTECT, verbose_name='Последняя оценка', null=True, related_name='+')

    birthday = CharField(max_length=20, verbose_name='День рождения', null=True)
    tel = CharField(max_length=15, verbose_name='Телефон', null=True)
    email = EmailField(verbose_name='Email', null=True)
    parents = CharField(max_length=1024, verbose_name='Родители', default='')

    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True, null=True)
    not_found_in_dnevnik = BooleanField(verbose_name='Профиль не найден в dnevnik.ru', default=False)

    @property
    def name(self):
        surname, name, patronymic = self.full_name.split()
        name = f'{surname} {name[0]}. {patronymic[0]}.'
        return name

    @name.setter
    def name(self, value):
        self.full_name = value

    @property
    def first_name(self):
        surname, name, patronymic = self.full_name.split()
        return name

    @property
    def patronymic(self):
        surname, name, patronymic = self.full_name.split()
        return patronymic

    @property
    def middle_name(self):
        return self.patronymic

    @property
    def surname(self):
        surname, name, patronymic = self.full_name.split()
        return surname

    def __str__(self):
        return '%s (%s)' % (self.name, self.klass.name)

    class Meta:
        verbose_name = 'ученик'
        verbose_name_plural = 'ученики'


class Lesson(Model):
    klass = ForeignKey(Class, verbose_name='Класс', on_delete=CASCADE)
    subject = ForeignKey(Subject, verbose_name='Предмет', on_delete=CASCADE)
    teacher = ForeignKey(Teacher, verbose_name='Учитель', on_delete=CASCADE)

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


class Mark(Model):
    PRESENSE_CHOICES = (
        (0, 'Присутствовал'),
        (1, 'Отсутствовал'),
        (2, 'Опоздал')
    )

    mark = IntegerField(verbose_name='Оценка')
    presence = SmallIntegerField(verbose_name='Присутствие', choices=PRESENSE_CHOICES)
    student = ForeignKey(Student, verbose_name='Ученик', on_delete=CASCADE)
    lesson_info = ForeignKey(Lesson, verbose_name='Урок', on_delete=CASCADE)
    quarter = ForeignKey(Quarter, verbose_name='Четверть', on_delete=CASCADE)
    date = DateField(null=True, verbose_name='Дата')
    is_semester = BooleanField(default=False, verbose_name='Четвертная')
    is_terminal = BooleanField(default=False, verbose_name='Годовая')

    def __str__(self):
        # if self.mark == self.ABSENT:
            # TODO изменение по роду "не было"
            # return '%s не было на %s в %s' % (self.student, self.lesson_info.subject.name.lower(), self.date)

        # TODO склонение предметов
        if self.is_semester:
            return 'Четвертная оценка %i по %s - %s' % (self.mark, self.lesson_info.subject.name.lower(), self.student)
        elif self.is_terminal:
            return 'Итоговая оценка %i по %s - %s' % (self.mark, self.lesson_info.subject.name.lower(), self.student)

        return '%i по %s за %s - %s' % (self.mark, self.lesson_info.subject.name.lower(), self.date, self.student)

    class Meta:
        verbose_name = 'оценка'
        verbose_name_plural = 'оценки'

