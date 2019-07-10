from collections import namedtuple
from typing import List

from django.contrib.auth.models import User
from django.db.models import Avg, Q, CharField
from django.db.models.functions import Length, Substr
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.related_serializer import RelatedSerializerCollector, RelatedSerializer, RelatedTarget
from api.serializers import *
from dnevnik.support import timer
from main.models import Class, Student, Mark, Subject, Teacher, Period, SemesterMark, TerminalMark

__all__ = [
    'UserViewSet',
    'PeriodViewSet',
    'TeacherViewSet',
    'ClassViewSet',
    'SubjectTypeViewSet',
    'SubjectViewSet',
    'StudentViewSet',
]

CLASSES_COLLECTOR = RelatedSerializerCollector(
    model=Class,
    serializer=ClassBasicSerializer
)
SUBJECTS_COLLECTOR = RelatedSerializerCollector(
    model=Subject,
    serializer=SubjectSerializer
)
TEACHERS_COLLECTOR = RelatedSerializerCollector(
    model=Teacher,
    serializer=TeacherBasicSerializer
)
PERIODS_COLLECTOR = RelatedSerializerCollector(
    model=Period,
    serializer=PeriodSerializer
)


class MarksRelatedTarget(RelatedTarget):
    serializer = MarkBasicSerializer
    collect = {
        'subjects': lambda mark: mark.lesson_info.subject_id,
        'teachers': lambda mark: mark.lesson_info.teacher_id,
        'periods': lambda mark: mark.period_id,
    }

    def __init__(self, marks: List[Mark]):
        self.objects = marks


class SemesterMarksRelatedTarget(RelatedTarget):
    serializer = SemesterMarkBasicSerializer
    collect = {
        'subjects': lambda mark: mark.lesson_info.subject_id,
        'teachers': lambda mark: mark.lesson_info.teacher_id,
        'periods': lambda mark: mark.period_id,
    }

    def __init__(self, marks: List[SemesterMark]):
        self.objects = marks


class TerminalMarksRelatedTarget(RelatedTarget):
    serializer = TerminalMarkBasicSerializer
    collect = {
        'subjects': lambda mark: mark.lesson_info.subject_id,
        'teachers': lambda mark: mark.lesson_info.teacher_id
    }

    def __init__(self, marks: List[TerminalMark]):
        self.objects = marks


class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)


