import json

from django.db.models import Count
from django.shortcuts import render

from api.serializers import ClassBasicSerializer, TeacherBasicSerializer, SubjectSerializer
from main.models import Class, Teacher, Subject
from main.models_extensions import Concat


def test(request, url=None):
    teachers = Teacher.objects.all() \
        .annotate(
        lesson_count=Count('lesson'),
        lesson_types=Concat('lesson__subject__type', True)
    ).filter(lesson_count__gt=0)
    sidenav = {
        'classes': ClassBasicSerializer(Class.objects.all(), many=True).data,
        'subjects': SubjectSerializer(Subject.objects.all(), many=True).data,
        'teachers': TeacherBasicSerializer(teachers, many=True).data,
    }
    sidenav = json.dumps(sidenav)
    return render(request, 'test.html', locals())
