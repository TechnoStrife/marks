from bs4 import BeautifulSoup

from dnevnik.parsers.support import request_page


class BasePage:
    URL = None
    response = None
    post = False
    soup = None
    fetched = False

    def __init__(self, params=None, data=None):
        self.params = params
        self.data = data

    def fetch(self, session):
        self.response = request_page(session, self.URL, self.params, self.data)
        self.soup = BeautifulSoup(self.response.text, "lxml")
        self.fetched = True
        return self

    def parse(self):
        return self
