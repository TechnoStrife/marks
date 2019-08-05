from typing import Callable, Dict, List

from django.db import connections, connection
from django.db.models import *

from dnevnik.support import timer
from main.models import Lesson, Student, Mark, Class, Subject, Teacher


# from main.summary.readonly_model import ReadOnlyModel, ReadOnlyManager


class DependentManager(Manager):  # ReadOnlyManager
    name = 'DependentManager'

    def __init__(self, sync_getter: Callable[[], List[Dict]] = None, query: str = None):
        super().__init__()
        if sync_getter is None and query is None:
            raise ValueError('provide either sync_getter or query to DependentManager')
        self.sync_getter = sync_getter
        self.query = query

    def synchronize(self):
        if self.sync_getter is not None:
            QuerySet.delete(self.all())
            table = self.sync_getter()
            QuerySet.bulk_create(self.all(), [self.model(**data) for data in table])
            return len(table)
        elif self.query is not None:
            with connections[self.db].cursor() as cursor:
                cursor.execute(self.query)
                res = cursor.fetchone()
                return res


class AvgMark(Model):
    mark = FloatField(null=True)
    terminal_mark = SmallIntegerField(null=True)
    lesson = ForeignKey(Lesson, on_delete=CASCADE)
    student = ForeignKey(Student, on_delete=CASCADE)

    # def __init__(self, mark, lesson_info, student):
    #     super().__init__(mark=mark, student_id=student, lesson_id=lesson_info)

    @classmethod
    @timer('AvgMark.synchronize')
    def synchronize(cls):
        cls.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO summary_avgmark (mark, lesson_id, student_id)
                SELECT AVG(mark), lesson_info_id, student_id FROM main_mark
                GROUP BY lesson_info_id, student_id""")
            cursor.execute("""UPDATE summary_avgmark SET terminal_mark = (
                    SELECT mark FROM main_terminalmark terminal
                    WHERE terminal.student_id = summary_avgmark.student_id
                        AND terminal.lesson_info_id = summary_avgmark.lesson_id
                )""")


class BaseSummaryAvgMark(Model):
    mark = FloatField(null=True)
    terminal_mark = FloatField(null=True)
    diff = FloatField(null=True)
    year = SmallIntegerField()
    aggregate_field = None

    @classmethod
    def synchronize(cls):
        if type(cls.aggregate_field) is not str:
            raise TypeError(f'{cls.__name__}.aggregate_field must be type str')
        field = cls.aggregate_field
        name = cls.__name__.lower()
        with timer(f'{cls.__name__}.synchronize'):
            cls.objects.all().delete()
            with connection.cursor() as cursor:
                cursor.execute(f"""INSERT INTO summary_{name} (mark, terminal_mark, diff, year, {field}_id)
                    SELECT AVG(mark), AVG(terminal_mark), 
                        AVG(terminal_mark - mark), class.year, {field}_id
                    FROM summary_avgmark
                    INNER JOIN main_lesson lesson on summary_avgmark.lesson_id = lesson.id
                    INNER JOIN main_class class on lesson.klass_id = class.id
                    GROUP BY lesson.{field}_id, class.year
                    HAVING AVG(mark) IS NOT NULL OR AVG(terminal_mark) IS NOT NULL""")

    class Meta:
        abstract = True


class ClassAvgMark(BaseSummaryAvgMark):
    klass = ForeignKey(Class, on_delete=CASCADE)
    aggregate_field = 'klass'


class SubjectAvgMark(BaseSummaryAvgMark):
    subject = ForeignKey(Subject, on_delete=CASCADE)
    aggregate_field = 'subject'


class TeacherAvgMark(BaseSummaryAvgMark):
    teacher = ForeignKey(Teacher, on_delete=CASCADE)
    aggregate_field = 'teacher'


def synchronize():
    AvgMark.synchronize()
    ClassAvgMark.synchronize()
    SubjectAvgMark.synchronize()
    TeacherAvgMark.synchronize()
