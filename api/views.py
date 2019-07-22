from collections import namedtuple
from typing import List, Union

from django.contrib.auth.models import User
from django.db.models import Avg, Q, CharField, FloatField, ExpressionWrapper as Expr, F
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
from main.summary.models import AvgMark

__all__ = [
    'UserViewSet',
    'PeriodViewSet',
    'TeacherViewSet',
    'ClassViewSet',
    'SubjectTypeViewSet',
    'SubjectViewSet',
    'StudentViewSet',
]


def round_none(number: Union[None, float], n_digits: int = None):
    if number is None:
        return number
    return round(number, n_digits)


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
        marks = AvgMark.objects.filter(lesson__klass=instance).prefetch_related('lesson')
        marks = [
            {
                'mark': round(mark.mark, 2),
                'terminal_mark': mark.terminal_mark,
                'student': mark.student_id,
                'subject': mark.lesson.subject_id,
                'teacher': mark.lesson.teacher_id
            }
            for mark in marks
        ]
        subjects = Subject.objects.filter(id__in=(mark['subject'] for mark in marks))
        data['subjects'] = SubjectSerializer(subjects, many=True).data
        teachers = Teacher.objects.filter(id__in=(mark['teacher'] for mark in marks))
        data['teachers'] = TeacherBasicSerializer(teachers, many=True).data
        data['marks'] = marks
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

        marks = AvgMark.objects.filter(lesson__subject=instance)
        marks = marks.values('lesson__teacher', 'lesson__klass').annotate(
            diff=Avg(Expr(F('terminal_mark') - F('mark'), output_field=FloatField())),
            mark=Avg('mark'),
            terminal_mark=Avg('terminal_mark'),
        ).filter(mark__isnull=False, terminal_mark__isnull=False)
        marks = list(marks)
        for mark in marks:
            mark['class'] = mark.pop('lesson__klass')
            mark['teacher'] = mark.pop('lesson__teacher')
        data['marks'] = marks
        assert all(mark['class'] in (klass.id for klass in classes) for mark in marks)
        assert all(mark['teacher'] in (teacher.id for teacher in teachers) for mark in marks)
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
