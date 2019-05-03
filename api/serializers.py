from typing import Type

from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.serializers import *

from main.models import *

__all__ = [
    'UserSerializer',
    'PeriodSerializer',
    'StudentSerializer',
    'TeacherSerializer',
    'ClassSerializer',
    'SubjectTypeSerializer',
    'SubjectSerializer',
    'LessonSerializer',
    'MarkSerializer',
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


# class IncludeBaseFields(type):
#     def __new__(mcs, name, bases, attrs: dict):
#         attrs['fields'] = bases[0].fields + attrs['fields']
#         return super().__new__(mcs, name, bases, attrs)


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


class PeriodSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = Period
        fields = get_fields(Period)


class TeacherBasicSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    head_in_classes = PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Teacher
        fields = get_fields(Teacher) + ['url', 'head_in_classes']


class ClassBasicSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    periods = PeriodSerializer(many=True)
    final_class = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Class
        fields = get_fields(Class) + ['url', 'periods']


class SubjectTypeSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = SubjectType
        fields = get_fields(SubjectType)


class SubjectSerializer(HyperlinkedModelSerializer):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    class Meta:
        model = Subject
        fields = get_fields(Subject) + ['url']


class StudentBasicSerializer(HyperlinkedModelSerializer,
                             metaclass=ReplaceReservedKeywordAttributes):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    previous_classes = HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='class-detail'
    )
    class_ = PrimaryKeyRelatedField(
        source='klass',
        read_only=True
    )

    class Meta:
        model = Student
        fields = get_fields(Student, exclude=['klass']) \
                 + ['url', 'class_', 'previous_classes']


class TeacherSerializer(TeacherBasicSerializer):
    head_in_classes = ClassBasicSerializer(many=True)


class ClassSerializer(ClassBasicSerializer):
    final_class = ClassBasicSerializer()
    students = StudentBasicSerializer(many=True)

    class Meta(ClassBasicSerializer.Meta):
        fields = ClassBasicSerializer.Meta.fields + ['students']


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


class MarkSerializer(HyperlinkedModelSerializer):
    student = StudentSerializer()
    lesson_info = LessonSerializer()
    period = PeriodSerializer()

    class Meta:
        model = Mark
        fields = get_fields(Mark)