class DefaultQuerySet(type):
    def __new__(mcs, name, base, attrs):
        serializer_class = attrs['serializer_class']
        queryset = serializer_class.Meta.model.objects.all().order_by('id')
        attrs['queryset'] = queryset
        return super().__new__(mcs, name, base, attrs)


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PeriodViewSet(ReadOnlyModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = PeriodSerializer


class TeacherViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = TeacherSerializer

    def retrieve(self, request, *args, **kwargs):
        instance: Teacher = self.get_object()
        data = self.get_serializer(instance).data

        subjects = Subject.objects.filter(lesson__teacher=instance).distinct()
        data['subjects'] = SubjectSerializer(subjects, many=True).data
        classes = Class.objects.filter(lesson__teacher=instance).distinct()
        data['classes'] = ClassBasicSerializer(classes, many=True).data
        return Response(data)


class ClassViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Class.objects.all()
    MarkInfo = namedtuple('MarkInfo', ['student', 'subject', 'mark'])

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassBasicSerializer
        if self.action == 'retrieve':
            return ClassSerializer

    def retrieve(self, request, *args, **kwargs):
        instance: Class = self.get_object()
        data = self.get_serializer(instance, context={'request': request}).data

        horizontal_classes = Class.objects.annotate(num=Substr(
            'name', 1,
            Length('name') - 1,
            output_field=CharField())
        ).filter(num=instance.number, year=instance.year)
        data['horizontal_classes'] = ClassBasicSerializer(horizontal_classes, many=True).data

        if instance.final_class_id is None:
            vertical_classes = Class.objects.filter(
                Q(id=instance.id)
                | Q(final_class=instance)
            )
        else:
            vertical_classes = Class.objects.filter(
                Q(id=instance.final_class_id)
                | Q(final_class_id=instance.final_class_id)
            )
        vertical_classes = vertical_classes.order_by('-year').distinct()
        data['vertical_classes'] = ClassBasicSerializer(vertical_classes, many=True).data
        students = instance.get_students().order_by('full_name')
        data['students'] = StudentBasicSerializer(students, many=True).data
        marks = Mark.objects.filter(lesson_info__klass=instance) \
            .values('student', 'lesson_info__subject') \
            .annotate(mark=Avg('mark'))
        for mark in marks:
            mark['subject'] = mark.pop('lesson_info__subject')
            if mark['mark'] is not None:
                mark['mark'] = round(mark['mark'], 2)
        subjects = Subject.objects.filter(id__in=(mark['subject'] for mark in marks))
        data['subjects'] = SubjectSerializer(subjects, many=True).data
        data['marks'] = list(marks)
        return Response(data)


class SubjectTypeViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = SubjectTypeSerializer


class SubjectViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()

    @timer('time', after=True)
    def retrieve(self, request, *args, **kwargs):
        instance: Subject = self.get_object()
        data = SubjectSerializer(instance).data
        teachers = Teacher.objects.filter(lesson__subject=instance).distinct()
        data['teachers'] = TeacherBasicSerializer(teachers, many=True).data
        classes = Class.objects.filter(lesson__subject=instance).distinct()
        data['classes'] = ClassBasicSerializer(classes, many=True).data

        marks = Mark.objects.filter(lesson_info__subject=instance) \
            .values('lesson_info__teacher', 'lesson_info__klass') \
            .annotate(mark=Avg('mark'))
        terminal_marks = TerminalMark.objects.filter(lesson_info__subject=instance) \
            .values('lesson_info__teacher', 'lesson_info__klass') \
            .annotate(mark=Avg('mark'))
        data['marks'] = list(marks)
        data['terminal_marks'] = list(terminal_marks)
        for mark in [*marks, *terminal_marks]:
            mark['class'] = mark.pop('lesson_info__klass')
            mark['teacher'] = mark.pop('lesson_info__teacher')
            if mark['mark'] is not None:
                mark['mark'] = round(mark['mark'], 2)
        assert all(mark['class'] in (klass.id for klass in classes)
                   for mark in [*marks, *terminal_marks])
        assert all(mark['teacher'] in (teacher.id for teacher in teachers)
                   for mark in [*marks, *terminal_marks])
        correct_overstating = """SELECT AVG(diff) overstating, class_id, klass, teacher_id, teacher
            FROM (
                SELECT terminal.mark - AVG(mark.mark) diff,
                    lesson.klass_id                class_id,
                    class.name                     klass,
                    lesson.teacher_id,
                    teacher.full_name              teacher,
                    mark.student_id,
                    student.full_name              student
                FROM main_mark mark
                    INNER JOIN main_lesson lesson ON mark.lesson_info_id = lesson.id
                    INNER JOIN main_class class ON lesson.klass_id = class.id
                    INNER JOIN main_teacher teacher ON lesson.teacher_id = teacher.id
                    INNER JOIN main_student student ON mark.student_id = student.id
                    INNER JOIN main_terminalmark terminal
                        ON mark.lesson_info_id = terminal.lesson_info_id
                            AND mark.student_id = terminal.student_id
                WHERE lesson.subject_id = %s
                GROUP BY class.id, teacher.id, student.id
                )
            GROUP BY class_id, teacher_id"""
        return Response(data)


class StudentViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = StudentBasicSerializer
    queryset = Student.objects.all()
    related_serializer = RelatedSerializer(
        subjects=SUBJECTS_COLLECTOR,
        teachers=TEACHERS_COLLECTOR,
        periods=PERIODS_COLLECTOR
    )

    def retrieve(self, request, *args, **kwargs):
        instance: Student = self.get_object()
        data = StudentSerializer(instance, context={'request': request}).data
        marks = Mark.objects.filter(student=instance) \
            .prefetch_related('lesson_info__subject', 'lesson_info__teacher')
        semester_marks = SemesterMark.objects.filter(student=instance) \
            .prefetch_related('lesson_info__subject', 'lesson_info__teacher')
        terminal_marks = TerminalMark.objects.filter(student=instance) \
            .prefetch_related('lesson_info__subject', 'lesson_info__teacher')

        data['marks'] = self.related_serializer.serialize(
            request,
            marks=MarksRelatedTarget(marks),
            semester_marks=SemesterMarksRelatedTarget(semester_marks),
            terminal_marks=TerminalMarksRelatedTarget(terminal_marks)
        )
        return Response(data)


class LessonViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = LessonSerializer


class MarkViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = MarkSerializer
