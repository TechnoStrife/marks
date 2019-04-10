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
            page.free()
            self.fetching = False


class FetchQueueProcessor:
    def __init__(self, session: Session, max_requests: int = 10):
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
        for index, page in enumerate(pages):
            self.queue.put(page)
            percent = round((index + 1) / len(pages) * 100)
            self._print_status(pages, f'{percent}%')
            time.sleep(0.05)

    def _print_status(self, pages, *args):
        queue_pages_count = sum(not page.parsed for page in pages)
        pages_stat = f'{queue_pages_count}/{len(pages)}'
        workers_stat = f'{self.fetchers_busy()}/{self.max_requests}'
        add_info = ' '.join(str(x) for x in args)
        print(f'\r{pages_stat}, {workers_stat} {add_info}', end='')

    def process(self, pages: Union[BasePage, List[BasePage]]) -> None:
        self.put(pages)
        if type(pages) is not list:
            pages = [pages]
        t = time.time()
        speed_status = [0] * 10
        last_parsed = 0
        speed = 0
        while any(not page.parsed for page in pages):
            if time.time() - t >= 1:
                t = time.time()
                parsed = sum(page.parsed for page in pages)
                speed_status.pop(0)
                speed_status.append(parsed - last_parsed)
                last_parsed = parsed
                speed = sum(speed_status) / len(speed_status)
            self._print_status(pages, f'{round(speed, 1)} p/s')
            time.sleep(0.1)
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
