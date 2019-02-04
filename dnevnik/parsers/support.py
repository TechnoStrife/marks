import re
import requests
from dnevnik import dnevnik_settings

__all__ = [
    'STUDENT', 'TEACHER', 'USER_TYPES',
    'skip_navigable_strings',
    'exclude_navigable_strings',
    'get_or_create',
    'update_or_create',
]

STUDENT = 'student'
TEACHER = 'teacher'
USER_TYPES = [STUDENT, TEACHER]


def skip_navigable_strings(soup):
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    for z in soup:
        if type(z) is NavigableString:
            continue
        yield z


def exclude_navigable_strings(soup):
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    return [x for x in soup if type(x) is not NavigableString]


def get_or_create(model, main_attr, **kwargs):
    obj = model.objects.filter(**{main_attr: kwargs[main_attr]})
    if obj.exists():
        return obj.first()
    else:
        return model.objects.create(**kwargs)


def update_or_create(model, main_attr, **kwargs):
    obj = model.objects.filter(**{main_attr: kwargs[main_attr]})
    if obj.exists():
        obj = obj.first()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj
    else:
        return model.objects.create(**kwargs)
