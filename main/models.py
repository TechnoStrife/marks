from django.db.models import *


class Quarter(Model):
    num = CharField(max_length=1, verbose_name='Четверть')
    year = SmallIntegerField(verbose_name='Уч. год')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru')

    def __str__(self):
        return '%s четверть %sа' % (self.num, str(self.year))

    class Meta:
        verbose_name = 'четверть'
        verbose_name_plural = 'четверти'


class Teacher(Model):
    full_name = CharField(max_length=127, verbose_name='ФИО')
    birth_date = CharField(max_length=20, verbose_name='День рождения')
    telephone = CharField(max_length=15, verbose_name='Телефон')
    email = EmailField(verbose_name='Email')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru')
    hidden_in_dnevnik = BooleanField(verbose_name='Профиль скрыт в dnevnik.ru')

    @property
    def name(self):
        name, patronymic, surname = self.full_name.split()
        name = f'{surname} {name[0]}. {patronymic[0]}.'
        return name

    @property
    def first_name(self):
        name, patronymic, surname = self.full_name.split()
        return name

    @property
    def patronymic(self):
        name, patronymic, surname = self.full_name.split()
        return patronymic

    @property
    def middle_name(self):
        return self.patronymic

    @property
    def surname(self):
        name, patronymic, surname = self.full_name.split()
        return surname

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'


class Class(Model):
    name = CharField(max_length=3, verbose_name='Класс')
    head_teacher = ForeignKey(Teacher, on_delete=CASCADE, verbose_name='Классный руководитель')
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru')

    def __str__(self):
        return self.name + ' класс'

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
    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'


class Student(Model):
    full_name = CharField(max_length=255, verbose_name='Имя')
    notes = CharField(max_length=4096, verbose_name='Примечания', default='')

    klass = ForeignKey(Class, verbose_name='Класс', on_delete=CASCADE)
    previous_classes = ManyToManyField(Class, db_table='students_previous_classes', verbose_name='Предыдущие классы', null=True)

    entered_quarter = ForeignKey(Quarter, on_delete=PROTECT, verbose_name='Четверть поступления', null=True)
    leaved_quarter = ForeignKey(Quarter, on_delete=PROTECT, verbose_name='Четверть окончания учебы', null=True)

    birth_date = CharField(max_length=20, verbose_name='День рождения', null=True)
    telephone = CharField(max_length=15, verbose_name='Телефон', null=True)
    email = EmailField(verbose_name='Email', null=True)

    dnevnik_id = BigIntegerField(verbose_name='ID в dnevnik.ru')
    hidden_in_dnevnik = BooleanField(verbose_name='Профиль скрыт в dnevnik.ru')

    @property
    def name(self):
        name, patronymic, surname = self.full_name.split()
        name = f'{surname} {name[0]}. {patronymic[0]}.'
        return name

    @property
    def first_name(self):
        name, patronymic, surname = self.full_name.split()
        return name

    @property
    def patronymic(self):
        name, patronymic, surname = self.full_name.split()
        return patronymic

    @property
    def middle_name(self):
        return self.patronymic

    @property
    def surname(self):
        name, patronymic, surname = self.full_name.split()
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
    quarter = ForeignKey(Quarter, verbose_name='Четверть', on_delete=PROTECT)

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


