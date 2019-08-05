from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from api.serializers import get_fields, ReplaceReservedKeywordAttributes, ClassBasicSerializer, SubjectSerializer, \
    TeacherBasicSerializer
from main.summary.models import AvgMark, ClassAvgMark, SubjectAvgMark, TeacherAvgMark


class AvgMarkBasicSerializer(ModelSerializer, metaclass=ReplaceReservedKeywordAttributes):
    student = PrimaryKeyRelatedField(read_only=True)
    class_ = PrimaryKeyRelatedField(read_only=True, source='lesson.klass_id')
    subject = PrimaryKeyRelatedField(read_only=True, source='lesson.subject_id')
    teacher = PrimaryKeyRelatedField(read_only=True, source='lesson.teacher_id')

    class Meta:
        model = AvgMark
        fields = ['mark', 'terminal_mark', 'student', 'class_', 'subject', 'teacher']
        read_only_fields = fields


class ClassAvgMarkBasicSerializer(ModelSerializer, metaclass=ReplaceReservedKeywordAttributes):
    class_ = ClassBasicSerializer(read_only=True, source='klass')

    class Meta:
        model = ClassAvgMark
        fields = get_fields(ClassAvgMark, exclude=['klass']) + ['class_']
        read_only_fields = fields


class SubjectAvgMarkBasicSerializer(ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectAvgMark
        fields = get_fields(SubjectAvgMark)
        read_only_fields = fields


class TeacherAvgMarkBasicSerializer(ModelSerializer):
    teacher = TeacherBasicSerializer(read_only=True)

    class Meta:
        model = TeacherAvgMark
        fields = get_fields(TeacherAvgMark)
        read_only_fields = fields
