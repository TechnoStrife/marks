from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import *

__all__ = [
    'UserViewSet',
    'PeriodViewSet',
    'TeacherViewSet',
    'ClassViewSet',
    'SubjectTypeViewSet',
    'SubjectViewSet',
    'StudentViewSet',
]


class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)


class DefaultQuerySet(type):
    def __new__(mcs, name, base, attrs):
        serializer_class = attrs['serializer_class']
        queryset = serializer_class.Meta.model.objects.all().order_by('id')
        attrs['queryset'] = queryset
        return super().__new__(mcs, name, base, attrs)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PeriodViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = PeriodSerializer


class TeacherViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = TeacherSerializer


class ClassViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = ClassSerializer


class SubjectTypeViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = SubjectTypeSerializer


class SubjectViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = SubjectSerializer


class StudentViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = StudentSerializer


class LessonViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = LessonSerializer


class MarkViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = MarkSerializer
