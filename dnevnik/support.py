import itertools
import re
from typing import List, Any, Union, Iterator, TypeVar, Callable, Sequence
from urllib.parse import parse_qs, urlparse

import requests
from bs4.element import NavigableString, Tag
from requests import Session

from dnevnik import settings
from dnevnik.settings import CHROME_USER_AGENT

__all__ = [
    'skip_navigable_strings',
    'exclude_navigable_strings',
    'login',
    'request_page',
    'flat_2d',
    'transform_class_name',
    'class_grade',
    'unique',
    'first_or_list',
    'get_query_params'
]

T = TypeVar('T')


def login() -> Session:
    session = Session()
    login_data = {
        'login': settings.LOGIN,
        'password': settings.PASSWORD
    }
    r = request_page(session, 'https://login.dnevnik.ru/', data=login_data)

    if re.match(r'https://dnevnik\.ru(:443)?/teacher', r.url):  # after redirect
        return session
    elif 'Ошибка в логине или пароле' in r.text:
        raise ValueError('Ошибка в логине или пароле')
    elif r.status_code != 200:
        raise RuntimeError('Неизвестная ошибка при попытке авторизации')
    else:
        raise RuntimeError('WTF how did it get here?')


def request_page(session: Session, url, params=None, data=None):
    import time
    method = session.get if data is None else session.post
    tries = 0
    while True:
        try:
            r = method(
                url,
                params=params,
                data=data,
                headers={'Referer': url, 'User-Agent': CHROME_USER_AGENT}
            )
        except requests.exceptions.ConnectionError:
            time.sleep(tries)
            tries += 1
            continue
        if r.status_code == 200 and len(r.text) > 0:
            break
        # if r.status_code >= 400:
        #     raise RuntimeError(f'status: {r.status_code}')
        if tries >= 10:
            raise RuntimeError
        time.sleep(tries)
        tries += 1
    return r


def skip_navigable_strings(soup):
    for z in soup:
        if type(z) is NavigableString:
            continue
        yield z


def exclude_navigable_strings(soup: Tag) -> List[Tag]:
    # noinspection PyProtectedMember
    from bs4 import NavigableString
    return [x for x in soup if type(x) is not NavigableString]


def flat_2d(arr: Union[List[List[T]], Iterator[List[T]]]) -> List[T]:
    return list(itertools.chain.from_iterable(arr))


def transform_class_name(name: str) -> str:
    """
    >>> transform_class_name('10 "А"')
    '10А'
    """
    if len(name) == 3:
        return name
    expr = re.match('^(\\d{1,2})\\s?\"([А-Я])\"', name)
    name = expr.group(1) + expr.group(2)
    return name


def class_grade(name: str) -> int:
    """
    >>> class_grade('10А')
    10
    """
    if name[1].isdigit():
        return int(name[:2])
    return int(name[0])


def unique(sequence: Union[List[T], Iterator[T]], key: Callable[[T], Any] = lambda x: x) -> List[T]:
    seen = {}
    result = []
    for item in sequence:
        marker = key(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def first_or_list(arr: Sequence[Any]):
    return arr[0] if len(arr) == 1 else arr


def get_query_params(url: str, *args: str) -> Union[str, List[Union[str, List[str]]]]:
    query = parse_qs(urlparse(url).query)
    return first_or_list([first_or_list(query[param]) for param in args])
