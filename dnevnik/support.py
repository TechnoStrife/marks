import re
import requests
from dnevnik import dnevnik_settings

__all__ = [
    'CHROME_USER_AGENT',
    'transform_class_name',
    'class_grade',
    'skip_navigable_strings',
    'exclude_navigable_strings',
    'request_page',
    'STUDENT', 'TEACHER', 'USER_TYPES',
    'get_pages_count',
    'get_or_create',
    'update_or_create',
]

CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/69.0.3497.100 Safari/537.36 '

STUDENT = 'student'
TEACHER = 'teacher'
USER_TYPES = [STUDENT, TEACHER]


def transform_class_name(name):
    if len(name) == 3:
        return name
    expr = re.match('^(\\d{1,2})\\s?\"([А-Я])\"', name)
    if not expr:
        return None
    name = expr.group(1) + expr.group(2)
    return name


def class_grade(name: str):
    if name[1].isdigit():
        return int(name[:2])
    return int(name[0])


def skip_navigable_strings(soup):
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    for z in soup:
        if type(z) is NavigableString:
            continue
        yield z


def exclude_navigable_strings(soup):
    from bs4 import NavigableString
    return [x for x in soup if type(x) is not NavigableString]


def request_page(session: requests.Session, page_name, params=None, data=None):
    import time
    method = session.get if data is None else session.post
    url = dnevnik_settings.URLS[page_name]
    tries = 0
    while True:
        r = method(
            url,
            params=params,
            data=data,
            headers={'Referer': url, 'User-Agent': CHROME_USER_AGENT}
        )
        if r.status_code == 200 and len(r.text) > 0:
            break
        if tries >= 10:
            raise RuntimeError
        time.sleep(tries)
        tries += 1
    return r


def get_pages_count(soup):
    pager = soup.find(class_='pager')
    last_page = exclude_navigable_strings(pager.ul.children)[-1]
    last_page = last_page.a.text if last_page.a else last_page.b.text
    return int(last_page)


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
