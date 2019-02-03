from django.contrib import admin
from main.models import *
from django.utils.translation import gettext_lazy as _


class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'birthday',
        'tel',
        'email',
        'not_found_in_dnevnik'
    ]

    list_filter = ['not_found_in_dnevnik']
    search_fields = ['full_name']

    class Meta:
        model = Teacher


class ClassIsFinalListFilter(admin.SimpleListFilter):
    title = _('Конечный класс?')
    parameter_name = 'is_final'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Да')),
            ('false', _('Нет'))
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        has_final_class = self.value() != 'true'
        return queryset.filter(final_class__isnull=has_final_class)


class ClassHasHeadTeacherListFilter(admin.SimpleListFilter):
    title = _('Указан классный руководитель?')
    parameter_name = 'has_head_teacher'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Да')),
            ('false', _('Нет'))
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        has_final_class = self.value() != 'true'
        return queryset.filter(head_teacher__isnull=has_final_class)


class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_final_class', 'info', 'head_teacher', 'year']
    list_filter = [
        'year',
        ClassIsFinalListFilter,
        ClassHasHeadTeacherListFilter
    ]
    search_fields = ['name', 'head_teacher']

    def display_final_class(self, obj):
        if obj.final_class:
            return obj.final_class.name
        return None
    display_final_class.admin_order_field = 'final_class'
    display_final_class.short_description = 'Конечный класс'

    class Meta:
        model = Class


admin.site.register(Class, ClassAdmin)
admin.site.register(Teacher, TeacherAdmin)
