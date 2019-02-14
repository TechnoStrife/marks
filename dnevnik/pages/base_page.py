from typing import Union

from bs4 import BeautifulSoup
from requests import Session, Response

from dnevnik.parsers.support import request_page


class BasePage:
    URL: str = None
    response: Response = None
    post: bool = False
    soup: BeautifulSoup = None
    fetched: bool = False
    parsed: bool = False

    def __init__(self, params: Union[None, dict] = None, data: Union[None, dict] = None):
        self.params = params
        self.data = data

    def fetch(self, session: Session) -> 'BasePage':
        self.response = request_page(session, self.URL, self.params, self.data)
        self.soup = BeautifulSoup(self.response.text, "lxml")
        self.fetched = True
        return self

    def parse(self) -> 'BasePage':
        return self
