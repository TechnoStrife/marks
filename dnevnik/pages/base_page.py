from enum import Enum, auto
from typing import Union, Dict, Any

from bs4 import BeautifulSoup
from requests import Session, Response

from dnevnik.support import request_page


class ResponseType(Enum):
    HTML = auto()
    JSON = auto()


class BasePage:
    URL: str = None
    response: Response = None
    post: bool = False
    soup: BeautifulSoup = None
    json: Dict[str, Any]
    fetched: bool = False
    parsed: bool = False
    response_type: ResponseType = ResponseType.HTML

    def __init__(self, params: Union[None, dict] = None, data: Union[None, dict] = None):
        if params is not None:
            for k, v in list(params.items()):
                if v is None:
                    del params[k]
        if data is not None:
            for k, v in list(data.items()):
                if v is None:
                    del data[k]

        self.params = params
        self.data = data

    def fetch(self, session: Session) -> 'BasePage':
        self.response = request_page(session, self.URL, self.params, self.data)
        if self.response_type is ResponseType.HTML:
            self.soup = BeautifulSoup(self.response.text, "lxml")
        elif self.response_type is ResponseType.JSON:
            self.json = self.response.json()
        self.fetched = True
        return self

    def parse(self) -> 'BasePage':
        return self

    def free(self):
        self.response = None
        self.soup = None
        self.json = None
