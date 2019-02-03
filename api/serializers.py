from django.contrib.auth.models import User
from rest_framework import serializers
from main.models import *


__all__ = [
    'UserSerializer',
    # 'QuarterSerializer',
    'StudentSerializer',
    'TeacherSerializer',
    'ClassSerializer',
    # 'SubjectSerializer',
    # 'LessonSerializer',
    # 'MarkSerializer',
]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')


# class QuarterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Quarter
#         fields = ('id', 'year', 'dnevnik_id')
#
#
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'info',
            'klass',
            'previous_classes',
            'first_mark',
            'last_mark',
            'birthday',
            'tel',
            'email',
            'dnevnik_id',
            'not_found_in_dnevnik'
        )


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = (
            'id',
            'full_name',
            'birthday',
            'tel',
            'email',
            'dnevnik_id',
            'not_found_in_dnevnik',
        )


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = (
            'id',
            'name',
            'info',
            'head_teacher',
            'year',
            'dnevnik_id',
            'final_class',
        )

# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = ('id', 'year', 'dnevnik_id')
#
#
# class LessonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Lesson
#         fields = ('id', 'year', 'dnevnik_id')
#
#
# class MarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Mark
#         fields = ('id', 'year', 'dnevnik_id')
