import time
from queue import Queue, Empty
from threading import Thread
from typing import List, Generic, Union, TypeVar

from requests import Session

from dnevnik.pages.base_page import BasePage

T = TypeVar('T')


class TypeQueue(Generic[T]):
    def get(self, block=True, timeout=None) -> T:
        pass

    def put(self, item: T, block=True, timeout=None) -> None:
        pass

    def qsize(self) -> int:
        pass

    def empty(self) -> bool:
        pass

    def full(self) -> bool:
        pass


class PageFetcher(Thread):
    def __init__(self, num: int, fetch_queue: 'FetchQueueProcessor'):
        super().__init__(name='PageFetcher-%d' % num, daemon=True)
        self.fetch_queue: 'FetchQueueProcessor' = fetch_queue
        self.fetching = False

    def run(self):
        while self.fetch_queue.alive:
            try:
                page = self.fetch_queue.queue.get(timeout=0.1)
            except Empty:
                continue

            self.fetching = True
            page.fetch(self.fetch_queue.session)
            page.parse()
            self.fetching = False


class FetchQueueProcessor:
    def __init__(self, session: Session, max_requests: int = 20):
        self.session: Session = session
        self.max_requests: int = max_requests
        self.queue: TypeQueue[BasePage] = Queue()
        self.alive: bool = False
        self.threads: List[PageFetcher] = []

    def put(self, pages: Union[BasePage, List[BasePage]]) -> None:
        if not self.alive:
            raise RuntimeError('FetchQueueProcessor is not activated. Call .start()')
        if type(pages) is not list:
            pages = [pages]
        for page in pages:
            self.queue.put(page)
            time.sleep(0.05)

    def process(self, pages: Union[BasePage, List[BasePage]]) -> None:
        self.put(pages)
        if type(pages) is not list:
            pages = [pages]
        while any(not page.parsed for page in pages):
            queue_pages_count = sum(not page.parsed for page in pages)
            print(f'\r{queue_pages_count}/{len(pages)}, {self.fetchers_busy()}/{self.max_requests}', end='')
            time.sleep(0.05)
        print()

    def fetchers_busy(self) -> int:
        return sum(thread.fetching for thread in self.threads)

    def start(self):
        self.alive = True
        for z in range(self.max_requests):
            thread = PageFetcher(z + 1, self)
            thread.start()
            self.threads.append(thread)

    def stop(self):
        self.alive = False
        while any(thread.is_alive() for thread in self.threads):
            time.sleep(0.05)
        self.threads = []
