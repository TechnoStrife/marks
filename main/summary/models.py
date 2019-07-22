from typing import Callable, Dict, List

from django.db import connections, connection
from django.db.models import *

from dnevnik.support import timer
from main.models import Lesson, Student, Mark


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


def synchronize():
    AvgMark.synchronize()
