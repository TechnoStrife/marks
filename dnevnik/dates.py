import datetime
import re
from typing import Any, Callable

from dnevnik.settings import MONTHS


class DateFormat:
    def __init__(self, regex: str, **modifiers: Callable[[str], Any]):
        self.regex = re.compile(regex)
        self.modifiers = modifiers

    def match(self, s):
        s = self.regex.match(s)
        if not s:
            return False
        res = {}
        for group_name, match in s.groupdict().items():
            if group_name in self.modifiers:
                res[group_name] = self.modifiers[group_name](match)
            else:
                res[group_name] = match
        return res


date_formats = [
    DateFormat(
        r'(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})',
        day=int, month=int, year=int
    ),
    DateFormat(
        r'(?P<day>\d{1,2})\s(?P<month>[а-я]+)\s(?P<year>\d{4})(?: г\.)?',
        day=int, month=lambda x: MONTHS.index(x.lower()) + 1, year=int
    ),
    DateFormat(
        r'(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{2})',
        day=int, month=int, year=int
    )
]


def transform_date(date):
    for date_format in date_formats:
        match = date_format.match(date)
        if match:
            return datetime.date(**match)
    raise ValueError(f'date matches nothing ({date})')
