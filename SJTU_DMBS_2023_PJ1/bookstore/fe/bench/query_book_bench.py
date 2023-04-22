from fe.bench.workload import Workload
from fe.bench.workload import QueryBookById
import time
import random


class QueryBookBench:
    def __init__(self, wl: Workload):
        self.workload = wl
        self.time_query_book = 0

    def run_order_book_bench(self, query_num: int):
        for _ in range(query_num):
            book_ind = random.randint(1, len(self.workload.book_ids))
            book_id = self.workload.book_ids[book_ind - 1]

            # one book, searching by book_id
            query = QueryBookById(book_id)
            before = time.time()
            ok = query.run()
            after = time.time()
            self.time_query_book = self.time_query_book + after - before
            assert ok
