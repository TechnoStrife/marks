from api.summary.serializers import *
from api.views import ModelViewSet, DefaultQuerySet


class ClassAvgMarkViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = ClassAvgMarkBasicSerializer


class SubjectAvgMarkViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = SubjectAvgMarkBasicSerializer


class TeacherAvgMarkViewSet(ModelViewSet, metaclass=DefaultQuerySet):
    serializer_class = TeacherAvgMarkBasicSerializer
