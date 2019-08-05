from typing import Type

from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.serializers import *

from main.models import *

__all__ = [
    'ReplaceReservedKeywordAttributes',
    'OptionalFieldsMixin',
    'get_fields',
    'UserSerializer',
    'PeriodSerializer',
    'StudentBasicSerializer',
    'StudentSerializer',
    'TeacherBasicSerializer',
    'TeacherSerializer',
    'ClassBasicSerializer',
    'ClassSerializer',
    'SubjectTypeSerializer',
    'SubjectSerializer',
    'LessonBasicSerializer',
    'LessonSerializer',
    'MarkBasicSerializer',
    'MarkSerializer',
    'SemesterMarkBasicSerializer',
    'SemesterMarkSerializer',
    'TerminalMarkBasicSerializer',
    'TerminalMarkSerializer',
]


class ReplaceReservedKeywordAttributes(SerializerMetaclass):
    def __new__(mcs, name, bases, attrs: dict):
        attrs = {mcs.rename(name): value for name, value in attrs.items()}

        if 'Meta' in attrs:
            meta = attrs['Meta']
            meta.fields = [mcs.rename(name) for name in meta.fields]

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def rename(name):
        if len(name) > 1 and name[-1] == '_' and name[-2] != '_':
            return name[:-1]
        else:
            return name


class OptionalFieldsMixin(ModelSerializer):
    def to_representation(self, instance):
        res = super().to_representation(instance)
        for field in self.Meta.optional_fields:
            if hasattr(instance, field):
                res[field] = getattr(instance, field)
        return res


def get_fields(model: Type[Model], exclude=None):
    if exclude is None:
        exclude = []
    return [field.name for field in model._meta.fields if field.name not in exclude]


class UserSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = User
        fields = (
            'url',
            'username',
            'email',
            'first_name',
            'last_name',
        )


class PeriodSerializer(ModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = Period
        fields = get_fields(Period)
        read_only_fields = get_fields(Period)


class TeacherBasicSerializer(OptionalFieldsMixin, ModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # head_in_classes = PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True
    # )

    class Meta:
        model = Teacher
        fields = get_fields(Teacher)
        read_only_fields = get_fields(Teacher, exclude=['job', 'tel', 'email'])
        optional_fields = ['lesson_types']


class ClassBasicSerializer(ModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    final_class = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Class
        fields = get_fields(Class)
        read_only_fields = get_fields(Class, exclude=['info'])


class SubjectTypeSerializer(ModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = SubjectType
        fields = get_fields(SubjectType)


class SubjectSerializer(ModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = Subject
        fields = get_fields(Subject)
        read_only_fields = get_fields(Subject, exclude=['type'])


class StudentBasicSerializer(ModelSerializer,
                             metaclass=ReplaceReservedKeywordAttributes):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    previous_classes = PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    class_ = PrimaryKeyRelatedField(
        source='klass',
        read_only=True
    )

    class Meta:
        model = Student
        fields = get_fields(Student, exclude=['klass']) \
                 + ['class_', 'previous_classes']
        read_only_fields = get_fields(Student, exclude=['info', 'tel', 'email'])


class LessonBasicSerializer(ModelSerializer,
                            metaclass=ReplaceReservedKeywordAttributes):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    class_ = PrimaryKeyRelatedField(read_only=True, source='klass')
    teacher = PrimaryKeyRelatedField(read_only=True)
    subject = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = get_fields(Lesson, exclude=['klass']) + ['class_']
        read_only_fields = get_fields(Lesson)


class MarkBasicSerializer(HyperlinkedModelSerializer):
    student = PrimaryKeyRelatedField(read_only=True)
    lesson_info = LessonBasicSerializer(read_only=True)
    period = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Mark
        fields = get_fields(Mark)
        read_only_fields = get_fields(Mark)


class SemesterMarkBasicSerializer(ModelSerializer):
    student = PrimaryKeyRelatedField(read_only=True)
    lesson_info = LessonBasicSerializer(read_only=True)
    period = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SemesterMark
        fields = get_fields(SemesterMark)
        read_only_fields = get_fields(SemesterMark)


class TerminalMarkBasicSerializer(ModelSerializer):
    student = PrimaryKeyRelatedField(read_only=True)
    lesson_info = LessonBasicSerializer(read_only=True)

    class Meta:
        model = TerminalMark
        fields = get_fields(TerminalMark)
        read_only_fields = get_fields(TerminalMark)


class TeacherSerializer(TeacherBasicSerializer):
    head_in_classes = ClassBasicSerializer(many=True)

    class Meta(TeacherBasicSerializer.Meta):
        fields = TeacherBasicSerializer.Meta.fields \
                 + ['head_in_classes']


class ClassSerializer(ClassBasicSerializer):
    final_class = ClassBasicSerializer()
    periods = PeriodSerializer(many=True)
    # students = StudentBasicSerializer(many=True)
    # previous_students = StudentBasicSerializer(many=True)
    head_teacher = TeacherBasicSerializer()

    class Meta(ClassBasicSerializer.Meta):
        fields = ClassBasicSerializer.Meta.fields \
                 + ['students', 'periods']


class StudentSerializer(StudentBasicSerializer):
    class_ = ClassBasicSerializer(source='klass')
    previous_classes = ClassBasicSerializer(many=True)


class LessonSerializer(StudentBasicSerializer,
                       metaclass=ReplaceReservedKeywordAttributes):
    class_ = ClassSerializer(source='klass')
    subject = SubjectSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = Lesson
        fields = get_fields(Lesson, exclude=['klass']) + ['class_']


class MarkSerializer(MarkBasicSerializer):
    student = StudentSerializer()
    lesson_info = LessonSerializer()
    period = PeriodSerializer()


class SemesterMarkSerializer(SemesterMarkBasicSerializer):
    student = StudentSerializer()
    lesson_info = LessonSerializer()
    period = PeriodSerializer()


class TerminalMarkSerializer(TerminalMarkBasicSerializer):
    student = StudentSerializer()
    lesson_info = LessonSerializer()
